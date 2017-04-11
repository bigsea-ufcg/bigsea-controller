import ConfigParser

from service.api.controller.plugins.basic_controller import Basic_Controller
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.actuator.actuator_builder import Actuator_Builder
from service.api.controller.plugins.single_application_controller import Single_Application_Controller

class Controller_Builder:

    def __init__(self):
        pass

    def get_controller(self, name, application_id, parameters):
        if name == "basic":
            config = ConfigParser.RawConfigParser()
            config.read("controller.cfg")
            
            # Read scaling policy
            metric_source_type = config.get("policy", "metric_source")
            actuator_type = config.get("policy", "actuator")
                        
            # Read configuration
            check_interval = config.getfloat("scaling", "check_interval")
            trigger_down = config.getfloat("scaling", "trigger_down")
            trigger_up = config.getfloat("scaling", "trigger_up")
            min_cap = config.getfloat("scaling", "min_cap")
            max_cap = config.getfloat("scaling", "max_cap")
            actuation_size = config.getfloat("scaling", "actuation_size")
            metric_rounding = config.getint("scaling", "metric_rounding")
            
            parameters = {"check_interval":check_interval,"trigger_down":trigger_down,
                          "trigger_up":trigger_up, "min_cap":min_cap, "max_cap":max_cap,
                          "actuation_size":actuation_size, "metric_rounding":metric_rounding}
            
            metric_source = Metric_Source_Builder().get_metric_source(metric_source_type)
            actuator = Actuator_Builder().get_actuator(actuator_type)
            
            return Basic_Controller(metric_source, actuator, parameters)
        elif name == "single":
            return Single_Application_Controller(application_id, parameters)
        else:
            # FIXME: exception type
            raise Exception("Unknown controller type")
