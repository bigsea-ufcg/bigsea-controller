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

from service.api.actuator.actuator import Actuator

# TODO: documentation


class KVM_Actuator(Actuator):

    def __init__(self, instance_locator, remote_kvm):
        self.instance_locator = instance_locator
        self.remote_kvm = remote_kvm

    # TODO: validation
    def prepare_environment(self, vm_data):
        self.adjust_resources(vm_data)

    # TODO: validation
    # This method receives as argument a map {vm-id:CPU cap}
    def adjust_resources(self, vm_data):
        instances_locations = {}

        # Discover vm_id - compute nodes map
        for instance in vm_data.keys():
            # Access compute nodes to discover vms location
            instances_locations[instance] = self.instance_locator.locate(instance)

        for instance in vm_data.keys():
            # Access a compute node and change cap
            self.remote_kvm.change_vcpu_quota(instances_locations[instance], instance, int(vm_data[instance]))
            # Add a call to change_io_quota

    # TODO: validation
    def get_allocated_resources(self, vm_id):
        # Access compute nodes to discover vm location
        host = self.instance_locator.locate(vm_id)
        # Access a compute node and get amount of allocated resources
        return self.remote_kvm.get_allocated_resources(host, vm_id)
