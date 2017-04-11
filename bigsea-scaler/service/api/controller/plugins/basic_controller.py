import threading
import time

from service.api.controller.plugins.basic_alarm import Basic_Alarm
from service.api.controller.controller import Controller
from utils.logger import Log, configure_logging


# TODO: documentation
class Basic_Controller(Controller):

    def __init__(self, metric_source, actuator, parameters):
        # Set up logging
        self.logger = Log("basic.controller.log", "controller.log")
        configure_logging()
        
        check_interval = parameters["check_interval"]
        trigger_down = parameters["trigger_down"]
        trigger_up = parameters["trigger_up"]
        min_cap = parameters["min_cap"]
        max_cap = parameters["max_cap"]
        actuation_size = parameters["actuation_size"]
        metric_rounding = parameters["metric_rounding"]

        # Start alarm
        self.alarm = Basic_Alarm(actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding)

        # Start up controller thread
        # Create lock to access application list
        self.applications_lock = threading.RLock()
        self.applications = {}
        self.controller = _Basic_Controller_Thread(self.applications, self.applications_lock, self.alarm, check_interval)
        self.controller_thread = threading.Thread(target=self.controller.start)
        self.controller_thread.start()

    def start_application_scaling(self, app_id, parameters):
        self.logger.log("Adding application id: %s" %  (app_id))
        # Acquire lock and add application
        with self.applications_lock:
            self.applications[app_id] = parameters

    def stop_application_scaling(self, app_id):
        #  Acquire lock and remove application
        with self.applications_lock:
            if self.applications.has_key(app_id):
                self.logger.log("Removing application id: %s" % (app_id))
                self.applications.pop(app_id)
            else:
                self.logger.log("Application %s not found" % (app_id))

    def stop_controller(self):
        self.controller.running = False


class _Basic_Controller_Thread():

    def __init__(self, applications, applications_lock, alarm, check_interval):
        self.logger = Log("basic.controller_thread.log", "controller.log")
        configure_logging()

        self.applications = applications
        self.applications_lock = applications_lock
        self.alarm = alarm
        self.check_interval = check_interval
        self.running = True

    def start(self):
        self.logger.log("Starting controller thread")

        while self.running:
            # acquire lock, check applications and wait
            with self.applications_lock:
                self.logger.log("Monitoring applications: %s" % (str(self.applications.keys())))

                applications_ids = self.applications.keys()

                # for each application check state
                for application_id in applications_ids:
                    instances = self.applications[application_id]["instances"]

                    self.logger.log("Checking application:%s|instances:%s" % (application_id, instances))
                    self.alarm.check_application_state(application_id, instances)

            time.sleep(float(self.check_interval))
