from service.api.actuator.actuator import Actuator
from service.exceptions.kvm_exceptions import InstanceNotFoundException

import ConfigParser
import subprocess

# TODO: documentation


class KVM_Actuator_UPV(Actuator):

    def __init__(self, conn_compute, conn_onevm):
        self.conn_compute = conn_compute
        self.conn_onevm = conn_onevm
        self.config = ConfigParser.RawConfigParser()
        self.config.read("controller.cfg")
        self.one_user = self.config.get("actuator", "one_username")
        self.one_password = self.config.get("actuator", "one_password")
        self.one_url = self.config.get("actuator", "one_url")


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
            instances_locations[instance] = self._find_host(instance)

        for instance in vm_data.keys():
            # Access a compute node and change cap
            self._change_vcpu_quota(instances_locations[instance],
                                    instance, int(vm_data[instance]))

    # TODO: validation
    def get_allocated_resources(self, vm_id):
        # Access compute nodes to discover vm location
        import pdb; pdb.set_trace()
        host = self._find_host(vm_id)
        # ssh for the actual host
        self.conn_compute.exec_command("ssh %s" % host)
        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn_compute.exec_command("virsh list")
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)
        command = ("virsh schedinfo %s | grep vcpu_quota " +
                   "| awk '{print $3}'" % (virsh_id))
        stdin, stdout, stderr = self.conn_compute.exec_command(command)
        self.conn_compute.exec_command("logout")
        return stdout.read()

    def get_allocated_resources_to_cluster(self, vms_ids):
        for vm_id in vms_ids:
            try:
                return self.get_allocated_resources(vm_id)
            except InstanceNotFoundException:
                print "instance not found:%s" % (vm_id)
                
        raise Exception("Could not get allocated resources")

    def _change_vcpu_quota(self, host, vm_id, cap):
        # ssh for the actual host
        self.conn_compute.exec_command("ssh %s" % host)
        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn_compute.exec_command("virsh list")
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)
        # Set the CPU cap
        self.conn_compute.exec_command("virsh schedinfo %s " +
                               "--set vcpu_quota=%s " +
                               "> /dev/null") % (virsh_id, cap)
        # Go back to the access node
        self.conn_compute.exec_command("logout")

    def _find_host(self, vm_id):
        list_vms = ("onevm show %s --user %s " +
                       "--password %s --endpoint %s") % (vm_id, self.one_user,
                                                         self.one_password, self.one_url)

        stdin, stdout, stderr = self.conn_onevm.exec_command(list_vms)

        for line in stdout.read().split('\n'):
            if "HOST" in line and "niebla" in line:
                return line.split()[2]

        return None

    def _extract_id(self, vm_list, vm_id):
        one_id = "one-" + vm_id
        for vm in vm_list:
            if one_id in vm:
                return vm.split()[0]

        return None

