from mock.mock import MagicMock
import unittest

from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.remote_kvm import Remote_KVM
from service.api.controller.plugins.basic_alarm import Basic_Alarm
from service.api.controller.metric_source_builder import Metric_Source_Builder
from utils.ssh_utils import SSH_Utils
import datetime


class Test_Basic_Alarm(unittest.TestCase):

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
        self.actuation_size = 10.0
        self.allocated_resources = 50
        self.metric_round = 2

        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = Metric_Source_Builder().get_metric_source("nop")
        self.instance_locator = Instance_Locator(SSH_Utils())
        self.remote_kvm = Remote_KVM(SSH_Utils())
        self.actuator = Basic_Actuator(self.instance_locator, self.remote_kvm)

        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size, self.metric_round)

        self.timestamps = [self.timestamp_1, self.timestamp_2, self.timestamp_3, self.timestamp_4]

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        # normal cases
        # application 0 -> job progress < time progress -> scale up
        # application 1 -> job progress = time progress -> do nothing
        # application 2 -> job progress > time progress -> scale down
        
        # rounding cases
        # application 3 -> job progress < time progress -> scale up depends on rounding
        # application 4 -> job progress > time progress -> scale down depends on rounding

        job_progress = {self.application_id_0:30.0, self.application_id_1:50.0, self.application_id_2:80.0, 
                        self.application_id_3:50.004, self.application_id_4:80.000}
        time_progress = {self.application_id_0:80.0, self.application_id_1:50.0, self.application_id_2:30.0, 
                         self.application_id_3:60.000, self.application_id_4:50.003}

        if metric_name == Basic_Alarm.PROGRESS_METRIC_NAME:
            return self.timestamp_1, job_progress[application_id]
        elif metric_name == Basic_Alarm.ELAPSED_TIME_METRIC_NAME:
            return self.timestamp_1, time_progress[application_id]

    def metrics_different_timestamps(self, metric_name, options):
        application_id = options["application_id"]
        
        job_progress = {self.application_id_0:30.0, self.application_id_1:50.0, self.application_id_2:80.0, 
                        self.application_id_3:50.004, self.application_id_4:80.000}
        time_progress = {self.application_id_0:80.0, self.application_id_1:50.0, self.application_id_2:30.0, 
                         self.application_id_3:60.000, self.application_id_4:50.003}

        timestamp = self.timestamps.pop(0)

        if metric_name == Basic_Alarm.PROGRESS_METRIC_NAME:
            return timestamp, job_progress[application_id]
        elif metric_name == Basic_Alarm.ELAPSED_TIME_METRIC_NAME:
            return timestamp, time_progress[application_id]
    

    def test_alarm_gets_metrics_and_scales_down(self):
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_2})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

    def test_alarm_gets_metrics_and_scales_up(self):
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_0, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_0})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Add resources
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

    def test_alarm_does_nothing(self):
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_1, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_1})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_1})

        # The method doesn't try to get the amount of allocated resources 
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_metric_rounding(self):
        #
        # The metrics are rounded to 2 digits from the decimal point
        # There should be scale up and down in these cases
        #
        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size, 2)
        
        # Scale up
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_3, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_3})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_3})

        # The method tries to get the amount of allocated resources 
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

        # Scale down
        # Set up mocks
        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size, 2)
        
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_4, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_4})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_4})

        # The method tries to get the amount of allocated resources 
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # The metrics are rounded to 3 digits from the decimal point
        # There should not be scale up and down in these cases
        #
        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up, 
                                 self.min_cap, self.max_cap, self.actuation_size, 3)
                
        # Scale up
        # Start up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_3, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_3})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_3})
        
        # The method doesn't try to get the amount of allocated resources 
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()
        
        # Scale down
        # Start up mocks
        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size, 3)
        
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_4, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_4})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_4})
        
        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_does_not_reuse_metrics_with_same_timestamp(self):
        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size, 2)
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_0})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_0})
        
        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Add resources
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # 2nd call. The method checks if the metric is new and does not acts
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)
        
        self.alarm.check_application_state(self.application_id_0, self.instances)
        
        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_0})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_0})
        
        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()
        
    def test_alarm_metrics_with_different_timestamps(self):
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_2})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
        #
        # 2nd call. The method checks if the metric is new and acts
        #
        
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances)

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_2})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
