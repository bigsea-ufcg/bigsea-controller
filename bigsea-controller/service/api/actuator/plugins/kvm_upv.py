from service.api.actuator.actuator import Actuator

import ConfigParser
import subprocess

# TODO: documentation


class KVM_Actuator_UPV(Actuator):

    def __init__(self, conn):
        self.conn = conn
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
        host = self._find_host(vm_id)
        # ssh for the actual host
        self.conn.exec_command("ssh %s") % host
        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn.exec_command("virsh list")
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)
        command = ("virsh schedinfo %s | grep vcpu_quota " +
                   "| awk '{print $3}'" % (virsh_id))
        stdin, stdout, stderr = self.conn.exec_command(command)
        return stdout.read()

    def _change_vcpu_quota(self, host, vm_id, cap):
        # ssh for the actual host
        self.conn.exec_command("ssh %s") % host
        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn.exec_command("virsh list")
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)
        # Set the CPU cap
        self.conn.exec_command("virsh schedinfo %s " +
                               "--set vcpu_quota=%s " +
                               "> /dev/null") % (virsh_id, cap)
        # Go back to the access node
        self.conn.exec_command("logout")

    def x_find_host(self, vm_id):
        bashCommand = ("onevm show %s --user %s " +
                       "--password %s --endpoint %s") % (vm_id, self.one_user,
                                                         self.one_password, self.one_url)

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        for line in output.split('\n'):
            if "HOST" in line and "niebla" in line:
                return line.split()[2]

        return None

    def _extract_id(self, vm_list, vm_id):
        one_id = "one-" + vm_id
        for vm in vm_list:
            if one_id in vm:
                return vm.split()[0]

        return None

