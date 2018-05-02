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
import pdb; pdb.set_trace()


def setup_environment(data):
    data = request.json

    plugin_name = data["actuator"]
    actuator = Actuator_Builder().get_actuator(plugin_name, data)

    logger.log("%s-Preparing environment for instances %s" %
	       (time.strftime("%H:%M:%S"), str(data)))

    try:
	actuator.adjust_resources(data['instances_cap'])
    except Exception as e:
	logger.log(str(e))

    return "prepared_environment"


def start_scaling(data, app_id):
    return "ok"


def stop_scaling(app_id):
    return "ok"
