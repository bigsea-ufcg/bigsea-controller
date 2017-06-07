import requests
import json

class Service_Instance_Locator:

    def __init__(self, compute_nodes, actuator_service_port):
        self.compute_nodes = compute_nodes
        self.actuator_service_port = actuator_service_port

    def locate(self, vm_id):
        # TODO: check vm_id
        for compute_node in self.compute_nodes:
            url = "http://" + compute_node + ":" + str(self.actuator_service_port) + "/actuator/list_vms/"
            options = {"actuator_plugin":"kvm", "vm_id":vm_id}
            response = requests.post(url, headers = {"Content-Type":"application/json"}, data = json.dumps(options))
            vms_ids_str = response.text
            vms_ids = vms_ids_str.split(",")
            
            if vm_id in vms_ids:
                return compute_node
            
        raise Exception("It was not possible to find the instance %s" % (vm_id)) 