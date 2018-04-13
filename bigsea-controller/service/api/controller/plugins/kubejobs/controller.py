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

import threading
import time

from service.api.actuator.actuator_builder import Actuator_Builder
from service.api.controller.controller import Controller
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.controller.plugins.kubejobs.alarm import KubeJobs
from utils.logger import ScalingLog

# This class dictates the pace of the scaling process. It controls when Generic_Alarm
# is called to check application state and when is necessary to wait.


class Kubejobs_Controller(Controller):

    def __init__(self, application_id, parameters):
        self.logger = ScalingLog(
            "diff.controller.log", "controller.log", application_id)

        scaling_parameters = parameters["scaling_parameters"]

        self.application_id = application_id
        # read scaling parameters
        self.check_interval = scaling_parameters["check_interval"]
        self.trigger_down = scaling_parameters["trigger_down"]
        self.trigger_up = scaling_parameters["trigger_up"]
        self.min_cap = scaling_parameters["min_cap"]
        self.max_cap = scaling_parameters["max_cap"]
        self.actuation_size = scaling_parameters["actuation_size"]
        # The actuator plugin name
        self.actuator_type = scaling_parameters["actuator"]
        # The metric source plugin name
        self.metric_source_type = scaling_parameters["metric_source"]

        # We use a lock here to prevent race conditions when stopping the controller
        self.running = True
        self.running_lock = threading.RLock()

        # Gets a new metric source plugin using the given name
        metric_source = Metric_Source_Builder().get_metric_source(
            self.metric_source_type, parameters)
        # Gets a new actuator plugin using the given name
        actuator = Actuator_Builder().get_actuator(self.actuator_type, parameters)
        # The alarm here is responsible for deciding whether to scale up or down, or even do nothing
        self.alarm = KubeJobs(actuator, metric_source, self.trigger_down, self.trigger_up,
                              self.min_cap, self.max_cap, self.actuation_size,
                              application_id)

    def start_application_scaling(self):
        run = True

        while run:
            self.logger.log("Monitoring application: %s" %
                            self.application_id)

            # Call the alarm to check the application
            self.alarm.check_application_state()

            # Wait some time
            time.sleep(float(self.check_interval))

            with self.running_lock:
                run = self.running

    def stop_application_scaling(self):
        with self.running_lock:
            self.running = False

    def status(self):
        return self.alarm.status()
