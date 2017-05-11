import ConfigParser

#from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.plugins.instance_locator_tunnel import Instance_Locator_Tunnel
from service.api.actuator.plugins.remote_KVM_tunnel import Remote_KVM_Tunnel
#from service.api.actuator.remote_kvm import Remote_KVM
from utils.ssh_utils import SSH_Utils
from service.api.actuator.plugins.kvm_actuator import KVM_Actuator
from service.api.actuator.plugins.instance_locator import Instance_Locator
from service.api.actuator.plugins.remote_kvm import Remote_KVM


# TODO: documentation
class Actuator_Builder:

    def get_actuator(self, name):
        config = ConfigParser.RawConfigParser()
        config.read("scaler.cfg")
        
        if name == "kvm":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]
            
            instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_keypair)
            remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_keypair)
            return KVM_Actuator(instance_locator, remote_kvm)
        elif name == "kvm-tunnel":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]
            
            ports_str = config.get("actuator", "tunnel_ports")
            ports = [x.strip() for x in ports_str.split(",")]
            
            hosts_ports = {compute_nodes[i]:ports[i] for i in xrange(len(ports))}
            
            instance_locator = Instance_Locator_Tunnel(SSH_Utils(hosts_ports), compute_nodes, compute_nodes_keypair)
            remote_kvm = Remote_KVM_Tunnel(SSH_Utils(hosts_ports), compute_nodes_keypair)
            return KVM_Actuator(instance_locator, remote_kvm)
        else:
            # FIXME: review this exception type
            raise Exception("Unknown actuator type")
