import unittest

from mock import MagicMock
from service.api.actuator.instance_locator import Instance_Locator
from service.api.actuator.basic_actuator import Basic_Actuator
from service.api.actuator.remote_kvm import Remote_KVM

class TestBasicActuator(unittest.TestCase):
    
    def setUp(self):
        self.instance_locator = Instance_Locator()
        self.remote_kvm = Remote_KVM()
        self.actuator = Basic_Actuator(self.instance_locator, self.remote_kvm)
        
    def locator(self, vm_id):
        return {"vm_id1":"host_ip1", "vm_id2":"host_ip2"}[vm_id]
        
    # TODO more cases
    def test_basic_actuator_locates_and_acts_correctly_1_instance(self):
        vm_data = {"vm_id":50}
        
        self.instance_locator.locate = MagicMock(return_value="host_ip")
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        
        self.actuator.prepare_environment(vm_data)
        self.instance_locator.locate.assert_called_once_with("vm_id")
        self.remote_kvm.change_vcpu_quota.assert_called_once_with("host_ip", "vm_id", 50)
        
    def test_basic_actuator_locates_and_acts_correctly_n_instances(self):
        vm_data = {"vm_id1":50,"vm_id2":78}
        
        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        
        self.actuator.prepare_environment(vm_data)
        self.instance_locator.locate.assert_any_call("vm_id1")
        self.instance_locator.locate.assert_any_call("vm_id2")
        
        self.assertEqual(self.instance_locator.locate.call_count, 2)
        
        self.remote_kvm.change_vcpu_quota.assert_any_call("host_ip1", "vm_id1", 50)
        self.remote_kvm.change_vcpu_quota.assert_any_call("host_ip2", "vm_id2", 78)
    
        self.assertEqual(self.remote_kvm.change_vcpu_quota.call_count, 2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
