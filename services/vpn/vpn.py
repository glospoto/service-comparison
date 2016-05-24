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

    def get_name(self):
        return self._name

    def add_site(self, site):
        self._sites.append(site)

    def get_sites(self):
        return self._sites

    def add_host(self, host):
        self._hosts[host.get_name()] = host

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
        return "Site(VPN=%s, PE=%s, port=%s, network=%s)" % (
            self._vpn.get_name(), self._pe.get_name(), self._port, self._network)

    def get_vpn(self):
        return self._vpn

    def get_pe(self):
        return self._pe

    def get_port(self):
        return self._port

    def get_network(self):
        return self._network


"""
This class models the switch in the network
"""


class Switch(object):
    def __init__(self, dpid, name, role):
        self._dpid = int(dpid)
        self._name = self._parse_name(name)
        self._variable_name = self._name.lower()
        self._vrf_role = role
        self._interfaces_to_host = {}

    def __repr__(self):
        return 'Switch[dpid=%s, name=%s, role=%s]' % (self._dpid, self._name, self._vrf_role)

    @staticmethod
    def _parse_name(name):
        name.replace(' ', '_')
        switch_name = name[:5]
        if switch_name.endswith('_'):
            switch_name = switch_name.replace('_', '')
        return switch_name

    def get_dpid(self):
        # Returned value is an INT
        return self._dpid

    def get_variable_name(self):
        return self._variable_name

    def get_name(self):
        return self._name

    def get_role(self):
        return self._vrf_role

    def assign_interface_to_host(self, host):
        number_of_interface = len(self._interfaces_to_host.values())
        number_of_interface += 1
        self._interfaces_to_host[host] = number_of_interface

    def get_interface_for_host(self, host):
        return self._name + '-eth' + str(self._interfaces_to_host.get(host))


"""
This class models a link in the network. An edge is an object with a start end an end switch.
"""


class Link(object):
    def __init__(self, from_node, to_node):
        self._from = from_node
        self._to = to_node

    def __repr__(self):
        return 'Link[from=%s, to=%s]' % (self._from, self._to)

    def get_from(self):
        return self._from

    def get_to(self):
        return self._to


"""
This class models a host in the network
"""


class Host(object):
    def __init__(self, name, ip):
        self._name = name
        # _ip is an instance of the class netaddr.IPAddr
        self._ip = ip
        # _mac is an instance of the class netaddr.EUI
        self._mac = None
        # PE to which this host is connected to
        self._pe = None

    def __repr__(self):
        return 'Host[name=%s, IP=%s, MAC=%s]' % (self._name, self._ip, self._mac)

    def get_name(self):
        return self._name

    def get_variable_name(self):
        return self._name

    def get_ip(self):
        return self._ip

    def set_mac(self, mac):
        self._mac = mac

    def get_mac(self):
        return self._mac

    def set_pe(self, pe):
        self._pe = pe

    def get_pe(self):
        return self._pe
