from subprocess import check_output

class Instance_Locator(object):

    def __init__(self):
        self.COMPUTE_NODES = ["c4-compute11", "c4-compute12"]
        
    def locate(self, vm_id):
        for compute_node in self.COMPUTE_NODES:
            print compute_node
            if int(check_output("ssh root@%s test -e \"/var/lib/nova/instances/%s\" && echo \"1\" || echo \"0\"" % (compute_node, vm_id), shell=True)) == 1:
                return compute_node
        raise Exception("It was not possible to find the instance")