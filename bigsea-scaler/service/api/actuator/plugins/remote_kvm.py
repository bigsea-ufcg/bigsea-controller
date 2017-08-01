# TODO: documentation
class Remote_KVM(object):

    def __init__(self, ssh_utils, compute_nodes_key, io_quota_to_vm = 1000, max_io = 1000000):
        self.ssh_utils = ssh_utils
        self.compute_nodes_key = compute_nodes_key
        self.io_quota_to_vm = io_quota_to_vm
        self.max_io = max_io

    # Warning: This code requires that the vcpu_quota parameter is between 0 and 100000
    def change_vcpu_quota(self, host_ip, vm_id, cap):
        # TODO: check ip value
        # TODO: check id value
        if cap < 0 or cap > 100:
            # FIXME review this exception type
            raise Exception("Invalid cap value")
        
        command = "virsh schedinfo %s --set vcpu_quota=%s > /dev/null" % (vm_id, cap*1000)
        # TODO: check errors
        self.ssh_utils.run_command(command, "root", host_ip, self.compute_nodes_key)

    def change_io_quota(self, host_ip, vm_id, cap):
        if cap < 0 or cap > 100:
            # FIXME review this exception type
            raise Exception("Invalid cap value")
        
        command_get_block_device = "virsh domblklist %s | awk 'FNR == 3 {print $1}'" % (vm_id)
        block_device = self.ssh_utils.run_command_and_get_result(command_get_block_device, "root", host_ip, self.compute_nodes_key)
        
        #virsh blkdeviotune lubuntu_1604 vda --current --total_bytes_sec 1000000
        command_set_io_quota = "virsh blkdeviotune %s %s --current --total_bytes_sec %d" % \
                        (vm_id, block_device, cap*self.io_quota_to_vm)
        
        self.ssh_utils.run_command(command_set_io_quota, "root", host_ip, self.compute_nodes_key)
    
    # Warning: This code requires that the vcpu_quota parameter is between 0 and 100000
    # TODO: Change this method name to get_vcpu_quota
    def get_allocated_resources(self, host_ip, vm_id):
        # TODO: check ip value
        # TODO: check id value
        command = "virsh schedinfo %s | grep vcpu_quota | awk '{print $3}'" % (vm_id)
        # TODO: check errors
        ssh_result = self.ssh_utils.run_and_get_result(command, "root", host_ip, self.compute_nodes_key)
        
        try:
            cap = int(ssh_result)
        
            if cap == 0:
                raise Exception("Could not get allocated resources")
            
            if cap == -1:
                return 100
            return cap/1000
        
        except:
            # FIXME: review this exception type
            raise Exception("Could not get allocated resources")

    def get_io_quota(self, host_ip, vm_id):
        command_get_block_device = "virsh domblklist %s | awk 'FNR == 3 {print $1}'" % (vm_id)
        block_device = self.ssh_utils.run_and_get_result(command_get_block_device, "root", host_ip, self.compute_nodes_key)
        
        command = "virsh blkdeviotune %s %s | grep total_bytes_sec: | awk {'print $2'}" % (vm_id, block_device)
        ssh_result = self.ssh_utils.run_and_get_result(command, "root", host_ip, self.compute_nodes_key)
        
        try:
            quota = int(ssh_result)
            return 100*quota/float(self.io_quota_to_vm)
        except:
            # FIXME: review this exception type
            raise Exception("Could not get allocated resources")
