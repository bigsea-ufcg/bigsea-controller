from service.api.controller.plugins.monasca_metric_source import Monasca_Metric_Source
from service.api.controller.plugins.nop_metric_source import Nop_Metric_Source

class Metric_Source_Builder:

    def get_metric_source(self, name):
        if name == "monasca":
            return Monasca_Metric_Source()
        elif name == "nop":
            return Nop_Metric_Source()
        else:
            # FIXME: exception type
            raise Exception("Unknown metric source type")