from abc import abstractmethod
from abc import ABCMeta


class Metric_Source:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_most_recent_value(self, metric_name, options):
        pass
