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

from controller.utils.ssh import SSHUtils
from controller.service import api

from controller.plugins.actuator.kvm.plugin import KVMActuator
from controller.plugins.actuator.kvm_io.plugin import KVMIOActuator
from controller.plugins.actuator.kvm_upv.plugin import KVMUPVActuator
from controller.plugins.actuator.service.plugin import ServiceActuator
from controller.plugins.actuator.nop.plugin import NopActuator

from controller.utils.locator.instance import InstanceLocator
from controller.utils.locator.instance_tunnel import InstanceTunnelLocator
from controller.utils.locator.service_instance import ServiceInstanceLocator

from controller.utils.remote.kvm import RemoteKVM
from controller.utils.remote.kvm_tunnel import RemoteKVMTunnel


class ActuatorBuilder:
    def get_actuator(self, name, parameters):
        if name == "kvm":
            compute_nodes_str = api.compute_nodes_str
            compute_nodes_keypair = api.compute_nodes_keypair

            iops_reference = api.iops_reference
            bs_reference = api.bs_reference
            default_io_cap = api.default_io_cap
            tunelling = api.tunelling

            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            if tunelling == "True": 
                instance_locator = InstanceLocator(SSHUtils({}),
                                       compute_nodes, compute_nodes_keypair)

                remote_kvm = RemoteKVM(SSHUtils({}), compute_nodes_keypair,
                                        iops_reference, bs_reference)

            else:
                ports_str = api.ports_str
                ports = [x.strip() for x in ports_str.split(",")]

                hosts_ports = {compute_nodes[i]: ports[i]
                               for i in xrange(len(ports))}

                instance_locator = InstanceTunnelLocator(
                                       SSHUtils(hosts_ports), compute_nodes,
	            			   compute_nodes_keypair)

                remote_kvm = RemoteKVMTunnel(SSHUtils(hosts_ports),
                                               compute_nodes_keypair,
                                               iops_reference, bs_reference)

            return KVMActuator(instance_locator, remote_kvm,
                               authorization_data, default_io_cap)

        elif name == "kvm_io":
            compute_nodes_str = api.compute_nodes_str
            compute_nodes_keypair = api.compute_nodes_keypair

            iops_reference = api.iops_reference
            bs_reference = api.bs_reference
            default_io_cap = api.default_io_cap
            tunelling = api.tunelling

            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            if tunelling == "True":
                instance_locator = InstanceLocator(SSHUtils({}),
                                                    compute_nodes,
                                                    compute_nodes_keypair)
     
                remote_kvm = RemoteKVM(SSHUtils({}), compute_nodes_keypair,
                                        iops_reference, bs_reference)

            else:
                ports_str = api.ports_str
                ports = [x.strip() for x in ports_str.split(",")]

                hosts_ports = {compute_nodes[i]: ports[i]
                               for i in xrange(len(ports))}

                instance_locator = InstanceTunnelLocator(
                                       SSHUtils(hosts_ports),
                                       compute_nodes, compute_nodes_keypair)

                remote_kvm = RemoteKVMTunnel(SSHUtils(hosts_ports),
                                               compute_nodes_keypair,
                                               iops_reference, bs_reference)

                
            return KVMIOActuator(instance_locator, remote_kvm,
                                   authorization_data)

        elif name == "kvm_upv":
            iops_reference = api.iops_reference
            bs_reference = api.bs_reference

            return KVMUPVActuator(iops_reference, bs_reference)

        elif name == "service":
            actuator_port = api.actuator_port

            compute_nodes_str = api.compute_nodes_str
            compute_nodes = [x.strip() for x in compute_nodes_str.split(",")]

            instance_locator = ServiceInstanceLocator(compute_nodes,
                                                        actuator_port)

            return ServiceActuator(actuator_port, instance_locator)

        elif name == "nop":
            return NopActuator()

        else:
            # FIXME: review this exception type
            raise Exception("Unknown actuator type")
