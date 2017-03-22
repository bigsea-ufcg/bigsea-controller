from service.api.actuator.basic_actuator import Basic_Actuator

class Actuator_Builder(object):
    
    def get_actuator(self, name):
        if name == "basic":
            return Basic_Actuator()
        else:
            raise Exception("Unknown actuator type")