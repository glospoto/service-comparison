from abc import ABCMeta, abstractmethod
import time

from scapy.layers.inet import TCP
from scapy.utils import rdpcap

from collector.extractor import Extractor
from utils.file import File

"""
This class implements an extractor for measuring the control plane overhead in terms of number of 
exchanged control plane messages.
"""


class ControlPlaneOverhead(Extractor):
	__metaclass__ = ABCMeta

	def __init__(self):
		Extractor.__init__(self)
		# Folder in which all extracted data will be stored
		self._extractor_folder_name = 'cp-overhead'

	'''
	Set the simulation path in which save the extracted data.
	'''

	@abstractmethod
	def set_simulation(self, simulation):
		pass

	'''
	Start the process of extracting data.
	'''

	@abstractmethod
	def extract_data(self):
		pass


"""
This class implements an extractor for measuring the number of control plane messages exchanged by 
an alternative running on Mininet simulator. This extractor is based on a control plane messages 
collector. The measure is based on the sniffed packets.
"""


class MininetControlPlaneOverhead(ControlPlaneOverhead):
	def __init__(self,):
		ControlPlaneOverhead.__init__(self)
		# The abspath to the extraction folder
		self._extractor_folder = None
		# The file name which contains extracted information
		self._extractor_file_name = 'overhead.data'

	def __repr__(self):
		return self.__class__.__name__

	'''
	Set the simulation path in which save the extracted data.
	'''

	def set_simulation(self, simulation):
		# Set the simulation
		self._simulation = simulation
		# The abspath to the extraction folder
		self._extractor_folder = self._fs.join(
			simulation.get_simulation_path(), self._extractor_folder_name)
		# Create extraction folder on the file system
		self._fs.make_dir(self._extractor_folder)

	'''
	Start the process of extracting data.
	'''

	def extract_data(self):
		# First of all, sleep for 1 minute
		self._log.info(self.__class__.__name__, 'Sleeping waiting for data to extract.')
		time.sleep(15)
		self._log.info(self.__class__.__name__, 'I woke up. I am starting to extract data.')
		# Load the sniff
		pkts = rdpcap(self._fs.get_tmp_folder() + '/sniff.pcap')
		# Counter for counting all openflow packets included into the sniffing.
		count = 0
		self._log.debug(
			self.__class__.__name__, 
			'Calculating the total number of exchanged control plane messages.')
		for pkt in pkts:
			# OpenFlow is not yet implemented as dissector in Scapy, thus just count TCP packets from/to standard
			# OpenFlow controller port.
			if TCP in pkt and (pkt[TCP].sport == 6633 or pkt[TCP].dport == 6633):
				if TCP in pkt:
					count += 1
		self._log.debug(
			self.__class__.__name__, 
			'Starting to write the convergence time into extractor folder.')
		# Write it into a file inside the extractor folder
		output_file = File(self._extractor_folder, self._extractor_file_name)
		# output_file_name = self._simulation_path + '/' + self._extractor_folder + '/overhead.data'
		# output_file = open(output_file_name, 'w')
		output_file.write('Exchanged packets: %s' % str(count))
		output_file.save()
		self._log.info(self.__class__.__name__, 'All data has been correctly extracted.')
		# Notify all observers
		self.notify_all('extractor')

	'''
	Run the thread in which this extractor is in execution.
	'''

	def run(self):
		self.extract_data()


class DockerControlPlaneOverhead(ControlPlaneOverhead):
	def __init__(self,):
		ControlPlaneOverhead.__init__(self)
		# The abspath to the extraction folder
		self._extractor_folder = None
		# The file name which contains extracted information
		self._extractor_file_name = 'overhead.data'

	def __repr__(self):
		return self.__class__.__name__

	'''
	Set the simulation path in which save the extracted data.
	'''

	def set_simulation(self, simulation):
		# Set the simulation
		self._simulation = simulation
		# The abspath to the extraction folder
		self._extractor_folder = self._fs.join(
			simulation.get_simulation_path(), self._extractor_folder_name)
		# Create extraction folder on the file system
		self._fs.make_dir(self._extractor_folder)

	'''
	Start the process of extracting data.
	'''

	def extract_data(self):
		pass

	def run(self):
		self.extract_data()
