from abc import abstractmethod
from abc import ABCMeta

class Actuator:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def prepare_environment(self, vm_data):
        pass
