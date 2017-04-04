from mock.mock import MagicMock
import unittest

from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.remote_kvm import Remote_KVM
from service.api.controller.basic_alarm import Basic_Alarm
from service.api.controller.monasca_metric_source import Monasca_Metric_Source
from utils.ssh_utils import SSH_Utils


class Test_Basic_Alarm(unittest.TestCase):

    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"

        self.alarm = None
        self.trigger_down = 30
        self.trigger_up = 10
        self.min_cap = 10
        self.max_cap = 100
        self.actuation_size = 10
        self.expected_time = 100
        self.allocated_resources = 50

        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = Monasca_Metric_Source()
        self.instance_locator = Instance_Locator()
        self.remote_kvm = Remote_KVM(SSH_Utils())
        self.actuator = Basic_Actuator(self.instance_locator, self.remote_kvm)

        self.alarm = Basic_Alarm(self.actuator, self.metric_source, self.trigger_down, self.trigger_up,
                                 self.min_cap, self.max_cap, self.actuation_size)

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        job_progress = {self.application_id_0:30, self.application_id_1:50, self.application_id_2:80}
        time_progress = {self.application_id_0:80, self.application_id_1:50, self.application_id_2:30}

        if metric_name == Basic_Alarm.PROGRESS_METRIC_NAME:
            return job_progress[application_id]
        elif metric_name == Basic_Alarm.ELAPSED_TIME_METRIC_NAME:
            return time_progress[application_id]

    def test_alarm_gets_metrics_and_scales_down(self):
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_2, self.instances, self.expected_time)

        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_2})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_2})

        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        new_cap = self.allocated_resources - self.actuation_size
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

    def test_alarm_gets_metrics_and_scales_up(self):
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_0, self.instances, self.expected_time)

        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_0})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_0})

        self.actuator.get_allocated_resources.assert_called_once_with(self.instance_name_1)
        new_cap = self.allocated_resources + self.actuation_size
        self.actuator.adjust_resources.assert_called_once_with({self.instance_name_1:new_cap, self.instance_name_2:new_cap})

    def test_alarm_does_nothing(self):
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources = MagicMock(return_value=self.allocated_resources)

        self.alarm.check_application_state(self.application_id_1, self.instances, self.expected_time)

        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.PROGRESS_METRIC_NAME, {"application_id":self.application_id_1})
        self.metric_source.get_most_recent_value.assert_any_call(Basic_Alarm.ELAPSED_TIME_METRIC_NAME, {"application_id":self.application_id_1})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
