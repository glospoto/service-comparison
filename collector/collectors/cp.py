"""
This class models an abstract DeviceLoad extractor
"""

from abc import ABCMeta, abstractmethod

import netifaces

from collector.collector import Collector
from utils.network import Sniffer
from utils.process import Process


class ControlPlaneMessages(Collector):
	__metaclass__ = ABCMeta

	def __init__(self):
		Collector.__init__(self)
		self._sniffer = None

	'''
	Collect data for this metric.
	'''

	@abstractmethod
	def collect_data(self):
		pass


"""
This class models a control plane messages collector for Mininet environment. This means starting a 
Sniffer on lo interface and collecting messages into a pcap file inside TMP folder.
"""


class MininetControlPlaneMessages(ControlPlaneMessages):
	def __init__(self):
		ControlPlaneMessages.__init__(self)

	def __repr__(self):
		return self.__class__.__name__

	'''
	Collect data for this collector.
	'''

	def collect_data(self):
		self._log.debug(self.__class__.__name__, 'Creating a new sniffer on interface lo.')
		# Starting a sniffer
		self._sniffer = Sniffer('lo', self._fs.get_tmp_folder() + '/sniff.pcap')
		# Sniff data
		self._log.info(self.__class__.__name__, 'Starting to sniff control plane messages.')
		self._sniffer.sniff()
		self._log.info(self.__class__.__name__, 'Sniffer finished to collect data.')

	'''
	Run the thread containing the control plane messages collector.
	'''

	def run(self):
		self.collect_data()

	def stop(self):
		pass

"""
This class models a control plane messages collector for Docker environment. This means starting a 
Sniffer on specific interfaces and collecting messages into a pcap file inside TMP folder.
"""


class DockerControlPlaneMessages(ControlPlaneMessages):
	def __init__(self):
		ControlPlaneMessages.__init__(self)
		# A list of interfaces with an active sniffere associated
		self._active_ifaces = []
		# The list of all tcpdump processes
		self._processes = []

	def __repr__(self):
		return self.__class__.__name__

	'''
	Get all docker bridges
	'''
	def _get_interfaces(self):
		host_ifaces = netifaces.interfaces()
		ifaces = filter(lambda iface: 'br-' in iface, host_ifaces)
		return ifaces

	'''
	Collect data for this collector.
	'''

	def collect_data(self):
		ifaces = self._get_interfaces()
		if len(ifaces) > 0:
			for iface in ifaces:
				if iface not in self._active_ifaces:
					self._log.debug(
						self.__class__.__name__, 
						'Creating a new sniffer on interface %s.', iface)
					cmd = 'sudo tcpdump -nli %s -w %s' % (
						iface, self._fs.get_tmp_folder() + '/' + iface + '.pcap')
					self._active_ifaces.append(iface)
					self._log.info(
						self.__class__.__name__, 
						'Starting to sniff control plane messages on interface %s.', iface)
					process = Process()
					process.execute(cmd)
					self._processes.append(process)
					self._log.info(
						self.__class__.__name__, 'Sniffer finished to collect data.')

	'''
	Run the thread containing the control plane messages collector.
	'''

	def run(self):
		# self.collect_data()
		pass

	def stop(self):
		# Kill all sniffers
		for p in self._processes:
			p.kill()
		self._processes[:]
		self._active_ifaces[:]

	def update(self, msg):
		if msg == 'bridge':
			self.collect_data()
			