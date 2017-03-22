from abc import abstractmethod
from abc import ABCMeta

class Controller:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def start_application_scaling(self, app_id, parameters):
        pass
    
    @abstractmethod
    def stop_application_scaling(self, app_id):
        pass
