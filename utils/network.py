from scapy.sendrecv import sniff, wrpcap

"""
This class implements a sniffer used for some collectors.
"""


class Sniffer(object):
	def __init__(self, intf, pcap_file):
		self._interface = intf
		self._pcap_file = pcap_file

	'''
	Sniff network packets.
	'''

	def sniff(self):
		pkts = sniff(iface=self._interface, timeout=14)
		wrpcap(self._pcap_file, pkts)
