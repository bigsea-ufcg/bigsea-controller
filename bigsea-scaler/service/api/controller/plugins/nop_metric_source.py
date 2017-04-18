import datetime

class Nop_Metric_Source:

    def get_most_recent_value(self, metric_name, options):
        return datetime.datetime.strptime("0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ'), 0
    