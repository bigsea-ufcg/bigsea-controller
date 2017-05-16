from service.api.actuator.actuator import Actuator

class Nop_Actuator(Actuator):

    def prepare_environment(self, vm_data):
        pass

    def adjust_resources(self, vm_data):
        pass

    def get_allocated_resources(self, vm_id):
        return 100