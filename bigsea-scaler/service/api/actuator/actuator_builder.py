from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.remote_kvm import Remote_KVM
from utils.ssh_utils import SSH_Utils
import ConfigParser

# TODO: documentation


class Actuator_Builder:

    def get_actuator(self, name):
        if name == "basic":
            config = ConfigParser.RawConfigParser()
            config.read("controller.cfg")
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]
            
            instance_locator = Instance_Locator(SSH_Utils(), compute_nodes, compute_nodes_keypair)
            remote_kvm = Remote_KVM(SSH_Utils(), compute_nodes_keypair)
            return Basic_Actuator(instance_locator, remote_kvm)
        else:
            # FIXME: review this exception type
            raise Exception("Unknown actuator type")
