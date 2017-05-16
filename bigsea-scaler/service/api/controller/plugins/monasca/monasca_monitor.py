import monascaclient.exc as exc
import ConfigParser

from monascaclient import client as monclient, ksclient


class Monasca_Monitor:

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('scaler.cfg')

        self.monasca_username = config.get('monasca', 'username')
        self.monasca_password = config.get('monasca', 'password')
        self.monasca_auth_url = config.get('monasca', 'auth_url')
        self.monasca_project_name = config.get('monasca', 'project_name')
        self.monasca_api_version = config.get('monasca', 'api_version')

        self._get_monasca_client()

    def get_measurements(self, metric_name, dimensions, start_time='2014-01-01T00:00:00Z'):
        measurements = []
        try:
            monasca_client = self._get_monasca_client()
            measurements = monasca_client.metrics.list_measurements(
                name=metric_name, dimensions=dimensions,
                start_time=start_time, debug=False)
        except exc.HTTPException as httpex:
            print httpex.message
        except Exception as ex:
            print ex.message
        if len(measurements) > 0:
            return measurements[0]['measurements']
        else:
            return None

    def first_measurement(self, name, dimensions):
        return [None, None, None] if self.get_measurements(name, dimensions) is None \
            else self.get_measurements(name, dimensions)[0]

    def last_measurement(self, name, dimensions):
        measurements = self.get_measurements(name, dimensions) 

        if measurements is None:
            raise Exception("No metrics")
        else:
            return measurements[-1]

    def _get_monasca_client(self):

        # Authenticate to Keystone
        ks = ksclient.KSClient(
            auth_url=self.monasca_auth_url,
            username=self.monasca_username,
            password=self.monasca_password,
            project_name=self.monasca_project_name,
            debug=False
        )

        # Monasca Client
        monasca_client = monclient.Client(self.monasca_api_version, ks.monasca_url,
                                          token=ks.token,
                                          debug=False)

        return monasca_client

    def send_metrics(self, measurements):

        batch_metrics = {'jsonbody': measurements}
        try:
            monasca_client = self._get_monasca_client()
            monasca_client.metrics.create(**batch_metrics)
        except exc.HTTPException as httpex:
            print httpex.message
        except Exception as ex:
            print ex.message
