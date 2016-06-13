import os
import shutil
import subprocess
from subprocess import PIPE

from model.scenario import Scenario
from services.vpn.vpn import VirtualPrivateNetwork, Host, Link, Site
from utils.generator import AddressGenerator

"""
This class implements the scenario for the VPN service. In this case, scenario simply consists of the number of VPNs in
the network
"""


class VpnScenario(Scenario):
    def __init__(self, scenario_params):
        Scenario.__init__(self)
        self._name = self.__class__.__name__
        # The number of the VPNs in the network
        self._number_of_vpns = int(scenario_params['number_of_vpns'])
        # All VPNs in the network
        self._vpns = {}

    def __repr__(self):
        return 'Scenario[name=%s, #VPNs=%s]' % (self._name, self._number_of_vpns)

    '''
    Return the name of the scenario
    '''

    def get_name(self):
        return self._name

    '''
    Return all VPNs in the scenario
    '''

    def get_vpns(self):
        return self._vpns

    '''
    Create the scenario
    '''

    def create(self, overlay):
        # Create the VPNs
        for i in range(0, self._number_of_vpns):
            name = 'vpn-' + str(i)
            vpn = VirtualPrivateNetwork(name)
            self._log.debug(self.__class__.__name__, 'VPN %s has been created', name)
            # Take two random PEs
            pes = overlay.get_two_random_pes()
            # Create sites
            self._log.debug(self.__class__.__name__, 'Starting to creates the sites for VPN %s.', vpn.get_name())
            vpn.add_site(self._create_site(vpn, pes[0], overlay, i))
            vpn.add_site(self._create_site(vpn, pes[1], overlay, i))
            self._log.debug(self.__class__.__name__, 'Sites have been successfully created.')

            # Add VPN to the map of VPNs
            self._vpns[name] = vpn
        self._log.info(self.__class__.__name__, 'All VPNs have been successfully created.')

    '''
    Create a site for a VPN
    '''

    def _create_site(self, vpn, pe, overlay, i):
        # IP generator
        ip_generator = AddressGenerator.get_instance()
        # First of all, create an host for this site
        # IP addresses for the hosts
        self._log.debug(self.__class__.__name__, 'Starting to create a new site for VPN %s.', vpn.get_name())
        self._log.debug(self.__class__.__name__, 'Generating IP address for the host.')
        h_ip = ip_generator.generate_ip_address()
        host = Host('h' + str(i) + '_' + pe.get_name(), h_ip)
        self._log.debug(self.__class__.__name__, 'Host %s has been successfully generated.', host.get_name())
        # Add host to the overlay
        overlay.add_host(host)
        self._log.debug(self.__class__.__name__, 'Host %s has been added to the overlay.', host.get_name())
        host.set_pe(pe)
        self._log.debug(self.__class__.__name__, 'Host %s has been connected to its PE.', host.get_name())
        # Add this host to the VPN
        vpn.add_host(host)
        self._log.debug(self.__class__.__name__, 'Host %s has been added to the VPN %s.',
                        host.get_name(), vpn.get_name())
        # Create a new interface for this switch
        pe_interface_name = pe.create_interface()
        self._log.debug(self.__class__.__name__, 'A new interface for %s has been successfully created.', pe.get_name())
        # Being a PE node, also set the loopback address
        pe.set_loopback(ip_generator.get_next_loopback())
        self._log.debug(self.__class__.__name__, 'A loopback address has been successfully associated to switch %s.',
                        pe.get_name())
        # Finally, create a Link object between host and PE and add it to the overlay
        link = Link(host, pe, host.get_interface_name(), pe_interface_name, ip_generator.get_next_subnet())
        self._log.debug(self.__class__.__name__, 'Link %s has been created.', link)
        overlay.add_link(link)
        self._log.debug(self.__class__.__name__,
                        'Link %s created and added to %s', link, overlay.get_name())
        site = Site(vpn, pe, pe_interface_name, ip_generator.get_subnet_from_ip(host.get_ip()))
        self._log.info(self.__class__.__name__, 'Site %s has been successfully created.', site)

        return site

    '''
    Destroy the scenario
    '''

    def destroy(self):
        pass


# """
# This class models a scenario for Rm3SdnVpn alternative. It has in charge the task of running the controller.
# """
#
#
# class Rm3SdnVpnScenario(Scenario):
#     def __init__(self, **kwargs):
#         Scenario.__init__(self)
#         # The name of the scenario
#         self._name = self.__class__.__name__
#         # Take params from kwargs
#         params = kwargs.get('scenario')
#         # Controller (actually, the path to the controller. ryu-manager is required.)
#         self._controller_path = params['controller_path']
#         # Command to run controller
#         self._controller_cmd = params['controller_cmd']
#         # System and VPN's configuration files
#         self._system_conf_file = None
#         self._vpns_conf_file = None
#         # Reference to the controller
#         self._controller = None
#
#     def __repr__(self):
#         return 'Rm3SdnVpnScenario[#VPNs=%s, controller=%s]' % (self._number_of_vpns, self._controller_path)
#
#     '''
#     Return the name of this scenario.
#     '''
#
#     def get_name(self):
#         return self._name
#
#     '''
#     Return the number of VPNs declared in this scenario.
#     '''
#
#     def get_number_of_vpns(self):
#         return self._number_of_vpns
#
#     '''
#     Return the VPNs in the scenario
#     '''
#
#     def get_vpns(self):
#         return self._vpns
#
#     '''
#     Return the path in which the controller is placed.
#     '''
#
#     def get_controller_path(self):
#         return self._controller_path
#
#     '''
#     Return the name of the command running the controller.
#     '''
#
#     def get_controller_cmd(self):
#         return self._controller_cmd
#
#     '''
#     This method allows the creation of this scenario.
#     '''
#
#     def create(self):
#         self._log.info(self.__class__.__name__, 'Preparing to start the scenario %s.', self._name)
#         # Before starting controller, copy VPNs configuration file inside the controller conf folder.
#         # In particular, copy tmp/system.conf and tmp/vpns.xml into controller conf folder.
#         # Take the files
#         self._log.debug(self.__class__.__name__, 'Taking the controller\'s configuration files.')
#         self._system_conf_file = self._fs.get_tmp_folder() + '/system.conf'
#         self._vpns_conf_file = self._fs.get_tmp_folder() + '/vpns.xml'
#         # Copy files into controller path (move into FileSystem, the class that handles all application file system
#         # aspects).
#         self._log.debug(self.__class__.__name__,
#                         'Coping the controller\'s configuration files into controller\'s path.')
#         # TODO: move this instructions into FileSystem class
#         shutil.copy(self._system_conf_file, os.path.expanduser(self._controller_path) + 'conf/')
#         shutil.copy(self._vpns_conf_file, os.path.expanduser(self._controller_path) + 'conf/vpns/')
#         # Essentially, this method has in charge the task of running controller
#         self._log.debug(self.__class__.__name__, 'Starting controller.')
#         self._controller = ControllerStarter(self._controller_path, self._controller_cmd)
#         self._controller.start()
#         self._log.info(self.__class__.__name__, 'Controller has been correctly started.')
#
#     '''
#     This method destroys the scenario previously created.
#     '''
#
#     def destroy(self):
#         self._log.debug(self.__class__.__name__, 'Stopping scenario %s.', self._name)
#         # Remove files from tmp dir
#         self._log.debug(self.__class__.__name__, 'Removing configuration\'s files from temporary folder.')
#         self._fs.delete(self._system_conf_file)
#         self._fs.delete(self._vpns_conf_file)
#         self._log.debug(self.__class__.__name__, 'Stopping the controller.')
#         # Stop the controller
#         self._controller.stop()
#         self._log.info(self.__class__.__name__, 'Scenario %s has been correctly stopped.', self._name)
#
#
# """
# This class models a scenario for Rm3SdnVpn alternative. It has in charge the task of running the controller.
# """
#
#
# class MplsBgpVpnScenario(Scenario):
#     def __init__(self, **kwargs):
#         Scenario.__init__(self)
#         # The name of the scenario
#         self._name = self.__class__.__name__
#         # Take params from kwargs
#         params = kwargs.get('scenario')
#         # Number of VPNs
#         self._number_of_vpns = int(params['number_of_vpns'])
#
#     def __repr__(self):
#         return 'MplsBpgVpnScenario[#VPNs=%s]' % (self._number_of_vpns)
#
#     '''
#     Return the name of this scenario.
#     '''
#
#     def get_name(self):
#         return self._name
#
#     '''
#     Return the number of VPNs declared in this scenario.
#     '''
#
#     def get_number_of_vpns(self):
#         return self._number_of_vpns
#
#     '''
#     This method allows the creation of this scenario.
#     '''
#
#     def start(self):
#         self._log.info(self.__class__.__name__, 'Preparing to start the scenario %s.', self._name)
#         # Put here the configuration of all docker instance, for example adding network interfaces
#         # Invoke pos.sh
#         self._fs.join(self._fs.get_tmp_folder(), 'poc.sh')
#         subprocess.Popen(self._fs.get_current_working_folder(), shell=True, stdout=PIPE, stderr=PIPE)
#         self._log.info(self.__class__.__name__, 'Scenario %s. has been correctly started.', self._name)
#
#     '''
#     This method destroys the scenario previously created.
#     '''
#
#     def destroy(self):
#         self._log.debug(self.__class__.__name__, 'Stopping scenario %s.', self._name)
#         # No specific actions for this scenario
#         # Invoke clean.sh
#         self._fs.join(self._fs.get_tmp_folder(), 'clean.sh')
#         subprocess.Popen(self._fs.get_current_working_folder(), shell=True, stdout=PIPE, stderr=PIPE)
#         self._log.info(self.__class__.__name__, 'Scenario %s has been correctly stopped.', self._name)
