from service.api.controller.basic_controller import Basic_Controller
import ConfigParser


class Controller_Builder:

    def __init__(self):
        pass

    def get_controller(self, name):
        if name == "basic":
            config = ConfigParser.RawConfigParser()
            config.read("controller.cfg")
            return Basic_Controller(config)
        else:
            raise Exception("Unknown controller type")
