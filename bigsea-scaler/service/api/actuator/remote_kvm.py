from subprocess import Popen

class Remote_KVM(object):
    
    def change_vcpu_quota(self, host_ip, vm_id, cap):
        command = "virsh schedinfo %s --set vcpu_quota=%s > /dev/null" % (vm_id, cap*1000)
        Popen('ssh -o "StrictHostKeyChecking no" root@%s %s' % (host_ip, command), shell=True)