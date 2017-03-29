from subprocess import Popen, check_output

# TODO: documentation
class Remote_KVM(object):

    def change_vcpu_quota(self, host_ip, vm_id, cap):
        # TODO: Separate virsh and ssh code to allow tests
        command = "virsh schedinfo %s --set vcpu_quota=%s > /dev/null" % (vm_id, cap*1000)
        Popen('ssh -o "StrictHostKeyChecking no" root@%s %s' % (host_ip, command), shell=True)

    def get_allocated_resources(self, host_ip, vm_id):
        # TODO: Separate virsh and ssh code to allow tests
        command = "virsh schedinfo %s | grep vcpu_quota | awk '{print $3}'" % (vm_id)
        cap = check_output('ssh -o "StrictHostKeyChecking no" root@%s %s' % (host_ip, command),
                           shell=True)
        # TODO: Check the returned value
        cap = int(cap)
        if cap == -1:
            return 100
        return cap/1000
