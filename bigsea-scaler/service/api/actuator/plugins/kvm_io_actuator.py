from service.api.actuator.actuator import Actuator

class KVM_IO_Actuator(Actuator):
    
    def __init__(self, instance_locator, remote_kvm):
        self.instance_locator = instance_locator
        self.remote_kvm = remote_kvm

    # TODO: validation
    def prepare_environment(self, vm_data):
        self.adjust_resources(vm_data)

    # TODO: validation
    # This method receives as argument a map {vm-id:cap}
    def adjust_resources(self, vm_data):
        instances_locations = {}

        # Discover vm_id - compute nodes map
        for instance in vm_data.keys():
            # Access compute nodes to discover vms location
            instances_locations[instance] = self.instance_locator.locate(instance)

        for instance in vm_data.keys():
            # Access a compute node and change cap
            self.remote_kvm.change_vcpu_quota(instances_locations[instance], instance, int(vm_data[instance]))
            self.remote_kvm.change_io_quota(instances_locations[instance], instance, int(vm_data[instance]))

    # TODO: validation
    def get_allocated_resources(self, vm_id):
        # Access compute nodes to discover vm location
        host = self.instance_locator.locate(vm_id)
        # Access a compute node and get amount of allocated resources
        return self.remote_kvm.get_allocated_resources(host, vm_id)