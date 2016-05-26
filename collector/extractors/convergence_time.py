from abc import ABCMeta, abstractmethod

from scapy.all import *
from scapy.layers.inet import TCP
from scapy.utils import rdpcap

from collector.extractor import Extractor

"""
This class implements an extractor for measuring the convergence time of an alternative.
"""


class ControlPlaneConvergenceTime(Extractor):
    __metaclass__ = ABCMeta

    def __init__(self):
        Extractor.__init__(self)
        # Folder in which all extracted data will be stored
        self._extractor_folder = 'cp-convergence-time'

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
This class implements an extractor for measuring the convergence time of an alternative running on Mininet simulator.
This extractor is based on a control plane messages collector. The convergence time measure is based on timestamps
reported in the sniffed packets.
"""


class MininetControlPlaneConvergenceTime(ControlPlaneConvergenceTime):
    def __init__(self):
        ControlPlaneConvergenceTime.__init__(self)

    def __repr__(self):
        return self.__class__.__name__

    '''
    Set the simulation path in which save the extracted data.
    '''

    def set_simulation_path(self, simulation_path):
        self._simulation_path = simulation_path
        # Create extractor's folder
        self._fs.make_dir(self._simulation_path + '/' + self._extractor_folder)

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
        # The list of all openflow packets in the sniffing.
        openflow_packets = []
        for pkt in pkts:
            # OpenFlow is not yet implemented as dissector in Scapy, thus just count TCP packets from/to standard
            # OpenFlow controller port.
            if TCP in pkt and (pkt[TCP].sport == 6633 or pkt[TCP].dport == 6633):
                if TCP in pkt:
                    # Add to the openflow_packet list
                    openflow_packets.append(pkt)
        self._log.debug(self.__class__.__name__, 'Calculating the time of the of the last sniffed packet.')
        # Take the time of the last sniffed packet
        time_last_packet = openflow_packets[len(openflow_packets) - 1].time
        self._log.debug(self.__class__.__name__, 'Calculating the time of the of the first sniffed packet.')
        # Take the time of the first sniffed packet
        time_first_packet = openflow_packets[0].time
        self._log.debug(self.__class__.__name__, 'Calculating the convergence time.')
        # Calculate the convergence time
        convergence_time = time_last_packet - time_first_packet
        self._log.debug(self.__class__.__name__, 'Starting to write the convergence time into extractor folder.')
        # Write it into a file inside the extractor folder
        output_file_name = self._simulation_path + '/' + self._extractor_folder + '/time.data'
        output_file = open(output_file_name, 'w')
        output_file.write('Convergence time (seconds): %s' % str(convergence_time))
        self._log.info(self.__class__.__name__, 'All data has been successfully extracted.')
        # Notify all observers
        self.notify_all()

    '''
    Run the thread in which this extractor is in execution.
    '''

    def run(self):
        self.extract_data()
