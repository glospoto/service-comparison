from abc import ABCMeta, abstractmethod

from scapy.all import *
from scapy.layers.inet import TCP
from scapy.utils import rdpcap

from collector.extractor import Extractor
from utils.fs import FileSystem

"""
This class implements an extractor for measuring the control plane overhead in terms of number of exchanged control
plane messages.
"""


class ControlPlaneOverhead(Extractor):
    __metaclass__ = ABCMeta

    def __init__(self):
        Extractor.__init__(self)
        # The FileSystem handler
        self._fs = FileSystem.get_instance()

    '''
    Set the simulation path in which save the extracted data.
    '''

    @abstractmethod
    def set_simulation_path(self, simulation_path):
        pass

    '''
    Set the overlay on which the simulation is running on.
    '''

    @abstractmethod
    def set_overlay(self, overlay):
        pass

    '''
    Start the process of extracting data.
    '''

    @abstractmethod
    def extract_data(self):
        pass


"""
This class implements an extractor for measuring the number of control plane messages exchanged by an alternative
running on Mininet simulator. This extractor is based on a control plane messages collector. The measure is based on
the sniffed packets.
"""


class MininetControlPlaneOverhead(ControlPlaneOverhead):
    def __init__(self):
        ControlPlaneOverhead.__init__(self)
        # Folder in which all extracred data will be stored
        self._extractor_folder = 'cp-overhead'
        # Simulation path for data extraction
        self._simulation_path = None
        # The overlay
        self._overlay = None

    def __repr__(self):
        return self.__class__.__name__

    '''
    Set the simulation path in which save the extracted data.
    '''

    def set_simulation_path(self, simulation_path):
        self._simulation_path = simulation_path
        # Create extractor's folder
        os.makedirs(self._simulation_path + '/' + self._extractor_folder)

    '''
    Set the overlay on which the simulation is running on.
    '''

    def set_overlay(self, overlay):
        self._overlay = overlay

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
        self._log.debug(self.__class__.__name__, 'Calculating the total number of exchanged control plane messages.')
        for pkt in pkts:
            # OpenFlow is not yet implemented as dissector in Scapy, thus just count TCP packets from/to standard
            # OpenFlow controller port.
            if TCP in pkt and (pkt[TCP].sport == 6633 or pkt[TCP].dport == 6633):
                if TCP in pkt:
                    count += 1
        self._log.debug(self.__class__.__name__, 'Starting to write the convergence time into extractor folder.')
        # Write it into a file inside the extractor folder
        output_file_name = self._simulation_path + '/' + self._extractor_folder + '/overhead.data'
        output_file = open(output_file_name, 'w')
        output_file.write('Exchanged packets: %s' % str(count))
        self._log.info(self.__class__.__name__, 'All data has been correctly extracted.')
        # Notify all observers
        self.notify_all()

    '''
    Run the thread in which this extractor is in execution.
    '''

    def run(self):
        self.extract_data()
