# TODO: documentation
class Instance_Locator(object):

    def __init__(self, ssh_utils, compute_nodes):
        self.compute_nodes = compute_nodes
        self.ssh_utils = ssh_utils

    def locate(self, vm_id):
        # TODO: check vm_id
        for compute_node in self.compute_nodes:
            check_command = "virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (vm_id)
            in_node = self.ssh_utils.run_and_get_result(check_command, "root", compute_node)
            if in_node == "0\n":
                return compute_node
        #FIXME: exception type
        raise Exception("It was not possible to find the instance: command %s, ssh return value %s" % (check_command, in_node)) 
