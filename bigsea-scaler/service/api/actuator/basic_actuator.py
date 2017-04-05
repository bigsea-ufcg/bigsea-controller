from actuator import Actuator

# TODO: documentation


class Basic_Actuator(Actuator):

    def __init__(self, instance_locator, remote_kvm):
        self.instance_locator = instance_locator
        self.remote_kvm = remote_kvm

    # TODO: validation
    def prepare_environment(self, vm_data):
        self.adjust_resources(vm_data)

    # TODO: validation
    def adjust_resources(self, vm_data):
        instances_locations = {}

        # discover vm_id - compute nodes map
        for instance in vm_data.keys():
            instances_locations[instance] = self.instance_locator.locate(instance)

        # access compute nodes
        # change cap
        for instance in vm_data.keys():
            self.remote_kvm.change_vcpu_quota(instances_locations[instance], instance, vm_data[instance])

    # TODO: validation
    def get_allocated_resources(self, vm_id):
        host = self.instance_locator.locate(vm_id)
        return self.remote_kvm.get_allocated_resources(host, vm_id)
