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

from utils.logger import ScalingLog
from utils.logger import TableLog, configure_logging
from utils.monasca import MonascaMonitor
import datetime
import time

# This class contains the logic used to adjust the amount of resources allocated to applications


class Generic_Alarm:

    ERROR_METRIC_NAME = "application-progress.error"
    JOB_PROGRESS_METRIC_NAME = "application-progress.job_progress"
    TIME_PROGRESS_METRIC_NAME = "application-progress.ref_value"
    CURRENT_CAP_METRIC_NAME = "application-progress.current_cap"
    PREVIOUS_CAP_METRIC_NAME = "application-progress.previous_cap"

    def __init__(self, actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap,
                 actuation_size, metric_rounding, application_id, instances):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.actuation_size = actuation_size
        self.metric_rounding = metric_rounding
        self.application_id = application_id
        self.instances = instances
        self.monasca = MonascaMonitor()
        self.dimensions = {'application_id': self.application_id,
                           'service': 'spark-sahara'}

        self.logger = ScalingLog("%s.generic.alarm.log" % (application_id), "controller.log",
                                 application_id)

        self.cap_logger = ScalingLog("%s.cap.log" % (
            application_id), "cap.log", application_id)

        self.table_logger = TableLog("%s.generic.alarm.table.log" % (application_id), "controller.table.log")

        self.last_progress_error_timestamp = datetime.datetime.strptime("0001-01-01T00:00:00.0Z",
                                                                        '%Y-%m-%dT%H:%M:%S.%fZ')
        self.last_action = ""
        self.cap = -1

    def check_application_state(self):
        """
            Checks the application progress by getting progress metrics from a
            metric source, checks if the metrics are new and tries to modify the
            amount of allocated resources if necessary.
        """

        # TODO: Check parameters
        try:
            action = "Getting metrics"
            job_progress = self._get_job_progress(self.application_id)
            time_progress = self._get_time_progress(self.application_id)
            self.table_logger.log(self.application_id, job_progress, time_progress, self.cap, '--', action)

            self.logger.log("Getting progress error")
            self.last_action = "getting progress error"
            # Get the progress error value and timestamp
            progress_error_timestamp, progress_error = self._get_progress_error(
                self.application_id)

            self.logger.log(
                "Progress error: %.2f" % (progress_error))
            self.last_action = "Progress error: %.2f" % (progress_error)

            # Check if the metric is new by comparing the timestamps of the current metric and most recent metric
            if self._check_measurements_are_new(progress_error_timestamp):
                self._scale_down(progress_error, self.instances)
                self._scale_up(progress_error, self.instances)

                if self.cap != -1:
                    self.cap_logger.log("%.0f|%s|%s" % (time.time(),
                                                        str(self.application_id), str(self.cap)))

                self.last_progress_error_timestamp = progress_error_timestamp
            else:
                self.last_action += " Could not acquire more recent metrics"
                self.logger.log("Could not acquire more recent metrics")
        except Exception as e:
            # TODO: Check exception type
            self.logger.log(str(e))
            return

    def _scale_down(self, progress_error, instances):
        """
            Checks if it is necessary to scale down, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """

        # If the error is positive and its absolute value is too high, scale down
        if progress_error > 0 and progress_error >= self.trigger_down:
            self.logger.log("Scaling down")
            self.last_action = "Getting allocated resources"

            # Get current CPU cap
            cap = self.actuator.get_allocated_resources_to_cluster(instances)
            new_cap = max(cap - self.actuation_size, self.min_cap)

            self.logger.log("Scaling from %d to %d" % (cap, new_cap))
            self.last_action = "Scaling from %d to %d" % (cap, new_cap)

            action = "Scaling down"
            job_progress = self._get_job_progress(self.application_id)
            time_progress = self._get_time_progress(self.application_id)
            self.table_logger.log(self.application_id, job_progress, time_progress, cap, new_cap, action)

            previous_cap = {}
            previous_cap['name'] = ('application-progress.previous_cap')
            previous_cap['value'] = cap
            previous_cap['timestamp'] = time.time() * 1000
            previous_cap['dimensions'] = self.dimensions
            self.monasca.send_metrics([previous_cap])

            current_cap = {}
            previous_cap['name'] = ('application-progress.current_cap')
            previous_cap['value'] = new_cap
            previous_cap['timestamp'] = time.time() * 1000
            previous_cap['dimensions'] = self.dimensions
            self.monasca.send_metrics([current_cap])

            # Currently, we use the same cap for all the vms
            cap_instances = {instance: new_cap for instance in instances}

            # Set the new cap
            self.actuator.adjust_resources(cap_instances)

            self.cap = new_cap

    def _scale_up(self, progress_error, instances):
        """
            Checks if it is necessary to scale up, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """

        # If the error is negative and its absolute value is too high, scale up
        if progress_error < 0 and abs(progress_error) >= self.trigger_up:
            self.logger.log("Scaling up")
            self.last_action = "Getting allocated resources"

            # Get current CPU cap
            cap = self.actuator.get_allocated_resources_to_cluster(instances)
            new_cap = min(cap + self.actuation_size, self.max_cap)

            self.logger.log("Scaling from %d to %d" % (cap, new_cap))
            self.last_action = "Scaling from %d to %d" % (cap, new_cap)

            action = "Scaling up"
            job_progress = self._get_job_progress(self.application_id)
            time_progress = self._get_time_progress(self.application_id)
            self.table_logger.log(self.application_id, job_progress, time_progress, cap, new_cap, action)

            # Currently, we use the same cap for all the vms
            cap_instances = {instance: new_cap for instance in instances}

            # Set the new cap
            self.actuator.adjust_resources(cap_instances)

            self.cap = new_cap

    def _get_progress_error(self, application_id):
        progress_error_measurement = self.metric_source.get_most_recent_value(Generic_Alarm.ERROR_METRIC_NAME,
                                                                              {"application_id": application_id})
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        progress_error = round(progress_error, self.metric_rounding)
        return progress_error_timestamp, progress_error

    def _get_job_progress(self, application_id):
        job_progress_measurement = self.metric_source.get_most_recent_value(Generic_Alarm.JOB_PROGRESS_METRIC_NAME,
                                                                            {"application_id": application_id})
        job_progress_timestamp = job_progress_measurement[0]
        job_progress = job_progress_measurement[1]
        return job_progress

    def _get_time_progress(self, application_id):
        time_progress_measurement = self.metric_source.get_most_recent_value(Generic_Alarm.TIME_PROGRESS_METRIC_NAME,
                                                                            {"application_id": application_id})
        time_progress_timestamp = time_progress_measurement[0]
        time_progress = time_progress_measurement[1]
        return time_progress

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp

    def status(self):
        return self.last_action
