from abc import ABCMeta
from abc import abstractmethod

class Controller:
    __metaclass__ = ABCMeta

    '''
        Creates a Controller instance. 
        
        app_id is the id of the application associated with the instance.
        parameters is a dictionary of scaling parameters. 
    '''
    @abstractmethod
    def __init__(self, app_id, parameters):
        pass

    '''
        Starts scaling for the application associated 
        with the controller instance. The method is not expected
        to return until the scaling is stopped through the 
        stop_application_scaling. Normally, this method is used
        as a run method by a thread.
    '''
    @abstractmethod
    def start_application_scaling(self):
        pass

    '''
        Stops scaling for the application associated 
        with the controller instance. This method's expected
        side effect is to make start_application_scaling to return
    '''
    @abstractmethod
    def stop_application_scaling(self):
        pass
    
    @abstractmethod
    def status(self):
        pass