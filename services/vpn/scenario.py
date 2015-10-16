import os
import shutil

from loader.env.controller import ControllerStarter
from model.scenario import Scenario

"""
This class models a scenario for Rm3SdnVpn alternative. It has in charge the task of running the controller.
"""


class Rm3SdnVpnScenario(Scenario):
    def __init__(self, *args, **kwargs):
        Scenario.__init__(self)
        # The name of the scenario
        self._name = self.__class__.__name__
        # Take params from kwargs
        params = kwargs.get('scenario')
        # Number of VPNs
        self._number_of_vpns = int(params['number_of_vpns'])
        # Controller (actually, the path to the controller. ryu-manager is required.)
        self._controller_path = params['controller_path']
        # Command to run controller
        self._controller_cmd = params['controller_cmd']
        # System and VPN's configuration files
        self._system_conf_file = None
        self._vpns_conf_file = None
        # Reference to the controller
        self._controller = None

    def __repr__(self):
        return 'Rm3SdnVpnScenario[#VPNs=%s, controller=%s]' % (self._number_of_vpns, self._controller_path)

    '''
    Return the name of this scenario.
    '''
    def get_name(self):
        return self._name

    '''
    Return the number of VPNs declared in this scenario.
    '''
    def get_number_of_vpns(self):
        return self._number_of_vpns

    '''
    Return the path in which the controller is placed.
    '''
    def get_controller_path(self):
        return self._controller_path

    '''
    Return the name of the command running the controller.
    '''
    def get_controller_cmd(self):
        return self._controller_cmd

    '''
    This method allows the creation of this scenario.
    '''
    def start(self):
        self._log.info(self.__class__.__name__, 'Preparing to start the scenario %s.', self._name)
        # Before starting controller, copy VPNs configuration file inside the controller conf folder.
        # In particular, copy tmp/system.conf and tmp/vpns.xml into controller conf folder.
        # Take the files
        self._log.debug(self.__class__.__name__, 'Taking the controller\'s configuration files.')
        self._system_conf_file = self._fs.get_tmp_folder() + '/system.conf'
        self._vpns_conf_file = self._fs.get_tmp_folder() + '/vpns.xml'
        # Copy files into controller path (move into FileSystem, the class that handles all application file system
        # aspects).
        self._log.debug(self.__class__.__name__,
                        'Coping the controller\'s configuration files into controller\'s path.')
        # TODO: move this instructions into FileSystem class
        shutil.copy(self._system_conf_file, os.path.expanduser(self._controller_path) + 'conf/')
        shutil.copy(self._vpns_conf_file, os.path.expanduser(self._controller_path) + 'conf/vpns/')
        # Essentially, this method has in charge the task of running controller
        self._log.debug(self.__class__.__name__, 'Starting controller.')
        self._controller = ControllerStarter(self._controller_path, self._controller_cmd)
        self._controller.start()
        self._log.info(self.__class__.__name__, 'Controller has been correctly started.')

    '''
    This method destroys the scenario previously created.
    '''
    def destroy(self):
        self._log.debug(self.__class__.__name__, 'Stopping scenario %s.', self._name)
        # Remove files from tmp dir
        self._log.debug(self.__class__.__name__, 'Removing configuration\'s files from temporary folder.')
        self._fs.delete(self._system_conf_file)
        self._fs.delete(self._vpns_conf_file)
        self._log.debug(self.__class__.__name__, 'Stopping the controller.')
        # Stop the controller
        self._controller.stop()
        self._log.info(self.__class__.__name__, 'Scenario %s has been correctly stopped.', self._name)