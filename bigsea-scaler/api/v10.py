import time

from flask import Flask
from flask import request

from service.api.actuator.actuator_builder import Actuator_Builder
from service.api.controller.main_controller import Main_Controller
from utils.logger import Log
from utils.logger import configure_logging


SETUP_ROUTE="/scaler/setup_env"
START_SCALING_ROUTE = '/scaler/start_scaling/<app_id>'
STOP_SCALING_ROUTE = '/scaler/stop_scaling/<app_id>'
STATUS = '/scaler/status'

app = Flask(__name__)

# Set up logging
logger = Log("scaler.api.logger", "scaler.api.log")
configure_logging()

main_controller = Main_Controller()

# API methods
# TODO: use Telles' code here
@app.route(SETUP_ROUTE, methods = ['POST'])
def prepare_environment():
    data = request.json

    plugin_name = data["plugin"]
    actuator = Actuator_Builder().get_actuator(plugin_name)
    
    logger.log("%s-Preparing environment for instances %s" % (time.strftime("%H:%M:%S"), str(data)))

    data.pop("plugin")
    
    try:
        actuator.prepare_environment(data)
    except Exception as e:
        logger.log(e.getMessage())

    return "prepared_environment"

# TODO: use Telles' code here
@app.route(START_SCALING_ROUTE, methods = ['POST'])
def start_application_scaling(app_id):
    data = request.json
    logger.log("%s-Started scaling for application %s using parameters:%s" % (time.strftime("%H:%M:%S"), app_id, str(data)))

    main_controller.start_application_scaling(app_id, data)

    return "started-scaling"

# TODO: use Telles' code here
@app.route(STOP_SCALING_ROUTE, methods = ['POST'])
def stop_application_scaling(app_id):
    logger.log("%s-Stopped scaling for application %s" % (time.strftime("%H:%M:%S"), app_id))

    main_controller.stop_application_scaling(app_id)

    return "stopped-scaling"

@app.route(STATUS, methods = ['GET'])
def status():
    return main_controller.status()