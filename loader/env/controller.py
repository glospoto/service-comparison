from subprocess import Popen, PIPE

import signal
import os
import psutil

from utils.fs import FileSystem
from utils.log import Logger

"""
This class is able to run an SDN controller.
"""


class ControllerStarter(object):
    def __init__(self, controller_path, controller_cmd):
        # Get the framework file system handler
        self._fs = FileSystem.get_instance()
        # Logger
        self._log = Logger.get_instance()
        # Controller's parameters
        self._path = controller_path
        self._cmd = controller_cmd
        # The controller process
        self._controller_process = None

    '''
    Start the controller.
    '''
    def start(self):
        self._log.debug(self.__class__.__name__, 'Going into the controller\'s folder.')
        self._fs.cd(self._path)
        self._log.debug(self.__class__.__name__, 'Starting the controller.')
        self._controller_process = Popen(self._cmd, shell=True, stdout=PIPE, stderr=PIPE)
        self._log.info(self.__class__.__name__, 'Controller has been correctly started.')

    '''
    Stop the controller.
    '''
    def stop(self):
        self._log.info(self.__class__.__name__, 'Stopping controller.')
        # Create a psutil.Process starting from the pid
        process = psutil.Process(self._controller_process.pid)
        self._log.debug(self.__class__.__name__, 'All child have been kept.')
        # Get all child' PID
        child_pid = process.get_children(recursive=True)
        self._log.debug(self.__class__.__name__, 'Starting to kill each children.')
        # Kill each children
        for pid in child_pid:
            os.kill(pid.pid, signal.SIGTERM)
        self._log.debug(self.__class__.__name__, 'Killing controller process.')
        # Finally, kill controller process
        self._controller_process.kill()
        self._log.info(self.__class__.__name__, 'Controller has been correctly stopped.')
