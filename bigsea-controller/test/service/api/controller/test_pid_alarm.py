# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import datetime
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.actuator.plugins.instance_locator import Instance_Locator
from utils.ssh_utils import SSH_Utils
from service.api.actuator.plugins.remote_kvm import Remote_KVM
from service.api.actuator.plugins.kvm_actuator import KVM_Actuator
from service.api.controller.plugins.pid.pid_alarm import PIDAlarm
from mock import MagicMock


class TestPIDAlarm(unittest.TestCase):


    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"
        self.application_id_3 = "app-03"
        self.application_id_4 = "app-04"
        self.application_id_5 = "app-05"
        self.application_id_6 = "app-06"
        self.application_id_7 = "app-07"
        
        self.timestamp_1 = datetime.datetime.strptime("2000-01-01T00:00:00.0Z", 
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_2 = datetime.datetime.strptime("2000-01-01T00:05:00.0Z", 
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_3 = datetime.datetime.strptime("2000-01-01T00:10:00.0Z", 
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_4 = datetime.datetime.strptime("2000-01-01T00:15:00.0Z", 
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        
        self.timestamps = [self.timestamp_1, self.timestamp_2, self.timestamp_3, self.timestamp_4]
        
        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"
        self.instances = [self.instance_name_1, self.instance_name_2]

        self.trigger_down = 0.0
        self.trigger_up = 0.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.actuation_size = 10.0
        self.allocated_resources_scale_down = 100
        self.allocated_resources_scale_up = 30
        self.metric_round = 2
        self.default_io_cap = 34

        self.bigsea_username = "username"
        self.bigsea_password = "password"
        self.authorization_url = "authorization_url"
        self.authorization_data = dict(authorization_url=self.authorization_url,
                                  bigsea_username=self.bigsea_username,
                                  bigsea_password=self.bigsea_password)

        compute_nodes = []
        compute_nodes_key = "key"
        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = Metric_Source_Builder().get_metric_source("nop", {})
        self.instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_key)
        self.actuator = KVM_Actuator(self.instance_locator, self.remote_kvm, self.authorization_data,
                                     self.default_io_cap)
        
        self.proportional_factor = 0.0
        self.derivative_factor = 0.0
        self.integrative_factor = 1.5
        
        self.heuristic_options = {"heuristic_name":"error_pid",
                                  "proportional_factor":self.proportional_factor,
                                  "derivative_factor":self.derivative_factor, 
                                  "integrative_factor":self.integrative_factor}
        
        self.progress_error = {
            # CASE 1
            self.application_id_0:{self.timestamp_1:-10.0, self.timestamp_2:-5.0, 
                                   self.timestamp_3:20.0}}

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        timestamp_to_use = self.timestamps.pop(0)

        if metric_name == PIDAlarm.ERROR_METRIC_NAME:
            return timestamp_to_use, self.progress_error[application_id][timestamp_to_use]


    def testPID(self):
        self.alarm = PIDAlarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up, self.min_cap, 
                              self.max_cap, self.metric_round, self.heuristic_options, self.application_id_0, self.instances)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
                        MagicMock(return_value=self.allocated_resources_scale_up)
        
        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
                    assert_any_call(PIDAlarm.ERROR_METRIC_NAME, 
                    {"application_id":self.application_id_0})
                    
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(self.instances)
        
        new_cap = self.allocated_resources_scale_up + 15

        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, 
                                    self.instance_name_2:new_cap})
        
        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
                        MagicMock(return_value=self.allocated_resources_scale_up)
                        
        self.alarm.check_application_state()
        
        self.metric_source.get_most_recent_value.\
                    assert_any_call(PIDAlarm.ERROR_METRIC_NAME, 
                    {"application_id":self.application_id_0})
        
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(self.instances)
        
        new_cap = self.allocated_resources_scale_up + 22.5
        
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, 
                                    self.instance_name_2:new_cap})
        
        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
                        MagicMock(return_value=self.allocated_resources_scale_up)
                        
        self.alarm.check_application_state()
        
        self.metric_source.get_most_recent_value.\
                    assert_any_call(PIDAlarm.ERROR_METRIC_NAME, 
                    {"application_id":self.application_id_0})
        
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(self.instances)

        new_cap = self.allocated_resources_scale_up - 7.5
        
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, 
                                    self.instance_name_2:new_cap})

if __name__ == "__main__":
    unittest.main()