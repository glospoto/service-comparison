from netaddr import IPNetwork

"""
This class models a VirtualPrivateNetwork (VPN). A VPN consists of two PEs and two hosts, each of which
is connected to a PE
"""


class VirtualPrivateNetwork(object):
    def __init__(self, name):
        self._name = name
        # The sites of the VPN
        self._sites = []
        # The hosts in the VPN
        self._hosts = {}

    def __repr__(self):
        return 'VPN[name=%s, Sites=%s, Hosts=%s]' % \
               (self._name, self._sites, self._hosts)

    '''
    Return the name of this Virtual Private Network
    '''

    def get_name(self):
        return self._name

    '''
    Add a site to this VPN
    '''

    def add_site(self, site):
        self._sites.append(site)

    '''
    Return the sites of this VPN
    '''

    def get_sites(self):
        return self._sites

    '''
    Add a host to this VPN
    '''

    def add_host(self, host):
        self._hosts[host.get_name()] = host

    '''
    Return a host of this VPN
    '''

    def get_host(self, host):
        return self._hosts.get(host.get_name())


"""
This class models a site. Each VPN has at least two sites linked on different PEs. So, a site represents the VPN subnet
linked at a certain PE at a well known port
"""


class Site(object):
    def __init__(self, vpn, pe, port, network):
        self._vpn = vpn
        self._pe = pe
        self._port = port
        self._network = IPNetwork(network)

    def __repr__(self):
        return "Site[VPN=%s, PE=%s, port=%s, network=%s]" % (
            self._vpn.get_name(), self._pe.get_name(), self._port, self._network)

    '''
    Return the VPN of this site
    '''

    def get_vpn(self):
        return self._vpn

    '''
    Return the PE of this site
    '''

    def get_pe(self):
        return self._pe

    '''
    Return the port of the PE for this site
    '''

    def get_port(self):
        return self._port

    '''
    Return the IP network associated to this site
    '''

    def get_network(self):
        return self._network


"""
This class models the switch in the network
"""


class Switch(object):
    def __init__(self, dpid, name, role):
        self._dpid = int(dpid)
        self._name = self._parse_name(name)
        # self._variable_name = self._name.lower()
        self._vrf_role = role
        self._interfaces = []

    def __repr__(self):
        return 'Switch[dpid=%s, name=%s, role=%s]' % (self._dpid, self._name, self._vrf_role)

    '''
    This method parse the name of the switch replacing undesirable characters (like ',', '_', spaces, ...)
    '''

    @staticmethod
    def _parse_name(name):
        name.replace(' ', '_')
        name.replace(',', '')
        switch_name = name  # [:5]
        if switch_name.endswith('_'):
            switch_name = switch_name.replace('_', '')
        return switch_name

    '''
    Return the DPID of the switch
    '''

    def get_dpid(self):
        # Returned value is an INT
        return self._dpid

    '''
    def get_variable_name(self):
        return self._variable_name
    '''

    '''
    Return the name of the switch
    '''

    def get_name(self):
        return self._name

    def get_role(self):
        return self._vrf_role

    '''
    Create and return a new interface (eth-X) for the switch.
    '''

    def create_interface(self):
        number_of_interface = len(self._interfaces)
        number_of_interface += 1
        interface_name = self._name + '-eth' + str(number_of_interface)
        self._interfaces.append(interface_name)
        return interface_name


"""
This class models a link in the network. An edge is an object with a start end an end switch.
"""


class Link(object):
    def __init__(self, from_switch, to_switch, from_switch_interface, to_switch_interface, subnet):
        self._from_switch = from_switch
        self._to_switch = to_switch
        self._from_switch_interface = from_switch_interface
        self._to_switch_interface = to_switch_interface
        # It is used for MplsBpg implementation
        self._subnet = subnet

    def __repr__(self):
        return 'Link[from=%s:%s, to=%s:%s]' % (
            self._from_switch, self._from_switch_interface, self._to_switch, self._to_switch_interface)

    '''
    Return the name of the link. That name is created by composing the name of the source node and the name of the
    destination node
    '''

    def get_name(self):
        return self._from_switch.get_name() + '-' + self._to_switch.get_name()

    '''
    Return the source switch of the link
    '''

    def get_from_switch(self):
        return self._from_switch

    '''
    Return the interface of the source switch on the link
    '''

    def get_from_switch_interface(self):
        return self._from_switch_interface

    '''
    Return the destination switch of the link
    '''

    def get_to_switch(self):
        return self._to_switch

    '''
    Return the interface of the destination switch on the link
    '''

    def get_to_switch_interface(self):
        return self._to_switch_interface

    '''
    Return the IP subnet associated to this link
    '''

    def get_subnet(self):
        return self._subnet


"""
This class models a host in the network
"""


class Host(object):
    def __init__(self, name, ip):
        self._name = name
        # The host's interface name
        self._interface_name = 'eth1'
        # _ip is an instance of the class netaddr.IPAddr
        self._ip = ip
        # _mac is an instance of the class netaddr.EUI
        self._mac = None
        # PE to which this host is connected to
        self._pe = None

    def __repr__(self):
        return 'Host[name=%s, IP=%s, MAC=%s]' % (self._name, self._ip, self._mac)

    '''
    Return the name of the host
    '''

    def get_name(self):
        return self._name

    '''
    Return the interface name of this host
    '''

    def get_interface_name(self):
        return self._interface_name

    '''
    Return the IP address of the host
    '''

    def get_ip(self):
        return self._ip

    '''
    Set the MAC address of the host
    '''

    def set_mac(self, mac):
        self._mac = mac

    '''
    Return the MAC address of the host
    '''

    def get_mac(self):
        return self._mac

    '''
    Set the PE switch which this host is connected to
    '''

    def set_pe(self, pe):
        self._pe = pe

    '''
    Return the PE switch connected to this host
    '''

    def get_pe(self):
        return self._pe
