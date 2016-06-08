from netaddr import IPNetwork

"""
This class implements a random IP addresses generator
"""


class AddressGenerator(object):
    __instance = None

    def __init__(self):
        # Flag indicating whether the /30 subnets have been already generated
        self._subnets_already_generated = False
        # The list with all the /30 subnets for p2p link
        self._subnets_for_p2p_links = []

    '''
    Return an instance of this class in accord with the Singleton pattern.
    '''

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = AddressGenerator()
        return cls.__instance

    '''
    Create a /30 set of subnets starting from a /16 subnets. Those subnets will be used for p2p links
    '''
    def _create_subnets_for_p2p_links(self):
        subnet = IPNetwork('10.0.0.0/20')
        self._subnets_for_p2p_links = list(subnet.subnet(30))
        # Subnets have been successfully generated
        self._subnets_already_generated = True

    def get_next_subnet(self):
        if not self._subnets_already_generated:
            self._create_subnets_for_p2p_links()
        if len(self._subnets_for_p2p_links) > 0:
            return self._subnets_for_p2p_links.pop(0)

    @staticmethod
    def generate_ip_address():
        import random
        import socket
        import struct
        return socket.inet_ntoa(struct.pack('>I', random.randint(2, 0xfffffffe)))

    @staticmethod
    def get_subnet_from_ip(ip):
        h_ip_ib_byte = ip.split('.')
        h_ip_ib_byte[3] = '0'
        h_subnet = '.'.join(h_ip_ib_byte) + '/24'
        return h_subnet
