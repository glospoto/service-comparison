import ConfigParser
from xml.dom import minidom
import subprocess
from subprocess import PIPE

import time

from model.configurator import Configurator
from services.vpn.vpn import VirtualPrivateNetwork, Site, Host, Link
from utils.generator import AddressGenerator

"""
This class model the configuration management for Rm3Sdn alternative
"""


class Rm3SdnVpnConfigurator(Configurator):
    def __init__(self):
        Configurator.__init__(self)
        self._name = self.__class__.__name__
        # References to object for handling configuration files
        self._system_config = ConfigParser.ConfigParser()
        self._vpns_config = minidom.Document()
        # Files names
        self.__SYS_CONG_FILE_NAME = 'system.conf'
        self.__VPNS_FILE_NAME = 'vpns.xml'

    def __repr__(self):
        return '%s' % self._name

    '''
    Return the name of this configurator.
    '''

    def get_name(self):
        return self._name

    '''
    Return the system file name for the rm3-sdn-vpn alternative
    '''

    def get_system_config_file(self):
        return self.__SYS_CONG_FILE_NAME

    '''
    Return the VPNs configuration file name for the rm3-sdn-vpn alternative
    '''

    def get_vpns_config_file(self):
        return self.__VPNS_FILE_NAME

    '''
    This method has in charge the task of writing the configuration files for RM3 SDN VPN controller.
    '''

    def configure(self, overlay, scenario):
        self._log.debug(self.__class__.__name__, 'Starting to create the configuration files for the controller.')
        self._write_system_configuration(scenario)
        self._write_vpns_configuration(overlay, scenario)
        self._log.info(self.__class__.__name__, 'Configuration files have been successfully created.')

    '''
    This method writes the system.conf VPN's controller configuration file.
    '''

    def _write_system_configuration(self, scenario):
        self._log.debug(self.__class__.__name__, 'Creating the %s file for VPN controller.', self.__SYS_CONG_FILE_NAME)
        # This method has in charge the task of creating the system configuration file. A system configuration file
        # contains the path to the vpns configuration file and the list of policy per VPN
        sys_conf_file_str = self._fs.join(self._fs.get_tmp_folder(), self.__SYS_CONG_FILE_NAME)
        sys_conf_file = open(sys_conf_file_str, 'w')
        self._log.debug(self.__class__.__name__, 'Adding System section to the the %s file.', self.__SYS_CONG_FILE_NAME)
        self._system_config.add_section('System')
        self._system_config.set('System', 'vpn-config-file',
                                'conf/vpns/' + self.__VPNS_FILE_NAME)  # VPN conf file; see below
        self._log.debug(self.__class__.__name__,
                        'Adding Policies section to the the %s file.', self.__SYS_CONG_FILE_NAME)
        self._system_config.add_section('Policies')
        # For each VPN, create an entry with vpn name as key, and policy as value
        self._log.debug(self.__class__.__name__, 'Adding Policy for VPN in the %s file.', self.__SYS_CONG_FILE_NAME)
        for vpn in scenario.get_vpns().keys():
            self._system_config.set('Policies', vpn, 'ShortestPath')
        self._log.debug(self.__class__.__name__, 'Writing %s in the framework temporary folder.',
                        self.__SYS_CONG_FILE_NAME)
        # Write the file into tmp directory
        self._system_config.write(sys_conf_file)
        self._log.info(self.__class__.__name__, '%s has been successfully generated.', self.__SYS_CONG_FILE_NAME)

    '''
    This method writes the XML VPN's configuration file.
    '''

    def _write_vpns_configuration(self, overlay, scenario):
        self._log.debug(self.__class__.__name__, 'Creating the %s file for VPN controller.', self.__VPNS_FILE_NAME)
        # This method has in charge the task of creating the VPNs configuration file. A VPN configuration file is a
        # XML file which contains the list of all mappings between datapath id and datapath name and all VPN
        # configuration (VPNs, sites, customer, ...). Assumption: this file will be always called vpns.xml (this
        # assumption is important for generating system.conf file)
        vpns_conf_file_str = self._fs.join(self._fs.get_tmp_folder(), self.__VPNS_FILE_NAME)
        self._log.debug(self.__class__.__name__, 'Creating the root for %s file.', self.__VPNS_FILE_NAME)
        root = self._vpns_config.createElement('vpns')
        self._vpns_config.appendChild(root)
        # Add datapahts' list
        dps = overlay.get_nodes()
        self._log.debug(self.__class__.__name__, 'Adding datapaths to the %s file.', self.__VPNS_FILE_NAME)
        for dp in dps.values():
            dp_element = self._vpns_config.createElement('datapath')
            dp_element.setAttribute('name', dp.get_name())
            dp_element.setAttribute('dpid', str(dp.get_dpid()))
            root.appendChild(dp_element)
        # Add VPNs
        self._log.debug(self.__class__.__name__, 'Adding the VPNs specification in %s file.', self.__VPNS_FILE_NAME)
        for vpn in scenario.get_vpns().values():
            vpn_element = self._vpns_config.createElement('vpn')
            vpn_element.setAttribute('name', vpn.get_name())
            sites = vpn.get_sites()
            self._log.debug(self.__class__.__name__, 'Adding site in the %s file for VPN %s.',
                            self.__VPNS_FILE_NAME, vpn.get_name())
            for site in sites:
                site_element = self._vpns_config.createElement('network')
                site_element.setAttribute('subnet', str(site.get_network()))
                site_element.setAttribute('pe', site.get_pe().get_name())
                site_element.setAttribute('port', site.get_port())
                site_element.setAttribute('nat', '')
                vpn_element.appendChild(site_element)
            self._log.debug(self.__class__.__name__, 'All sites have been added to %s file.', self.__VPNS_FILE_NAME)
            root.appendChild(vpn_element)
        self._log.debug(self.__class__.__name__, 'All VPNs have been added to %s file.', self.__VPNS_FILE_NAME)

        xml_str = self._vpns_config.toprettyxml(indent="  ", encoding='UTF-8')
        with open(vpns_conf_file_str, 'w') as f:
            f.write(xml_str)
        self._log.info(self.__class__.__name__, '%s has been successfully generated.', self.__VPNS_FILE_NAME)


"""
This class model the configuration management for Rm3Sdn alternative
"""


class MplsBgpVpnConfigurator(Configurator):
    def __init__(self):
        Configurator.__init__(self)
        self._name = self.__class__.__name__

    def __repr__(self):
        return '%s' % self._name

    '''
    Return the name of this configurator.
    '''

    def get_name(self):
        return self._name

    '''
    This method has in charge the task of writing the configuration files for RM3 SDN VPN controller.
    '''

    def configure(self, overlay, scenario):
        self._log.info(self.__class__.__name__, 'Starting to create the configuration.')

        # Generating all configuration file for BagPipeBGP, GoBGP and OSPF
        # Copying all configuration files into the docker instances
        # Executing all routing daemons (OSPF on all nodes and GoBGP and BagPipeBGP on PE)
        for node in overlay.get_nodes().values():

            self._log.info(self.__class__.__name__, 'Creating the Zebra configuration file.')
            confs = self._fs.join(self._fs.get_tmp_folder(), 'confs')
            cmd_zebra = 'sudo docker cp %s/zebra.conf %s:/etc/quagga/' % (confs, node.get_name())
            subprocess.Popen(cmd_zebra, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            self._log.debug(self.__class__.__name__, 'Zebra configuration file has been successfully created.')

            self._log.info(self.__class__.__name__, 'Creating the Quagga configuration file.')
            confs = self._fs.join(self._fs.get_tmp_folder(), 'confs')
            cmd_quagga = 'sudo docker cp %s/daemons %s:/etc/quagga/' % (confs, node.get_name())
            subprocess.Popen(cmd_quagga, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            self._log.debug(self.__class__.__name__, 'Quagga configuration file has been successfully created.')

            # Switch to specific node configuration folder
            node_folder = self._fs.join(self._fs.get_tmp_folder(), 'confs', node.get_name())

            if node.get_role() == 'PE':
                self._log.info(self.__class__.__name__, 'Creating the GoBGP configuration file.')
                # Copying all file in the current directory into the container
                cmd_gobgp = 'sudo docker cp %s/gobgp.conf %s:/etc/quagga/' % (node_folder, node.get_name())
                subprocess.Popen(cmd_gobgp, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                self._log.debug(self.__class__.__name__, 'GoBGP configuration file has been successfully created.')

                self._log.info(self.__class__.__name__, 'Starting GoBGP routing daemon.')
                # Starting GoBGP
                cmd_gobgp_daemon = 'sudo docker exec -d %s /root/go/bin/gobgpd -f /etc/quagga/gobgp.conf' % node.get_name()
                subprocess.Popen(cmd_gobgp_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                self._log.debug(self.__class__.__name__, 'GoBGP routing daemon has been successfully started.')

                self._log.info(self.__class__.__name__, 'Creating the BagPipiBGP configuration file.')
                cmd_bagpipebgp = 'sudo docker cp %s/bgp.conf %s:/etc/bagpipe-bgp/' % (node_folder, node.get_name())
                subprocess.Popen(cmd_bagpipebgp, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                self._log.debug(self.__class__.__name__, 'BagPipeBGP configuration file has been successfully created.')

                self._log.info(self.__class__.__name__, 'Starting BagPipeBGP routing daemon.')
                # Starting BagPipeBGP
                cmd_bagpipebgp_daemon = 'sudo docker exec -d %s service bagpipe-bgp start' % node.get_name()
                subprocess.Popen(cmd_bagpipebgp_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                self._log.debug(self.__class__.__name__, 'BagPipeBGP routing daemon has been successfully started.')

            self._log.info(self.__class__.__name__, 'Creating the OSPF configuration file.')
            cmd_ospf = 'sudo docker cp %s/ospfd.conf %s:/etc/quagga/' % (node_folder, node.get_name())
            subprocess.Popen(cmd_ospf, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            self._log.debug(self.__class__.__name__, 'OSPF configuration file has been successfully created.')

            self._log.info(self.__class__.__name__, 'Starting OSPF routing daemon.')
            # Starting OSPF
            cmd_ospf_daemon = 'sudo docker exec -d %s /etc/init.d/quagga start' % node.get_name()
            subprocess.Popen(cmd_ospf_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            self._log.debug(self.__class__.__name__, 'OSPF routing daemon has been successfully started.')

        time.sleep(30)
        self._attach_customers(overlay)

        self._log.info(self.__class__.__name__, 'Configuration has been correctly created.')

    def _attach_customers(self, overlay):
        for node in overlay.get_nodes().values():
            if node.get_name() == 'WestP':
                cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
                               '--ip 192.168.10.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
                               node.get_name()
            else:
                cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
                               '--ip 192.168.11.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
                               node.get_name()
            self._log.info(self.__class__.__name__, 'Attaching client to %s.', node.get_name())
            # Attaching customer
            subprocess.Popen(cmd_customer, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            self._log.debug(self.__class__.__name__, 'Client has been successfully attached to %s.', node.get_name())
