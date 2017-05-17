import datetime
import unittest

from mock.mock import MagicMock
from service.api.actuator.plugins.instance_locator import Instance_Locator
from service.api.actuator.plugins.kvm_actuator import KVM_Actuator
from service.api.actuator.plugins.remote_kvm import Remote_KVM
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.controller.plugins.tendency.tendency_aware_proportional_alarm import Tendency_Aware_Proportional_Alarm
from utils.ssh_utils import SSH_Utils

class Test_Proportional_Alarm(unittest.TestCase):


    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"
        self.application_id_3 = "app-03"
        self.application_id_4 = "app-04"

        self.timestamp_1 = datetime.datetime.strptime("2000-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_2 = datetime.datetime.strptime("2000-01-01T00:05:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_3 = datetime.datetime.strptime("2000-01-01T00:10:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_4 = datetime.datetime.strptime("2000-01-01T00:15:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"

        self.trigger_down = 30.0
        self.trigger_up = 10.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.allocated_resources = 50
        self.metric_round = 2

        compute_nodes = []
        compute_nodes_key = "key"
        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = Metric_Source_Builder().get_metric_source("nop", {})
        self.instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_key)
        self.actuator = KVM_Actuator(self.instance_locator, self.remote_kvm)

        self.alarm = Tendency_Aware_Proportional_Alarm(self.actuator, self.metric_source, 
                                        self.trigger_down, self.trigger_up, 
                                        self.min_cap, self.max_cap, 
                                        self.metric_round)
        
        self.timestamps = [self.timestamp_1, self.timestamp_2, self.timestamp_3, self.timestamp_4]
        self.diff_values = {self.application_id_0:[10.0,10.0],
                  self.application_id_1:[10.0,-5.0],
                  self.application_id_2:[0.0,15.0]} 
    
    def metric_values(self, metric_name, options):
        application_id = options["application_id"]
        timestamp = self.timestamps.pop(0)
        return timestamp, self.diff_values[application_id].pop(0)

    def tearDown(self):
        pass

    def test_alarm_base_case(self):
        # Base case
        # diff is null
        # difference is null
        # Do nothing
        
        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = None)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_0})
        self.actuator.get_allocated_resources.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()
        
        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = None)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_0})
        self.actuator.get_allocated_resources.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()
    
    def test_case1(self):
        # Case 1
        # progress is ok. application performance is worse. add more resources. how much?
        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = None)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_1, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_1})
        self.actuator.get_allocated_resources.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()
        
        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = self.allocated_resources)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_1, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_1})
        
        self.actuator.get_allocated_resources.assert_any_call(self.instance_name_1)
        
        new_cap = self.allocated_resources + 15
        self.actuator.adjust_resources.assert_any_call({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
    def test_case2(self):
        # Case 2
        # progress is ok. application performance is improving. remove resources. how much?
        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = None)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_2, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_2})
        self.actuator.get_allocated_resources.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()
        
        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metric_values
        self.actuator.get_allocated_resources = MagicMock(return_value = self.allocated_resources)
        self.actuator.adjust_resources = MagicMock(return_value = None)
        
        self.alarm.check_application_state(self.application_id_2, self.instances)
        
        self.metric_source.get_most_recent_value.assert_any_call(self.alarm.ERROR_METRIC_NAME, 
                                                                 {"application_id": self.application_id_2})
        
        self.actuator.get_allocated_resources.assert_any_call(self.instance_name_1)
        
        new_cap = self.allocated_resources - 15
        self.actuator.adjust_resources.assert_any_call({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()