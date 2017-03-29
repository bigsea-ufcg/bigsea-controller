from service.api.controller.metric_source import Metric_Source
from service.api.controller.monasca_monitor import Monasca_Monitor


class Monasca_Metric_Source(Metric_Source):
    def __init__(self):
        self.monasca = Monasca_Monitor()

    def get_most_recent_value(self, metric_name, options):
        return self.monasca.last_measurement(metric_name, {"application_id":options["application_id"], "service":"spark-sahara"})
