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

from controller.plugins.actuator.builder import ActuatorBuilder
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.controller.base import Controller
from controller.plugins.controller.generic.alarm import GenericAlarm
from controller.plugins.controller.pid.alarm import PIDAlarm
from controller.exceptions.monasca import MetricNotFoundException

from controller.utils.logger import ScalingLog
import threading
import time


class PIDController(Controller):

    def __init__(self, application_id, parameters):
        self.logger = ScalingLog("pid.controller.log", "controller.log",
                                 application_id)

        scaling_parameters = parameters["scaling_parameters"]

        self.application_id = application_id
        # read scaling parameters
        self.instances = scaling_parameters["instances"]
        self.check_interval = scaling_parameters["check_interval"]
        self.trigger_down = scaling_parameters["trigger_down"]
        self.trigger_up = scaling_parameters["trigger_up"]
        self.min_cap = scaling_parameters["min_cap"]
        self.max_cap = scaling_parameters["max_cap"]
        self.metric_rounding = scaling_parameters["metric_rounding"]
        # The actuator plugin name
        self.actuator_type = scaling_parameters["actuator"]
        # The metric source plugin name
        self.metric_source_type = scaling_parameters["metric_source"]
        self.heuristic_options = scaling_parameters["heuristic_options"]

        # We use a lock here to prevent race conditions when stopping the controller
        self.running = True
        self.running_lock = threading.RLock()

        # Gets a new metric source plugin using the given name
        metric_source = MetricSourceBuilder().get_metric_source(self.metric_source_type, parameters)
        # Gets a new actuator plugin using the given name
        actuator = ActuatorBuilder().get_actuator(self.actuator_type, parameters)
        # The alarm here is responsible for deciding whether to scale up or down, or even do nothing
        self.alarm = PIDAlarm(actuator, metric_source, self.trigger_down,
                              self.trigger_up, self.min_cap, self.max_cap, self.metric_rounding,
                              self.heuristic_options, application_id, self.instances)

    def start_application_scaling(self):
        run = True

        while run:
            self.logger.log("Monitoring application: %s" % (self.application_id))

            # Call the alarm to check the application
            try:
                self.alarm.check_application_state()
            except MetricNotFoundException:
                self.logger.log("No metrics available")
            except Exception as e:
                self.logger.log(str(e))

            # Wait some time
            time.sleep(float(self.check_interval))

            with self.running_lock:
                run = self.running

    def stop_application_scaling(self):
        with self.running_lock:
            self.running = False

    def status(self):
        return self.alarm.status()
