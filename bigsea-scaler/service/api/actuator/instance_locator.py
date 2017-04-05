# TODO: documentation
class Instance_Locator(object):

    def __init__(self, ssh_utils):
        # FIXME: hard coded
        self.COMPUTE_NODES = ["c4-compute11", "c4-compute12"]
        self.ssh_utils = ssh_utils

    def locate(self, vm_id):
        # TODO: check vm_id
        for compute_node in self.COMPUTE_NODES:
            check_command = "test -e \"/var/lib/nova/instances/%s\" && echo \"1\" || echo \"0\"" % (vm_id)
            in_node = self.ssh_utils.run_and_get_result(check_command, "root", compute_node)
            if in_node == "1":
                return compute_node
        raise Exception("It was not possible to find the instance")
            
        
