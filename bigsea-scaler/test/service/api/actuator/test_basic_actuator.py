from mock import MagicMock
import unittest

from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.remote_kvm import Remote_KVM
from utils.ssh_utils import SSH_Utils


class Test_Basic_Actuator(unittest.TestCase):

    def setUp(self):
        self.vm_id1 = "vm_id1"
        self.vm_id2 = "vm_id2"

        self.host_ip1 = "host_ip1"
        self.host_ip2 = "host_ip2"

        self.cap1 = 50
        self.cap2 = 78

        self.instance_locator = Instance_Locator()
        self.remote_kvm = Remote_KVM(SSH_Utils())
        self.actuator = Basic_Actuator(self.instance_locator, self.remote_kvm)

    def locator(self, vm_id):
        return {self.vm_id1:self.host_ip1, self.vm_id2:self.host_ip2}[vm_id]

    # TODO more cases
    def test_basic_actuator_locates_and_acts_correctly_1_instance(self):
        vm_data = {self.vm_id1:self.cap1}

        self.instance_locator.locate = MagicMock(return_value=self.host_ip1)
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)

        self.actuator.prepare_environment(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_called_once_with(self.host_ip1, self.vm_id1, self.cap1)

    def test_basic_actuator_locates_and_acts_correctly_n_instances(self):
        vm_data = {self.vm_id1:self.cap1,self.vm_id2:self.cap2}

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)

        self.actuator.prepare_environment(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_any_call(self.vm_id1)
        self.instance_locator.locate.assert_any_call(self.vm_id2)

        # Actuator tries to locate only the given instances
        self.assertEqual(self.instance_locator.locate.call_count, 2)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_any_call(self.host_ip1, self.vm_id1, self.cap1)
        self.remote_kvm.change_vcpu_quota.assert_any_call(self.host_ip2, self.vm_id2, self.cap2)

        # Actuator tries to change the cap of only the given instances
        self.assertEqual(self.remote_kvm.change_vcpu_quota.call_count, 2)

    def test_adjust_resources_locates_and_acts_correctly_1_instance(self):
        vm_data = {self.vm_id1:self.cap1}

        self.instance_locator.locate = MagicMock(return_value=self.host_ip1)
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)

        self.actuator.adjust_resources(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_called_once_with(self.host_ip1, self.vm_id1, self.cap1)

    def test_adjust_resources_locates_and_acts_correctly_n_instances(self):
        vm_data = {self.vm_id1:self.cap1,self.vm_id2:self.cap2}

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)

        self.actuator.adjust_resources(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_any_call(self.vm_id1)
        self.instance_locator.locate.assert_any_call(self.vm_id2)

        # Actuator tries to locate only the given instances
        self.assertEqual(self.instance_locator.locate.call_count, 2)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_any_call(self.host_ip1, self.vm_id1, self.cap1)
        self.remote_kvm.change_vcpu_quota.assert_any_call(self.host_ip2, self.vm_id2, self.cap2)

        # Actuator tries to change the cap of only the given instances
        self.assertEqual(self.remote_kvm.change_vcpu_quota.call_count, 2)

    def test_get_allocated_resources(self):
        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.get_allocated_resources = MagicMock(return_value=50)

        cap = self.actuator.get_allocated_resources(self.vm_id1)

        # Actuator returns the correct cap value
        self.assertEquals(cap, 50)

        # Actuator tries to locate the instance
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to get the resources allocated to the given instance
        self.remote_kvm.get_allocated_resources.assert_called_once_with(self.host_ip1, self.vm_id1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
