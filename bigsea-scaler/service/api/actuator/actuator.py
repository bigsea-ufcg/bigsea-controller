from abc import abstractmethod
from abc import ABCMeta

# TODO: documentation
class Actuator:
    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare_environment(self, vm_data):
        pass

    @abstractmethod
    def adjust_resources(self, vm_data):
        pass

    @abstractmethod
    def get_allocated_resources(self, vm_id):
        pass
