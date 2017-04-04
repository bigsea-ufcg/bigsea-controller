from subprocess import Popen, check_output


class SSH_Utils(object):

    def run_command(self, command, user, host):
        Popen('ssh -o "StrictHostKeyChecking no" %s@%s %s' % (user, host, command))

    def run_and_get_result(self, command, user, host):
        return check_output('ssh -o "StrictHostKeyChecking no" %s@%s %s' % (user, host, command), shell=True)
