# Copyright (c) 2018 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""kubeadm_actuator module contains the classes to operate
    in kubeadm clusters and join/unjoin new nodes.
"""

import ConfigParser
import time
import uuid
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
import paramiko
import kubernetes.client


def wait_for_node(host, key):
    """ Wait for a node creation and main services to be up
    - param: host=ip addres to the new node
    - param: key_path=private key path to access the new host
    """
    host_available = False
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while not host_available:
        try:
            cli.connect(host, username="ubuntu", key_filename=key)
            host_available = True
        except paramiko.SSHException as e:
            print e
            time.sleep(2)
    cli.close()


def wait_for_node_ready(node_name):
    """ Waits for a specified node to be ready
    - param: node_name=name of the node to be examined
    """
    ready = False
    core_v1 = kubernetes.client.CoreV1Api()
    nodes = core_v1.list_node()
    current_node = None
    for node in nodes.items:
        if node.metadata.name == node_name:
            current_node = node
    while not ready:
        for event in current_node.status.conditions:
            if event.type == "Ready":
                ready = (event.status in ["True"])

class KubeadmActuator:
    def __init__(self, master):

        cmd = """kubeadm join --token f9b3ff.fcb6cb5f9bb158ee %s \
            --discovery-token-unsafe-skip-ca-verification""" % master
        self.join = dict(
            name="Join kubernetes node",
            tasks=[
                dict(action=dict(
                    module='command',
                    args='kubeadm reset'),
                     name="Reset previous k8s cluster"),
                dict(action=dict(
                    module='command',
                    args=cmd),
                     name="Join node")
            ]
        )
        self.unjoin = dict(
            name="Remove kubernetes node",
            gather_facts='no',
            tasks=[
                dict(action=dict(module='command', args='kubeadm reset'))
            ]
        )

        config = ConfigParser.RawConfigParser()
        config.read('controller.cfg')

        self.username = config.get('keystoneauth', 'username')
        self.password = config.get('keystoneauth', 'password')
        self.auth_url = config.get('keystoneauth', 'auth_url')
        self.project_name = config.get('keystoneauth', 'project_name')
        self.project_domain_name = config.get('keystoneauth', 'project_domain_name')
        self.user_domain_name = config.get('keystoneauth', 'user_domain_name')

        self.image_uuid = config.get('kubeadm_actuator', 'image_uuid')
        self.flavor_name = config.get('kubeadm_actuator', 'flavor_name')
        self.network_uuid = config.get('kubeadm_actuator', 'network_uuid')
        self.key_name = config.get('kubeadm_actuator', 'key_name')
        self.key_path = config.get('kubeadm_actuator', 'key_path')
        self.timeout = config.getint('kubeadm_actuator', 'node_creation_timeout')
        config_path = config.get("actuator", "k8s_manifest")
        kubernetes.config.load_kube_config(config_path)

        self.novaclient = self._get_nova_client()

    def _get_ksa_session(self):
        """Authenticate to keystone and return a keystoneauth1 Session"""
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url=self.auth_url, password=self.password,
            username=self.username, project_name=self.project_name,
            project_domain_name=self.project_domain_name,
            user_domain_name=self.user_domain_name)

        return session.Session(auth=auth)

    def _get_nova_client(self):
        """Create a novaclient.client.Client instance (version = 2.1)"""
        sess = self._get_ksa_session()
        return client.Client("2.1", session=sess)

    def create_node(self):
        """Create one node (OpenStack instance) and return it."""
        flavor = self.novaclient.flavors.find(name=self.flavor_name)
        nics = [{"net-id": self.network_uuid}]

        node_uuid = self.novaclient.servers.create(
            name=uuid.uuid4(), image=self.image_uuid, flavor=flavor,
            nics=nics, key_name=self.key_name).id

        # give it some time...
        time.sleep(10)
        start = time.time()

        node = self.novaclient.servers.find(id=node_uuid)
        while node.status != 'ACTIVE':
            print "waiting for node to be ready..."
            print "current status: %s" % node.status
            time.sleep(5)

            if time.time() - start > self.timeout:
                self.delete_node(node_uuid)
                raise Exception("timeout exceeded. deleting instance.")
            elif node.status == 'ERROR':
                self.delete_node(node_uuid)
                raise Exception("something went wrong. deleting instance")

            node = self.novaclient.servers.find(id=node_uuid)

        return node

    def delete_node(self, id):
        nc = self._get_nova_client()
        nc.servers.delete(id)

    def reset_node(self, host, key_path):
        """ Resets a node so it won't be part of a kubernetes cluster
        - param: host=ip addres to the new node
        - param: key_path=private key path to access the new host
        """
        self._run_playbook(host=host, key_path=key_path, play_source=self.unjoin)

    def join_node(self, host, node_name, key_path):
        """ Joins a new node to a previous configured kubernetes cluster
        - param: host=ip addres to the new node
        - param: key_path=private key path to access the new host
        """
        self._run_playbook(host=host, key_path=key_path, play_source=self.join)
        wait_for_node_ready(node_name)

    def _run_playbook(self, host, key_path, play_source):
        """ Runs a playbook in the specified host
        - param: host=ip addres to the new node
        - param: key_path=private key path to access the new host
        - param: play_source=dictionary with the playbook source
        - returns: ansible code for the playbook operation (0 for success)
        """
        wait_for_node(host=host, key=key_path)

        options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts',
                                         'syntax', 'connection', 'module_path', 'forks',
                                         'remote_user', 'private_key_file', 'ssh_common_args',
                                         'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args',
                                         'become', 'become_method', 'become_user', 'verbosity',
                                         'check', 'diff', 'python_interpreter'])
        opts = options(listtags=False, listtasks=False, listhosts=False, syntax=False,
                       connection='ssh', module_path=None, forks=100, remote_user='ubuntu',
                       private_key_file=key_path, ssh_common_args=None, ssh_extra_args=None,
                       sftp_extra_args=None, scp_extra_args=None, become=True,
                       become_method='sudo', become_user='root', verbosity=None,
                       check=False, diff=False)
        passwords = dict(vault_pass='secret')
        self.join["hosts"] = [host]
        loader = DataLoader()
        inventory = InventoryManager(loader=loader, sources='%s,' % host)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=opts,
                passwords=passwords,
                stdout_callback=None
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
        return result
