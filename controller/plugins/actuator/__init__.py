# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ConfigParser

from controller.utils.ssh_utils import SSH_Utils
from controller.plugins.actuator.instance_locator_tunnel.plugin import Instance_Locator_Tunnel
from controller.plugins.actuator.remote_KVM_tunnel.plugin import Remote_KVM_Tunnel
from controller.plugins.actuator.kvm_actuator.plugin import KVM_Actuator
from controller.plugins.actuator.instance_locator.plugin import Instance_Locator
from controller.plugins.actuator.remote_kvm.plugin import Remote_KVM
from controller.plugins.actuator.nop_actuator.plugin import Nop_Actuator
from controller.plugins.actuator.service_actuator.plugin import Service_Actuator
from controller.plugins.actuator.service_instance_locator.plugin import Service_Instance_Locator
from controller.plugins.actuator.kvm_io_actuator.plugin import KVM_IO_Actuator
from controller.plugins.actuator.kvm_upv.plugin import KVM_Actuator_UPV

from abc.plugin import abstractmethod
from abc.plugin import ABCMeta


# TODO: documentation
class Actuator_Builder:

    def get_actuator(self, name, parameters):
        config = ConfigParser.RawConfigParser()
        config.read("controller.cfg")

        authorization_url = config.get("authorization", "authorization_url")
        bigsea_username = parameters["bigsea_username"]
        bigsea_password = parameters["bigsea_password"]

        authorization_data = dict(authorization_url=authorization_url,
                                  bigsea_username=bigsea_username,
                                  bigsea_password=bigsea_password)

        if name == "kvm":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            iops_reference = config.getint("actuator", "iops_reference")
            bs_reference = config.getint("actuator", "bs_reference")
            default_io_cap = config.getint("actuator", "default_io_cap")

            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_keypair)
            remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_keypair,
                                    iops_reference, bs_reference)
            return KVM_Actuator(instance_locator, remote_kvm, authorization_data, default_io_cap)

        elif name == "kvm-tunnel":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            iops_reference = config.getint("actuator", "iops_reference")
            bs_reference = config.getint("actuator", "bs_reference")
            default_io_cap = config.getint("actuator", "default_io_cap")

            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            ports_str = config.get("actuator", "tunnel_ports")
            ports = [x.strip() for x in ports_str.split(",")]

            hosts_ports = {compute_nodes[i]: ports[i] for i in xrange(len(ports))}

            instance_locator = Instance_Locator_Tunnel(SSH_Utils(hosts_ports), compute_nodes,
                                                       compute_nodes_keypair)
            remote_kvm = Remote_KVM_Tunnel(SSH_Utils(hosts_ports), compute_nodes_keypair,
                                           iops_reference, bs_reference)
            return KVM_Actuator(instance_locator, remote_kvm, authorization_data, default_io_cap)

        elif name == "kvm-io":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            iops_reference = config.getint("actuator", "iops_reference")
            bs_reference = config.getint("actuator", "bs_reference")
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            instance_locator = Instance_Locator(SSH_Utils({}), compute_nodes, compute_nodes_keypair)
            remote_kvm = Remote_KVM(SSH_Utils({}), compute_nodes_keypair, iops_reference,
                                    bs_reference)
            return KVM_IO_Actuator(instance_locator, remote_kvm, authorization_data)

        elif name == "kvm-io-tunnel":
            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes_keypair = config.get("actuator", "keypair_compute_nodes")
            iops_reference = config.getint("actuator", "iops_reference")
            bs_reference = config.getint("actuator", "bs_reference")

            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            ports_str = config.get("actuator", "tunnel_ports")
            ports = [x.strip() for x in ports_str.split(",")]

            hosts_ports = {compute_nodes[i]: ports[i] for i in xrange(len(ports))}

            instance_locator = Instance_Locator_Tunnel(SSH_Utils(hosts_ports), compute_nodes,
                                                       compute_nodes_keypair)
            remote_kvm = Remote_KVM_Tunnel(SSH_Utils(hosts_ports), compute_nodes_keypair,
                                           iops_reference, bs_reference)
            return KVM_IO_Actuator(instance_locator, remote_kvm, authorization_data)

        elif name == "kvm-upv":
            iops_reference = config.getint("actuator", "iops_reference")
            bs_reference = config.getint("actuator", "bs_reference")

            return KVM_Actuator_UPV(iops_reference, bs_reference)

        elif name == "nop":
            return Nop_Actuator()
        elif name == "service":
            actuator_port = config.get("actuator", "actuator_port")

            compute_nodes_str = config.get("actuator", "compute_nodes")
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            instance_locator = Service_Instance_Locator(compute_nodes, actuator_port)
            return Service_Actuator(actuator_port, instance_locator)
        else:
            # FIXME: review this exception type
            raise Exception("Unknown actuator type")


'''
The Actuator is the component responsible for connecting to the underlying infrastructure and
triggering the commands or API calls that allocate or deallocate resources, based on other
component's (normally the Controller) requests.
'''


class Actuator:
    __metaclass__ = ABCMeta

    '''
        Sets the amount of allocated resources to the given instances, using the given values
        of caps. This method expects a dictionary of format:

        {
            "instance_id_1":cap_value_1,
            "instance_id_2":cap_value_2
        }

        Normally used when executing an application.
    '''
    @abstractmethod
    def adjust_resources(self, vm_data):
        pass

    '''
        Returns a number which represents the amount of allocated resources to the given instance
    '''
    @abstractmethod
    def get_allocated_resources(self, vm_id):
        pass

    '''
        Returns a number which represents the amount of allocated resources to the given cluster
    '''
    @abstractmethod
    def get_allocated_resources_to_cluster(self, vms_ids):
        pass

