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
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.actuator.plugins.instance_locator import Instance_Locator
from utils.ssh_utils import SSH_Utils
from service.api.actuator.plugins.remote_kvm import Remote_KVM
from service.api.actuator.plugins.kvm_actuator import KVM_Actuator
from service.api.controller.plugins.proportional_derivative.alarm import (
    ProportionalDerivativeAlarm
)
from mock.mock import MagicMock
import datetime


class TestProportionalDerivativeAlarm(unittest.TestCase):

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

        self.timestamps = [self.timestamp_1, self.timestamp_2,
                           self.timestamp_3, self.timestamp_4]

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"
        self.instances = [self.instance_name_1, self.instance_name_2]

        self.trigger_down = 10.0
        self.trigger_up = 10.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.actuation_size = 10.0
        self.allocated_resources_scale_down = 100
        self.allocated_resources_scale_up = 10
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
        self.instance_locator = Instance_Locator(
            SSH_Utils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_key)
        self.actuator = KVM_Actuator(self.instance_locator, self.remote_kvm, self.authorization_data,
                                     self.default_io_cap)

        self.proportional_factor = 1.5
        self.derivative_factor = 0.5

        self.heuristic_options = {"heuristic_name": "error_proportional_derivative",
                                  "proportional_factor": self.proportional_factor,
                                  "derivative_factor": self.derivative_factor}

        self.progress_error = {
            # CASE 1
            self.application_id_0: {self.timestamp_1: -30.0, self.timestamp_2: -20.0,
                                    self.timestamp_3: -15.0},

            # CASE 2
            self.application_id_1: {self.timestamp_1: -30.0, self.timestamp_2: -40.0,
                                    self.timestamp_3: -60.0},

            # CASE 3
            self.application_id_2: {self.timestamp_1: 30.0, self.timestamp_2: 20.0,
                                    self.timestamp_3: 15.0},

            # CASE 4
            self.application_id_3: {self.timestamp_1: 30.0, self.timestamp_2: 40.0,
                                    self.timestamp_3: 55.0},

            # CASE 5
            self.application_id_4: {self.timestamp_1: 100.0, self.timestamp_2: 100.0,
                                    self.timestamp_3: 100.0},

            # CASE 6
            self.application_id_5: {self.timestamp_1: -100.0, self.timestamp_2: -100.0,
                                    self.timestamp_3: -100.0},

            # CASE 7
            self.application_id_6: {self.timestamp_1: -30.0, self.timestamp_2: 10.0,
                                    self.timestamp_3: 30.0},

            # CASE 8
            self.application_id_7: {self.timestamp_1: -5.0, self.timestamp_2: -1.0,
                                    self.timestamp_3: 2.0}}

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        timestamp_to_use = self.timestamps.pop(0)

        if metric_name == ProportionalDerivativeAlarm.ERROR_METRIC_NAME:
            return timestamp_to_use, self.progress_error[application_id][timestamp_to_use]

    '''

        CASE 1
        The error is always negative and its absolute value decreases throughout the execution
        The derivative component decreases the proportional effect
        Uses application_id_0 progress

    '''

    def test_alarm_gets_metrics_and_scales_up_decreasing_error(self):
        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_0, self.instances)

        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 30
        # Derivative effect = -5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 25

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = 22.5
        # Derivative effect = -2.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 20

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 2

       The error is always negative and its absolute value increases throughout the execution
       The derivative component increases the proportional effect
       Uses application_id_1 progress

    '''

    def test_alarm_gets_metrics_and_scales_up_increasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_1, self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 60
        # Derivative effect = 5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 65

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = 90
        # Derivative effect = 10
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 90

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 3

       The error is always positive and its absolute value decreases throughout the execution
       The derivative component decreases the proportional effect
       Uses application_id_2 progress

    '''

    def test_alarm_gets_metrics_and_scales_down_decreasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = -45
        # Derivative effect = 0
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_2, self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -30
        # Derivative effect = 5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 25

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -22.5
        # Derivative effect = 2.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 20

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 4

       The error is always positive and its absolute value increases throughout the execution
       The derivative component increases the proportional effect
       Uses application_id_3 progress

    '''

    def test_alarm_gets_metrics_and_scales_down_increasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = -45
        # Derivative effect = 0
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_3, self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -60
        # Derivative effect = -5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 65

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -82.5
        # Derivative effect = -7.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 90

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 5

       The error value is set to force the use of the minimum possible cap value
       Uses application_id_4 progress

    '''

    def test_alarm_scale_down_limits(self):
        #
        # First call - there is no derivative effect - timestamp_1
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_4, self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_4})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.min_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_4})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.min_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 6

       The error value is set to force the use of the maximum possible cap value
       Uses application_id_5 progress

    '''

    def test_alarm_scale_up_limits(self):
        #
        # First call - there is no derivative effect - timestamp_1
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 self.trigger_down, self.trigger_up, self.min_cap,
                                                 self.max_cap, self.metric_round, self.heuristic_options,
                                                 self.application_id_5, self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_5})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.max_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_5})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.max_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 7

       The error is negative in the first call and positive in the following calls.
       Uses application_id_6 progress

    '''

    def test_alarm_negative_to_positive_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 0, 0, self.min_cap, self.max_cap, self.metric_round,
                                                 self.heuristic_options, self.application_id_6, self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -15
        # Derivative effect = -20
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 35

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -45
        # Derivative effect = -10
        #

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 55

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

    '''

       CASE 8

       The error is negative in the two first calls and positive in the following calls.
       Uses application_id_7 progress

    '''

    def test_alarm_smoothly_negative_to_positive_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 7.5
        # Derivative effect = 0
        #

        self.alarm = ProportionalDerivativeAlarm(self.actuator, self.metric_source,
                                                 0, 0, self.min_cap, self.max_cap, self.metric_round,
                                                 self.heuristic_options, self.application_id_7, self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_up + 7.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 1.5
        # Derivative effect = -2.0
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 0.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -3.0
        # Derivative effect = -1.5
        #

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalDerivativeAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_called_once_with(
            self.instances)

        new_cap = self.allocated_resources_scale_down - 4.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1: new_cap,
                                                                self.instance_name_2: new_cap})


if __name__ == "__main__":
    unittest.main()
