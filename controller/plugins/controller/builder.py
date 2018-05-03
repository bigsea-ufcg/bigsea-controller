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

from controller.plugins.controller.basic.plugin import BasicController
from controller.plugins.controller.generic.plugin import GenericController
from controller.plugins.controller.pid.plugin import PIDController
from controller.plugins.controller.single.plugin import (
    SingleApplicationController
)
from controller.plugins.controller.proportional.plugin import (
    ProportionalController
)
from controller.plugins.controller.tendency.plugin import (
    TendencyAwareProportionalController
)
from controller.plugins.controller.proportional_derivative.plugin import (
    ProportionalDerivativeController
)
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.actuator.builder import ActuatorBuilder


class ControllerBuilder:

    def __init__(self):
        pass

    def get_controller(self, name, application_id, parameters):
        if name == "basic":
            metric_source_type = parameters["policy"]["metric_source"]
            actuator_type = parameters["policy"]["actuator"]

            metric_source = MetricSourceBuilder().get_metric_source(
                                metric_source_type)

            actuator = ActuatorBuilder().get_actuator(actuator_type)

            return BasicController(metric_source, actuator, parameters)

        elif name == "single":
            return SingleApplicationController(application_id, parameters)

        elif name == "progress_error":
            return GenericController(application_id, parameters)

        elif name == "proportional":
            return ProportionalController(application_id, parameters)

        elif name == "proportional_derivative":
            return ProportionalDerivativeController(application_id,
                                                    parameters)

        elif name == "pid":
            return PIDController(application_id, parameters)

        elif name == "progress_tendency":
            return TendencyAwareProportionalController(application_id,
                                                          parameters)

        else:
            # FIXME: exception type
            raise Exception("Unknown controller type")
