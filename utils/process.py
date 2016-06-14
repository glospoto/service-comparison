import os
from subprocess import Popen, PIPE

import signal

# TODO Implement a factory to create new processes


class FactoryProcess(object):
    pass

"""
This class implements a wrapper to execute independent processes into bash. Currently, this class wraps subprocess.Popen
object
"""


class Process(object):
    def __init__(self):
        # The process returned by Popen constructor
        self._process = None
        # The PID taken by the object built by Popen()
        self._pid = None
        # The object returned by psutil.Process() constructor
        self._ps_process = None

    def __repr__(self):
        return 'Process[pid=%s]' % str(self._pid)

    '''
    Execute a commando into a bash terminal. By default both stdout and stderr will be redirect on /dev/null.
    '''

    def execute(self, command, shell=True, stdout=PIPE, stderr=PIPE):
        self._process = Popen(command, shell=shell, stdout=stdout, stderr=stderr)
        # Take the PID from the process object
        self._pid = self._process.pid
        # TODO Move inside this method the Popen.communicate() or Popen.wait() functions invoked on the current process
        # TODO based on the content of stdout parameter (stdout=PIPE -> communicate; stdout=None -> wait.)

    '''
    Wait the end of the command.
    '''

    def communicate(self):
        self._process.communicate()

    '''
    Kill a process by pid.
    '''

    def kill(self):
        os.kill(self._pid, signal.SIGTERM)

    '''
    Kill this process and all its children.
    '''

    def kill_all(self):
        # Create a psutil.Process object
        self._ps_process = Process(self._pid)
        # Take the children
        children = self._process.childred(recursive=True)
        # Kill each children
        for child in children:
            os.kill(child.pid, signal.SIGTERM)
