from subprocess import check_output

hosts_ports = {"c4-compute11":9000, "c4-compute12":9001, "c4-compute22":9002}

class SSH_Utils(object):

#     def run_command(self, command, user, host):
#         check_output('ssh -o "StrictHostKeyChecking no" %s@%s %s' % (user, host, command), shell=True)
# 
#     def run_and_get_result(self, command, user, host):
#         return check_output('ssh -o "StrictHostKeyChecking no" %s@%s %s' % (user, host, command), shell=True)
    
    def run_command(self, command, user, host):
        check_output('ssh -o "StrictHostKeyChecking no" root@127.0.0.1 -p %s %s' % (hosts_ports[host], command), shell=True)

    def run_and_get_result(self, command, user, host):
        return check_output('ssh -o "StrictHostKeyChecking no" root@127.0.0.1 -p %s %s' % (hosts_ports[host], command), shell=True)
