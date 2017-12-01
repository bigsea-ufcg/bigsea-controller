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
import datetime
import time

class Fuzzy_Alarm:
    
    ERROR_METRIC_NAME = "application-progress.error"
    
    def __init__(self, actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap, 
                 metric_rounding, heuristic_options, application_id, instances):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.metric_rounding = metric_rounding
        self.heuristic_options = heuristic_options
        self.application_id = application_id
        self.instances = instances
        
        self.logger = ScalingLog("%s.fuzzy.controller.log" % (application_id), "controller.log", 
                                                                          application_id)
        self.cap_logger = ScalingLog("%s.cap.log" % (application_id), "cap.log", application_id)
        
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
        self.logger.log("Getting progress error")
        # Get the progress error value and timestamp
        progress_error_timestamp, progress_error = self._get_progress_error(self.application_id)
            
        self.logger.log("Progress error-[%s]-%f" % (str(progress_error_timestamp), progress_error))
        self.last_action = "Progress error-[%s]-%f" % (str(progress_error_timestamp), progress_error)

        # Check if the metric is new by comparing the timestamps of the current metric and most recent metric
        if self._check_measurements_are_new(progress_error_timestamp):
            self._scale(progress_error/100, self.instances)

            if self.cap != -1:
                self.cap_logger.log("%.0f|%s|%s" % (time.time(), str(self.application_id), str(self.cap)))

        else:
            self.logger.log("Could not acquire more recent metrics")
#         except Exception as e:
#             # TODO: Check exception type
#             self.logger.log(str(e))
#             return

    def _scale(self, diff, instances):
        self.logger.log("Setting cap...")
        current_cap = self.actuator.get_allocated_resources_to_cluster(instances)
        self.logger.log("Current CAP: %s" % current_cap)
        category = self._defuzzification(diff)
        new_cap = Fuzzy_Alarm._decide_next_cap(category)
        self.logger.log("New CAP: %s" % new_cap)

        if new_cap != current_cap:
            self.logger.log("Scaling from %d to %d" % (current_cap, new_cap))
            cap_instances = {instance: new_cap for instance in instances}
            self.actuator.adjust_resources(cap_instances)
            self.cap = new_cap
            # change resources
            pass

        pass

    def _get_progress_error(self, application_id):
        progress_error_measurement = self.metric_source.get_most_recent_value(Fuzzy_Alarm.ERROR_METRIC_NAME,
                                                                {"application_id":application_id})
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        progress_error = round(progress_error, self.metric_rounding)
        return progress_error_timestamp, progress_error

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp

    def status(self):
        return self.last_action

    @staticmethod
    def _very_late(diff):
        if diff > -0.2:
            level = 0
        elif diff < -1:
            level = 1
        else:
            level = -(5.0 / 3) * diff - (1 / 3.0)

        return float("%.2f" % level)

    @staticmethod
    def _very_advanced(diff):
        if diff < 0.2:
            level = 0
        elif diff > 1:
            level = 1
        else:
            level = (5.0 / 3) * diff - (1 / 3.0)

        return float("%.2f" % level)

    @staticmethod
    def _low_late(diff):
        if diff >= 0 or diff <= -0.4:
            level = 0
        elif -0.4 <= diff <= -0.2:
            level = (5 * diff) + 2
        elif -0.2 < diff < 0:
            level = -5 * diff

        return float("%.2f" % level)

    @staticmethod
    def _low_advanced(diff):
        if diff <= 0 or diff >= 0.4:
            level = 0
        elif 0.4 >= diff >= 0.2:
            level = (-5 * diff) + 2
        elif 0.2 > diff > 0:
            level = 5 * diff

        return float("%.2f" % level)

    def _defuzzification(self, diff):
        results = []
        self.logger.log("Diff: %s" % diff)
        results.append(("VA", Fuzzy_Alarm._very_advanced(diff)))
        results.append(("LA", Fuzzy_Alarm._low_advanced(diff)))
        results.append(("VL", Fuzzy_Alarm._very_late(diff)))
        results.append(("LL", Fuzzy_Alarm._low_late(diff)))

        results = sorted(results, key=lambda x: x[1])
        self.logger.log("Fuzzy Category: %s | Ellected with pertinence level %s" % (results[3][0], results[3][1]))
        return results[3][0]

    @staticmethod
    def _decide_next_cap(category):
        if "VL"== category:
            cap = 100
        elif "LL" == category:
            cap = 70
        elif "LA" == category:
            cap = 40
        elif "VA" == category:
            cap = 10

        return cap

