from threading import Thread
from subprocess import Popen, PIPE

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from utils.log import Logger

"""
This class implements a custom switch that can be associated to the Mininet instance. A 
CustomSwitch is based on a standard OVVSwitch object defined into Mininet API.
"""


class CustomSwitch(OVSSwitch):
	# Modify this class if you want to use another switch
	def __init__(self, name, **params):
		OVSSwitch.__init__(self, name=name, datapath='user', **params)


"""
This class wraps a Mininet object
"""


class MininetTopology(object):
	def __init__(self, overlay):
		# Logger
		self._log = Logger.get_instance()
		# The overlay based on which the topology is created
		self._overlay = overlay
		# Create a Mininet instance
		self._net = Mininet(
			controller=None, switch=CustomSwitch, listenPort=6634, inNamespace=False)
		# Add controller to the network
		self._net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

	'''
	Calculate the hex representation of the datapath's DPID starting from its decimal 
	representation.
	'''

	@staticmethod
	def _dpid(dpid):
		return hex(dpid)[2:]

	'''
	Return a reference to Mininet object.
	'''

	def get_mininet_object(self):
		return self._net

	'''
	Add switches to the Mininet object.
	'''

	# Add switch to the MininetTopology
	def add_switches(self):
		self._log.debug(self.__class__.__name__, 'Starting to add switches to Mininet.')
		for switch in self._overlay.get_nodes().values():
			self._net.addSwitch(switch.get_name(), dpid=self._dpid(switch.get_dpid()))
		self._log.info(self.__class__.__name__, 'All switches have been successfully added.')

	'''
	Add hosts to the Mininet object.
	'''

	def add_hosts(self):
		self._log.debug(self.__class__.__name__, 'Starting to add hosts to Mininet.')
		for host in self._overlay.get_hosts().values():
			self._net.addHost(host.get_name())
		self._log.info(self.__class__.__name__, 'All hosts have been successfully added.')

	'''
	Add links to the Mininet object.
	'''

	def add_links(self):
		self._log.debug(self.__class__.__name__, 'Starting to add links to Mininet.')
		for link in self._overlay.get_links():
			self._net.addLink(link.get_from_switch().get_name(), link.get_to_switch().get_name())
		self._log.info(self.__class__.__name__, 'All links have been successfully added.')


"""
This class implements a thread in which Mininet will be executed.
"""


class MininetStartSimulation(Thread):
	def __init__(self, mininet_topology):
		Thread.__init__(self)
		# Logger
		self._log = Logger.get_instance()
		# The reference to the topology executing into mininet
		self._mininet_topology = mininet_topology

	'''
	Run the Mininet environment.
	'''

	def run(self):
		self._log.debug(self.__class__.__name__, 'Preparing to execute a Mininet instance.')
		net = self._mininet_topology.get_mininet_object()
		net.start()
		self._log.info(self.__class__.__name__, 'Mininet has been successfully started.')

	'''
	Stop the Mininet environment.
	'''

	def stop(self):
		self._log.debug(self.__class__.__name__, 'Preparing to stop Mininet instance.')
		# net = self._mininet_topology.get_mininet_object()
		# net.stop()
		# Run mn -c for cleaning virtual interfaces and bridges
		mininet_stop = Popen('sudo mn -c', shell=True, stdout=PIPE, stderr=PIPE)
		mininet_stop.wait()
		self._log.debug(self.__class__.__name__, 'Mininet has been successfully stopped.')
