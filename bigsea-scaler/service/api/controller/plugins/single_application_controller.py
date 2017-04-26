import threading
import time

from service.api.actuator.actuator_builder import Actuator_Builder
from service.api.controller.controller import Controller
from service.api.controller.metric_source_builder import Metric_Source_Builder
from service.api.controller.plugins.basic_alarm import Basic_Alarm
from utils.logger import Log, configure_logging


class Single_Application_Controller(Controller):

    def __init__(self, application_id, parameters):
        self.logger = Log("single.controller.log", "controller.log")
        configure_logging()
        
        self.application_id = application_id
        self.instances = parameters["instances"]
        self.check_interval = parameters["check_interval"]
        self.trigger_down = parameters["trigger_down"]
        self.trigger_up = parameters["trigger_up"]
        self.min_cap = parameters["min_cap"]
        self.max_cap = parameters["max_cap"]
        self.actuation_size = parameters["actuation_size"]
        self.metric_rounding = parameters["metric_rounding"]
        self.actuator_type = parameters["actuator"]
        self.metric_source_type = parameters["metric_source"]
        
        self.running = True
        self.running_lock = threading.RLock()
        
        metric_source = Metric_Source_Builder().get_metric_source(self.metric_source_type)
        actuator = Actuator_Builder().get_actuator(self.actuator_type)
        self.alarm = Basic_Alarm(actuator, metric_source, self.trigger_down, self.trigger_up, 
                                 self.min_cap, self.max_cap, self.actuation_size, self.metric_rounding)
    
    def start_application_scaling(self):
    #def start(self):
        run = True
        
        while run:
            self.logger.log("Monitoring application: %s" % (self.application_id))

            self.alarm.check_application_state(self.application_id, self.instances)

            time.sleep(float(self.check_interval))
                
            with self.running_lock:
                run = self.running
            
    def stop_application_scaling(self):
    #def stop(self):
        with self.running_lock:
            self.running = False
        
