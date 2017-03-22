from service.api.controller.basic_controller import Basic_Controller

class Controller_Builder:

    def __init__(self):
        pass

    def get_controller(self, name):
        if name == "basic":
            return Basic_Controller()
        else:
            raise Exception("Unknown controller type")