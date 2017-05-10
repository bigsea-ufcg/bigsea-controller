import unittest
from service.api.actuator.instance_locator import Instance_Locator
from utils.ssh_utils import SSH_Utils
from mock.mock import MagicMock


class Test_Instance_Locator(unittest.TestCase):

    def setUp(self):
        self.compute_1 = "compute1"
        self.compute_2 = "compute2"
        self.user = "root"
        self.vm_id = "vm-id"
        
        self.ssh_utils = SSH_Utils()
        self.compute_nodes = [self.compute_1, self.compute_2]
        self.instance_locator = Instance_Locator(self.ssh_utils, self.compute_nodes)

    def tearDown(self):
        pass

    def located(self, command, user, host):
        return {self.compute_1:"0\n", self.compute_2:"1\n"}[host]

    def impossible_to_locate(self, command, user, host):
        return {self.compute_1:"1\n", self.compute_2:"1\n"}[host]

    def test_locate(self):
        self.ssh_utils.run_and_get_result = MagicMock()
        self.ssh_utils.run_and_get_result.side_effect = self.located
        
        result = self.instance_locator.locate(self.vm_id)
        
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), self.user, self.compute_1)
        self.assertEquals(result, self.compute_1)
        
    def test_locate_impossible_to_find_instance(self):
        self.ssh_utils.run_and_get_result = MagicMock()
        self.ssh_utils.run_and_get_result.side_effect = self.impossible_to_locate
        
        self.assertRaises(Exception, self.instance_locator.locate, self.vm_id)
        
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), self.user, self.compute_1)
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), self.user, self.compute_2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()