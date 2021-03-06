import ConfigParser
from xml.dom import minidom

from model.configurator import Configurator
from services.vpn.vpn import VirtualPrivateNetwork, Site, Host, Link
from utils.generator import AddressGenerator


class Rm3SdnVpnConfigurator(Configurator):
    def __init__(self):
        Configurator.__init__(self)
        self._name = self.__class__.__name__
        # All created VPNs
        self._vpns = {}
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
    Return the map of all created VPNs.
    '''
    def get_vpns(self):
        return self._vpns

    '''
    This method has in charge the task of creating all VPNs defined using the configuration file.
    '''
    def create_vpns(self, overlay, number_of_vpns):
        self._log.info(self.__class__.__name__, 'Starting to configure the alternative.')
        for i in range(0, number_of_vpns):
            name = 'vpn-' + str(i)
            vpn = VirtualPrivateNetwork(name)
            self._log.debug(self.__class__.__name__, 'VPN %s has been created', name)
            # Take two random PEs
            pes = overlay.get_two_random_pes()
            # Create sites
            self._log.debug(self.__class__.__name__, 'Starting to creates the sites for VPN %s.', vpn.get_name())
            vpn.add_site(self._create_site(vpn, pes[0], overlay, i))
            vpn.add_site(self._create_site(vpn, pes[1], overlay, i))
            self._log.debug(self.__class__.__name__, 'Sites have been correctly created.')

            # Add VPN to the map of VPNs
            self._vpns[name] = vpn
        self._log.info(self.__class__.__name__, 'All VPNs have been created.')

    '''
    Private method used for creating a site to add to a VPN. This is made in accord to the model defined into
    services.vpn.vpn.py
    '''
    def _create_site(self, vpn, pe, overlay, i):
        # First of all, create an host for this site
        # IP addresses for the hosts
        self._log.debug(self.__class__.__name__, 'Starting to create a new site for VPN %s.', vpn.get_name())
        self._log.debug(self.__class__.__name__, 'Generating IP address for the host.')
        h_ip = AddressGenerator.generate_ip_address()
        host = Host('h' + str(i) + '_' + pe.get_name(), h_ip)
        self._log.debug(self.__class__.__name__, 'Host %s has been correctly generated.', host.get_name())
        # Add host to the overlay
        overlay.add_host(host)
        self._log.debug(self.__class__.__name__, 'Host %s has been added to the overlay.', host.get_name())
        host.set_pe(pe)
        self._log.debug(self.__class__.__name__, 'Host %s has been connected to its PE.', host.get_name())
        # Add this host to the VPN
        vpn.add_host(host)
        self._log.debug(self.__class__.__name__, 'Host %s has been added to the VPN %s.',
                        host.get_name(), vpn.get_name())
        pe.assign_interface_to_host(host)
        self._log.debug(self.__class__.__name__, 'Host %s has been assigned to a certain interface of PE %s.',
                        host.get_name(), pe.get_name())
        # Finally, create a Link object between host and PE and add it to the overlay
        link = Link(host, pe)
        self._log.debug(self.__class__.__name__, 'Link %s has been created.', link)
        overlay.add_link(link)
        self._log.debug(self.__class__.__name__,
                        'Link %s created and added to %s', link, overlay.get_name())

        return Site(vpn, pe, pe.get_interface_for_host(host), AddressGenerator.get_subnet_from_ip(host.get_ip()))

    '''
    This method has in charge the task of writing the configuration files for RM3 SDN VPN controller.
    '''
    def write_configurations(self, overlay):
        self._log.info(self.__class__.__name__, 'Starting to create the configuration file for the controller.')
        self._write_system_configuration()
        self._write_vpns_configuration(overlay)

    '''
    This method writes the system.conf VPN's controller configuration file.
    '''
    def _write_system_configuration(self):
        self._log.debug(self.__class__.__name__, 'Creating the %s file for VPN controller.', self.__SYS_CONG_FILE_NAME)
        # This method has in charge the task of creating the system configuration file. A system configuration file
        # contains the path to the vpns configuration file and the list of policy per VPN
        sys_conf_file_str = self._fs.join(self._fs.get_tmp_folder(), self.__SYS_CONG_FILE_NAME)
        sys_conf_file = open(sys_conf_file_str, 'w')
        self._log.debug(self.__class__.__name__, 'Adding System section to the the %s file.', self.__SYS_CONG_FILE_NAME)
        self._system_config.add_section('System')
        self._system_config.set('System', 'vpn-config-file',
                                'conf/vpns/' + self.__VPNS_FILE_NAME)   # VPN conf file; see below
        self._log.debug(self.__class__.__name__,
                        'Adding Policies section to the the %s file.', self.__SYS_CONG_FILE_NAME)
        self._system_config.add_section('Policies')
        # For each VPN, create an entry with vpn name as key, and policy as value
        self._log.debug(self.__class__.__name__, 'Adding Policy for VPN in the %s file.', self.__SYS_CONG_FILE_NAME)
        for vpn in self._vpns.keys():
            self._system_config.set('Policies', vpn, 'ShortestPath')
        self._log.debug(self.__class__.__name__, 'Writing %s in the framework temporary folder.',
                        self.__SYS_CONG_FILE_NAME)
        # Write the file into tmp directory
        self._system_config.write(sys_conf_file)
        self._log.info(self.__class__.__name__, '%s has been correctly generated.', self.__SYS_CONG_FILE_NAME)

    '''
    This method writes the XML VPN's configuration file.
    '''
    def _write_vpns_configuration(self, overlay):
        self._log.debug(self.__class__.__name__, 'Creating the %s file for VPN controller.', self.__VPNS_FILE_NAME)
        # This method has in charge the task of creating the VPNs configuartion file. A VPN configuration file is a
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
        for vpn in self._vpns.values():
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
        self._log.info(self.__class__.__name__, '%s has been correctly generated.', self.__VPNS_FILE_NAME)
