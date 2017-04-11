from service.api.controller.controller_builder import Controller_Builder
import threading
from utils.logger import Log, configure_logging

class Main_Controller:

    def __init__(self):
        self.logger = Log("main.controller.log", "controller.log")
        configure_logging()
        
        self.controller_thread_pool = {}
        self.controller_builder = Controller_Builder()
        
    def start_application_scaling(self, application_id, parameters):
        self.logger.log("Adding application id: %s" %  (application_id))
        plugin_name = parameters["plugin"]
        controller = self.controller_builder.get_controller(plugin_name, application_id, parameters)
        controller_thread = threading.Thread(target=controller.start)
        controller_thread.start()
        
        self.controller_thread_pool[application_id] = controller
        
    def stop_application_scaling(self, app_id):
        if self.controller_thread_pool.has_key(app_id):
            self.logger.log("Removing application id: %s" % (app_id))
            app_controller = self.controller_thread_pool[app_id]
            app_controller.stop()
            self.controller_thread_pool.pop(app_id)
        else:
            self.logger.log("Application %s not found" % (app_id))
    