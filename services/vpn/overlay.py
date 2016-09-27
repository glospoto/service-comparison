import random

from model.topology.overlay import Overlay
from utils.log import Logger

"""
A VPN overlay is a graph populated with subclasses of Node and Edge regards the VPN service.
"""


class VpnOverlay(Overlay):
	def __init__(self):
		Overlay.__init__(self, self.__class__.__name__)
		# Logger
		self._log = Logger.get_instance()
		# Internal data structures
		self._switches = {}
		self._hosts = {}
		# This is a map<device, list of all connected devices>; it is an OrderedDict to preserve 
		# the mapping between host-pe connections.
		self._links = []  # OrderedDict()

	def __repr__(self):
		return 'Overlay[name=%s, #switches=%i, #links=%i, #hosts=%i]' \
			   % (self._name, len(self._switches), len(self._links), len(self._hosts))

	'''
	Return the name of this overlay.
	'''

	def get_name(self):
		return self._name

	'''
	Add a new datapath to this overlay.
	'''

	def add_node(self, switch):
		self._switches[switch.get_dpid()] = switch
		self._log.debug(self.__class__.__name__, 'Switch %s added.', switch)

	'''
	Add a new link to this overlay.
	'''

	def add_link(self, link):
		self._links.append(link)
		self._log.debug(self.__class__.__name__, 'Link %s added.', link)

	'''
	Add a new host to this overlay.
	'''

	def add_host(self, host):
		self._hosts[host.get_name()] = host
		self._log.debug(self.__class__.__name__, 'Host %s added.', host)

	'''
	Return a datapath starting from its datapath ID.
	'''

	def get_node(self, dpid):
		return self._switches.get(dpid)

	'''
	Return all switches in this overlay.
	'''

	def get_nodes(self):
		return self._switches

	'''
	Return all links in this overlay.
	'''

	def get_links(self):
		return self._links

	'''
	Return a Link starting from the host connected to it.
	'''

	def get_host_link(self, host):
		for link in self._links:
			src_switch = link.get_from_switch()
			dst_switch = link.get_to_switch()
			if src_switch == host.get_name() or dst_switch.get_name() == host.get_name():
				return link

	'''
	Return a host.
	'''

	def get_host(self, host):
		return self._hosts.get(host.get_name())

	'''
	Return all hosts in this overlay.
	'''

	def get_hosts(self):
		return self._hosts

	'''
	Return a random pair of PEs. On each PE, an host will be attached, in order to create VPN's 
	sites.
	'''

	def get_two_random_pes(self):
		pes = []
		first_pe = None
		second_pe = None
		while first_pe is None or second_pe is None:
			if first_pe is None:
				first_pe = random.choice(self._switches.values())
			if second_pe is None:
				second_pe = random.choice(self._switches.values())

			if first_pe.get_dpid() != second_pe.get_dpid():
				if first_pe not in pes:
					if first_pe.get_role() == 'PE':
						pes.append(first_pe)
					else:
						first_pe = None
				if second_pe not in pes:
					if second_pe.get_role() == 'PE':
						pes.append(second_pe)
					else:
						second_pe = None
			else:
				# Only keep one of the two PEs (for example the first) and discard the other one
				second_pe = None
		return pes
