import ConfigParser
from xml.dom import minidom
import subprocess
from subprocess import PIPE

import time

from model.configurator import Configurator
from services.vpn.vpn import VirtualPrivateNetwork, Site, Host, Link
from utils.generator import AddressGenerator
from utils.process import Process
from utils.template import FactoryTemplate

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
        # The name of this class
        self._name = self.__class__.__name__
        # The factory to create protocol specific template
        self._factory_template = FactoryTemplate.get_instance()

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
        # The process used for the different actions
        process = Process()

        # Configuring each node
        for node in overlay.get_nodes().values():
            self._configure_zebra(node, process)
            self._configure_ospf(node, process)
            if node.get_role() == 'PE':
                self._configure_bgp(node, scenario, process)
            # Start all protocols
            self._start_protocols(node, process)

        # time.sleep(30)
        self._attach_customers(scenario, overlay, process)

        self._log.info(self.__class__.__name__, 'Configuration has been correctly created.')

    '''
    Generating Zebra configuration.
    '''

    def _configure_zebra(self, node, process):
        # Creating and copy Zebra configuration file
        self._log.debug(self.__class__.__name__, 'Creating the Zebra configuration file.')
        zebra_template = self._factory_template.create_zebra_template()
        zebra_template.generate()
        self._log.debug(self.__class__.__name__, 'Zebra configuration file has been successfully created.')

        self._log.debug(self.__class__.__name__, 'Copying the Zebra configuration file into the Docker instance.')
        zebra_cfg_file = self._fs.join(self._fs.get_tmp_folder(), 'zebra.conf')
        cmd_zebra = 'sudo docker cp %s %s:/etc/quagga/' % (zebra_cfg_file, node.get_name())
        process.execute(cmd_zebra)
        process.communicate()
        # Remove the file
        # self._fs.delete(zebra_cfg_file.get_path())
        self._log.debug(self.__class__.__name__,
                        'Zebra configuration file has been successfully deleted from temporary folder.')

        # Do the same for Zebra daemons file
        self._log.debug(self.__class__.__name__,
                        'Copying the Zebra daemons configuration file into the Docker instance.')
        zebra_daemons_cfg_file = self._fs.join(self._fs.get_tmp_folder(), 'daemons')
        cmd_zebra_daemons = 'sudo docker cp %s %s:/etc/quagga/' % (zebra_daemons_cfg_file, node.get_name())
        process.execute(cmd_zebra_daemons)
        process.communicate()
        # Remove the file
        # self._fs.delete(zebra_daemons_cfg_file)
        self._log.debug(self.__class__.__name__,
                        'Zebra daemons configuration file has been successfully deleted from temporary folder.')

        self._log.debug(self.__class__.__name__, 'Zebra has been successfully configured on %s.', node.get_name())

    '''
    Generating OSPF configuration.
    '''

    def _configure_ospf(self, node, process):
        # Creating and copy Zebra configuration file
        self._log.debug(self.__class__.__name__, 'Creating the OSPF configuration file.')
        ospf_template = self._factory_template.create_ospf_template(node.get_subnets())
        ospf_template.generate()
        self._log.debug(self.__class__.__name__, 'OSPF configuration file has been successfully created.')
        self._log.debug(self.__class__.__name__, 'Copying the OSPF configuration file into the Docker instance.')
        ospf_cfg_file = self._fs.join(self._fs.get_tmp_folder(), 'ospfd.conf')
        cmd_ospf = 'sudo docker cp %s %s:/etc/quagga/' % (ospf_cfg_file, node.get_name())
        process.execute(cmd_ospf)
        process.communicate()
        # Remove the file
        # self._fs.delete(ospf_cfg_file)
        self._log.debug(self.__class__.__name__,
                        'OSPF configuration file has been successfully deleted from temporary folder.')
        self._log.debug(self.__class__.__name__, 'OSPF has been successfully configured on %s.', node.get_name())

    '''
    Generating OSPF configuration.
    '''

    def _configure_bgp(self, node, scenario, process):
        # In order to configure BGP on each PE, first of all, take all neighbors of a given PE
        neighbors = []
        # For each vpn, if node is a PE of the vpn, then take the remote PE and add it to the list of the neighbors
        for vpn in scenario.get_vpns().values():
            if vpn.has_site_with_pe(node):
                # In neighbors list, add only the loopback
                neighbors.append(vpn.get_remote_pe(node).get_loopback())
        self._log.debug(self.__class__.__name__, 'Neighbors\' loopback addresses have been successfully acquired.')

        # Creating and copy GoBGP configuration file
        self._log.debug(self.__class__.__name__, 'Creating the GoBGP configuration file.')
        gobgp_template = self._factory_template.create_gobgp_template(node.get_loopback(), neighbors)
        gobgp_template.generate()
        self._log.debug(self.__class__.__name__, 'GoBGP configuration file has been successfully created.')
        self._log.debug(self.__class__.__name__, 'Copying the GoBGP configuration file into the Docker instance.')
        gobgp_cfg_file = self._fs.join(self._fs.get_tmp_folder(), 'gobgp.conf')
        cmd_gobgp = 'sudo docker cp %s %s:/etc/quagga/' % (gobgp_cfg_file, node.get_name())
        process.execute(cmd_gobgp)
        process.communicate()
        # Remove the file
        # self._fs.delete(ospf_cfg_file)
        self._log.debug(self.__class__.__name__,
                        'GoBGP configuration file has been successfully deleted from temporary folder.')
        self._log.debug(self.__class__.__name__, 'GoBGP has been successfully configured on %s.', node.get_name())

    '''
    Starts all protocols on the node.
    '''

    def _start_protocols(self, node, process):
        # Start OSPF
        # If node is a PE, then start BGP
        if node.get_role() == 'PE':
            pass
        pass

    '''
    Connect customer to the PE
    '''

    def _attach_customers(self, scenario, overlay, process):
        # Configuring BagPipeBGP on each host
        for vpn in scenario.get_vpns().values():
            # Get hosts
            hosts = vpn.get_hosts()
            for host in hosts.values():
                # Host's IP address is always in position 2 in the subnet assigned to the bridge connecting the host
                # with the PE
                host_ip = list(overlay.get_host_link(host).get_subnet())[2]
                self._log.debug(self.__class__.__name__, 'Creating the BagPipeBGP configuration file.')
                bagpipebgp_template = self._factory_template.create_bagpipebgp_template(host_ip, list(overlay.get_host_link(host).get_subnet())[3])
                bagpipebgp_template.generate()
                self._log.debug(self.__class__.__name__, 'BAgPipeBGP configuration file has been successfully created.')
                self._log.debug(self.__class__.__name__,
                                'Copying the BagPipeBGP configuration file into the Docker instance.')
                bagpipebgp_cfg_file = self._fs.join(self._fs.get_tmp_folder(), 'bgp.conf')
                cmd_bagpipebgp = 'sudo docker cp %s %s:/etc/quagga/' % (bagpipebgp_cfg_file, host.get_name())
                process.execute(cmd_bagpipebgp)
                process.communicate()
                # Remove the file
                # self._fs.delete(ospf_cfg_file)
                self._log.debug(self.__class__.__name__,
                                'BagPipeBGP configuration file has been successfully deleted from temporary folder.')
                self._log.debug(self.__class__.__name__, 'BagPipeBGP has been successfully configured on %s.',
                                host.get_name())

                # Start the protocol

                # Attach the host

        # for host in overlay.get_hosts().values():
        #     print '#######################', host, list(overlay.get_host_link(host).get_subnet())[2]
        # for node in overlay.get_nodes().values():
        #     if node.get_name() == 'WestP':
        #         cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
        #                        '--ip 192.168.10.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
        #                        node.get_name()
        #     else:
        #         cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
        #                        '--ip 192.168.11.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
        #                        node.get_name()
        #     self._log.info(self.__class__.__name__, 'Attaching client to %s.', node.get_name())
        #     # Attaching customer
        #     subprocess.Popen(cmd_customer, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        #     self._log.debug(self.__class__.__name__, 'Client has been successfully attached to %s.', node.get_name())

            # def configure(self, overlay, scenario):
            #     self._log.info(self.__class__.__name__, 'Starting to create the configuration.')
            #
            #     # Generating all configuration file for BagPipeBGP, GoBGP and OSPF
            #     # Copying all configuration files into the docker instances
            #     # Executing all routing daemons (OSPF on all nodes and GoBGP and BagPipeBGP on PE)
            #     for node in overlay.get_nodes().values():
            #
            #         self._log.info(self.__class__.__name__, 'Creating the Zebra configuration file.')
            #         confs = self._fs.join(self._fs.get_tmp_folder(), 'confs')
            #         cmd_zebra = 'sudo docker cp %s/zebra.conf %s:/etc/quagga/' % (confs, node.get_name())
            #         subprocess.Popen(cmd_zebra, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #         self._log.debug(self.__class__.__name__, 'Zebra configuration file has been successfully created.')
            #
            #         self._log.info(self.__class__.__name__, 'Creating the Quagga configuration file.')
            #         confs = self._fs.join(self._fs.get_tmp_folder(), 'confs')
            #         cmd_quagga = 'sudo docker cp %s/daemons %s:/etc/quagga/' % (confs, node.get_name())
            #         subprocess.Popen(cmd_quagga, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #         self._log.debug(self.__class__.__name__, 'Quagga configuration file has been successfully created.')
            #
            #         # Switch to specific node configuration folder
            #         node_folder = self._fs.join(self._fs.get_tmp_folder(), 'confs', node.get_name())
            #
            #         if node.get_role() == 'PE':
            #             self._log.info(self.__class__.__name__, 'Creating the GoBGP configuration file.')
            #             # Copying all file in the current directory into the container
            #             cmd_gobgp = 'sudo docker cp %s/gobgp.conf %s:/etc/quagga/' % (node_folder, node.get_name())
            #             subprocess.Popen(cmd_gobgp, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #             self._log.debug(self.__class__.__name__, 'GoBGP configuration file has been successfully created.')
            #
            #             self._log.info(self.__class__.__name__, 'Starting GoBGP routing daemon.')
            #             # Starting GoBGP
            #             cmd_gobgp_daemon = 'sudo docker exec -d %s /root/go/bin/gobgpd -f /etc/quagga/gobgp.conf' % node.get_name()
            #             subprocess.Popen(cmd_gobgp_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #             self._log.debug(self.__class__.__name__, 'GoBGP routing daemon has been successfully started.')
            #
            #             self._log.info(self.__class__.__name__, 'Creating the BagPipiBGP configuration file.')
            #             cmd_bagpipebgp = 'sudo docker cp %s/bgp.conf %s:/etc/bagpipe-bgp/' % (node_folder, node.get_name())
            #             subprocess.Popen(cmd_bagpipebgp, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #             self._log.debug(self.__class__.__name__, 'BagPipeBGP configuration file has been successfully created.')
            #
            #             self._log.info(self.__class__.__name__, 'Starting BagPipeBGP routing daemon.')
            #             # Starting BagPipeBGP
            #             cmd_bagpipebgp_daemon = 'sudo docker exec -d %s service bagpipe-bgp start' % node.get_name()
            #             subprocess.Popen(cmd_bagpipebgp_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #             self._log.debug(self.__class__.__name__, 'BagPipeBGP routing daemon has been successfully started.')
            #
            #         self._log.info(self.__class__.__name__, 'Creating the OSPF configuration file.')
            #         cmd_ospf = 'sudo docker cp %s/ospfd.conf %s:/etc/quagga/' % (node_folder, node.get_name())
            #         subprocess.Popen(cmd_ospf, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #         self._log.debug(self.__class__.__name__, 'OSPF configuration file has been successfully created.')
            #
            #         self._log.info(self.__class__.__name__, 'Starting OSPF routing daemon.')
            #         # Starting OSPF
            #         cmd_ospf_daemon = 'sudo docker exec -d %s /etc/init.d/quagga start' % node.get_name()
            #         subprocess.Popen(cmd_ospf_daemon, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #         self._log.debug(self.__class__.__name__, 'OSPF routing daemon has been successfully started.')
            #
            #     time.sleep(30)
            #     self._attach_customers(overlay)
            #
            #     self._log.info(self.__class__.__name__, 'Configuration has been correctly created.')
            #
            # def _attach_customers(self, overlay):
            #     for node in overlay.get_nodes().values():
            #         if node.get_name() == 'WestP':
            #             cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
            #                            '--ip 192.168.10.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
            #                            node.get_name()
            #         else:
            #             cmd_customer = 'sudo docker exec -d %s bagpipe-rest-attach --attach --port netns ' \
            #                            '--ip 192.168.11.1 --network-type evpn --vpn-instance-id test --rt 64512:79' % \
            #                            node.get_name()
            #         self._log.info(self.__class__.__name__, 'Attaching client to %s.', node.get_name())
            #         # Attaching customer
            #         subprocess.Popen(cmd_customer, shell=True, stdout=PIPE, stderr=PIPE).communicate()
            #         self._log.debug(self.__class__.__name__, 'Client has been successfully attached to %s.', node.get_name())
