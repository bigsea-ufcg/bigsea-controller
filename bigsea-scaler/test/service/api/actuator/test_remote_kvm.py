import unittest
from service.api.actuator.plugins.remote_kvm import Remote_KVM
from utils.ssh_utils import SSH_Utils
from mock.mock import MagicMock

class Test_Remote_KVM(unittest.TestCase):

    def setUp(self):
        self.ssh_utils = SSH_Utils({})
        self.compute_nodes_key = "key"
        self.remote_kvm = Remote_KVM(self.ssh_utils, self.compute_nodes_key)
        self.cap = 56
        self.host_ip = "vm-ip"
        self.vm_id = "vm-id"

    def tearDown(self):
        pass

    def test_change_cpu_quota(self):
        self.ssh_utils.run_command = MagicMock(return_value=None)

        self.remote_kvm.change_vcpu_quota(self.host_ip, self.vm_id, self.cap)

        command = "virsh schedinfo %s --set vcpu_quota=%s > /dev/null" % (self.vm_id, self.cap*1000)
        self.ssh_utils.run_command.assert_called_once_with(command, "root", self.host_ip, self.compute_nodes_key)

    def test_change_cpu_quota_negative_cap_value(self):
        self.assertRaises(Exception, self.remote_kvm.change_vcpu_quota, self.host_ip, self.vm_id, -10, self.compute_nodes_key)

    def test_change_cpu_quota_too_high_cap_value(self):
        self.assertRaises(Exception, self.remote_kvm.change_vcpu_quota, self.host_ip, self.vm_id, 100 + 20, self.compute_nodes_key)

    def test_get_allocated_resources_success(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="56000")

        result_cap = self.remote_kvm.get_allocated_resources(self.host_ip, self.vm_id)

        self.assertEquals(result_cap, 56)

        command = "virsh schedinfo %s | grep vcpu_quota | awk '{print $3}'" % self.vm_id
        self.ssh_utils.run_and_get_result.assert_called_once_with(command, "root", self.host_ip, self.compute_nodes_key)

    def test_get_allocated_resources_virsh_returns_negative_1(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="-1")

        result_cap = self.remote_kvm.get_allocated_resources(self.host_ip, self.vm_id)

        self.assertEquals(result_cap, 100)

        command = "virsh schedinfo %s | grep vcpu_quota | awk '{print $3}'" % self.vm_id
        self.ssh_utils.run_and_get_result.assert_called_once_with(command, "root", self.host_ip, self.compute_nodes_key)

    def test_get_allocated_resources_ssh_returns_empty_string(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="")

        self.assertRaises(Exception, self.remote_kvm.get_allocated_resources, self.host_ip, self.vm_id, self.compute_nodes_key)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
