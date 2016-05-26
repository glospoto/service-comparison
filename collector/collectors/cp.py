from abc import ABCMeta, abstractmethod

from collector.collector import Collector
from utils.network import Sniffer

"""
This class models an abstract DeviceLoad extractor
"""


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
This class models a control plane messages collector for Mininet environment. This means starting a Sniffer on lo
interface and collecting messages into a pcap file inside TMP folder.
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
        self._log.info(self.__class__.__name__, 'Sniffer has been finished to collect data.')

    '''
    Run the thread containing the control plane messages collector.
    '''

    def run(self):
        self.collect_data()
