"""
This class implements a random IP addresses generator
"""


class AddressGenerator(object):
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
