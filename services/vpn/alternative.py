import os
import shutil

from loader.env.controller import ControllerStarter
from model.alternative import Alternative

from services.vpn.configurator import Rm3SdnVpnConfigurator, MplsBgpVpnConfigurator
from services.vpn.overlay import VpnOverlay
from services.vpn.vpn import Switch, Link

"""
This class implements the rm3-sdn-vpn's alternative.
"""


class Rm3SdnVpnAlternative(Alternative):
    def __init__(self, name, **kwargs):
        Alternative.__init__(self, name)
        # This is an instance of services.vpn.configurator.Rm3SdnVpnConfigurator
        self._configurator = Rm3SdnVpnConfigurator()
        # Parameters
        params = kwargs.get('scenario')
        # To start the controller
        self._controller = None
        # Controller path
        self._controller_path = params['controller_path']
        # Controller executable file
        self._controller_cmd = params['controller_cmd']

    def __repr__(self):
        return 'Alternative[name=%s, metrics=%s]' % (self._name, self._metrics)

    '''
    Deploy the alternative into the scenario associated to the service which this alternative belongs to.
    '''

    def deploy(self, overlay, scenario):
        self._log.debug(self.__class__.__name__, 'Starting to configure the alternative.')
        # Generate the configuration file
        self._configurator.configure(overlay, scenario)
        self._log.debug(self.__class__.__name__, 'Passing the configuration files to the controller.')
        # Copy the configuration files into the controller configuration folder
        # system.conf file will be moved into controller_path/conf folder
        self._fs.copy(self._fs.join(self._fs.get_tmp_folder(), self._configurator.get_system_config_file()),
                      self._fs.join(self._controller_path, 'conf'))
        # vpns.xml file will be moved into controller_path/conf/vpns folder
        self._fs.copy(self._fs.join(self._fs.get_tmp_folder(), self._configurator.get_vpns_config_file()),
                      self._fs.join(self._controller_path, 'conf', 'vpns'))
        # Start the controller
        self._log.debug(self.__class__.__name__, 'Preparing to start the controller.')
        self._controller = ControllerStarter(self._controller_path, self._controller_cmd)
        self._controller.start()
        self._log.info(self.__class__.__name__, 'Alternative %s has been successfully deployed.', self._name)

    '''
    Destroy this alternative.
    '''

    def destroy(self):
        # Stop the controller
        self._log.debug(self.__class__.__name__, 'Preparing to stop the controller.')
        self._controller.stop()
        self._log.info(self.__class__.__name__, 'Alternative %s has been successfully stopped.')

    '''
    Return the configurator associated to this alternative.
    '''

    def get_configurator(self):
        return self._configurator


"""
This class implements the mpls-bgp-vpn's alternative.
"""


class MplsBgpVpnAlternative(Alternative):
    def __init__(self, name, *args, **kwargs):
        Alternative.__init__(self, name)
        # This is an instance of services.vpn.configurator.MplsBgpVpnConfigurator
        self._configurator = MplsBgpVpnConfigurator()

    def __repr__(self):
        return 'Alternative[name=%s, metrics=%s]' % (self._name, self._metrics)

    '''
    Deploy the alternative into the scenario associated to the service which this alternative belongs to.
    '''

    def deploy(self, overlay, scenario):
        self._log.debug(self.__class__.__name__, 'Starting to configure the alternative.')
        # Generate the configuration file
        # self._configurator.configure(overlay, scenario)
        self._log.info(self.__class__.__name__, 'Alternative %s has been successfully deployed.', self._name)

    '''
    Destroy this alternative.
    '''

    def destroy(self):
        pass

    '''
    Return the configurator associated to this alternative.
    '''

    def get_configurator(self):
        return self._configurator
