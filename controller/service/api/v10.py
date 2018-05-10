# Copyright (c) 2017 UFCG-LSD.
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

from flask import request
from controller.plugins.actuator.builder import ActuatorBuilder
from controller.plugins.controller.builder import ControllerBuilder
from controller.utils.logger import Log


API_LOG = Log("APIv10", "APIv10.log")

scaled_apps = {}

controller_builder = ControllerBuilder()
actuator_builder = ActuatorBuilder()


def setup_environment(data):
    data = request.json

    plugin = data["actuator"]
    actuator = actuator_builder.get_actuator(plugin, data)

    API_LOG.log("%s-Preparing environment for instances %s" %
	       (time.strftime("%H:%M:%S"), str(data)))

    try:
	actuator.adjust_resources(data['instances_cap'])
    except Exception as e:
	API_LOG.log(str(e))

    return "prepared_environment"


def start_scaling(app_id, data):
    API_LOG.log("Adding application id: %s" % (app_id))

    plugin = data["scaler_plugin"]
    controller = controller_builder.get_controller(plugin, app_id, data)
    executor = threading.Thread(
                            target=controller.start_application_scaling)

    executor.start()
    scaled_apps[app_id] = controller


def stop_scaling(app_id):
    if app_id in scaled_apps:
        API_LOG.log("Removing application id: %s" % (app_id))

        executor = scaled_apps[app_id]
        executor.stop_application_scaling()
        scaled_apps.pop(app_id)

    else:
        API_LOG.log("Application %s not found" % (app_id))


def controller_status():
    status = "Status: OK\n"
    status += "Monitoring applications:\n"
    for app_id in scaled_apps:
        status += app_id + "\n"
        status += "Last action:" + scaled_apps[app_id].status()
        status += "\n"

    return status