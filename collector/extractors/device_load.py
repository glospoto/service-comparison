from abc import ABCMeta, abstractmethod
from subprocess import Popen
import os
import time

from collector.extractor import Extractor
from utils.file import File

"""
This class models a device load extractor. This kind of extractor has in charge the task of dumping the routing tables.
"""


class DeviceLoad(Extractor):
    __metaclass__ = ABCMeta

    def __init__(self):
        Extractor.__init__(self)
        # Folder in which all extracted data will be stored
        self._extractor_folder_name = 'device-load'

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
This class implements an extractor for measuring the device load in terms of how many entries are installed inside the
routing table. Being an implementation for Mininet, this extractor simply runs an ovs-ofctl dump-flows command on each
switch in the overlay, and it stores the output inside the extractor folder.
"""


class MininetDeviceLoad(DeviceLoad):
    def __init__(self):
        DeviceLoad.__init__(self)
        # The abspath to the extraction folder
        self._extractor_folder = None

    def __repr__(self):
        return self.__class__.__name__

    '''
    Set the simulation path in which save the extracted data.
    '''

    def set_simulation(self, simulation):
        # Set the simulation
        self._simulation = simulation
        # The abspath to the extraction folder
        self._extractor_folder = self._fs.join(simulation.get_simulation_path(), self._extractor_folder_name)
        # Create extraction folder on the file system
        self._fs.make_dir(self._extractor_folder)

    '''
    Start the process of extracting data.
    '''

    def extract_data(self):
        # First of all, sleep for 1 minute
        self._log.info(self.__class__.__name__, 'Sleeping waiting for data to extract.')
        time.sleep(10)
        self._log.info(self.__class__.__name__, 'I woke up. I am starting to extract data.')
        switches = self._simulation.get_overlay().get_nodes()
        # Probably put here the creation of the folder which will contain all datapaths' flow tables.
        for switch in switches.values():
            self._log.debug(self.__class__.__name__, 'Extracting routing table from %s', switch.get_name())
            # Command for extracting data
            cmd = 'sudo ovs-ofctl -O OpenFlow13 dump-flows ' + switch.get_name()
            # File into the simulation folder in which storing data
            file_name = switch.get_name() + '.data'
            output_file = File(self._extractor_folder, file_name)
            self._log.debug(self.__class__.__name__, 'Starting to write FIB into extractor folder.')
            # Create a new subprocess whose output will be redirect into output_file
            extractor = Popen(args=cmd, stdout=output_file.get_file(), shell=True)
            # Write data on disk
            output_file.save()
            # Wait for process termination
            extractor.wait()
        self._log.info(self.__class__.__name__, 'All data has been successfully extracted.')
        # Notify all observers
        self.notify_all()

    '''
    Run the thread in which this extractor is in execution.
    '''

    def run(self):
        self.extract_data()


"""
This class implements an extractor for measuring the device load in terms of how many entries are installed inside the
routing table. Being an implementation for Docker, this extractor runs certain commands in order to correctly dump
information from routing tables.
"""


class DockerDeviceLoad(DeviceLoad):
    def __init__(self):
        DeviceLoad.__init__(self)
        # The abspath to the extraction folder
        self._extractor_folder = None

    def __repr__(self):
        return self.__class__.__name__

    '''
    Set the simulation path in which save the extracted data.
    '''

    def set_simulation(self, simulation):
        # Set the simulation
        self._simulation = simulation
        # The abspath to the extraction folder
        self._extractor_folder = self._fs.join(simulation.get_simulation_path(), self._extractor_folder_name)
        # Create extraction folder on the file system
        self._fs.make_dir(self._extractor_folder)

    '''
    Start the process of extracting data.
    '''

    def extract_data(self):
        extractors = []
        # First of all, sleep for 1 minute
        self._log.info(self.__class__.__name__, 'Sleeping waiting for data to extract.')
        time.sleep(120)
        self._log.info(self.__class__.__name__, 'I woke up. I am starting to extract data.')
        switches = self._overlay.get_nodes()
        # Probably put here the creation of the folder which will contain all datapaths' flow tables.
        for switch in switches.values():
            self._log.debug(self.__class__.__name__, 'Extracting routing table from %s', switch.get_name())
            # File into the simulation folder in which storing data
            output_file_name = self._simulation_path + '/' + self._extractor_folder + '/' + switch.get_name() + '.data'
            # Create a file starting from its name
            output_file = open(output_file_name, 'wa')
            # Command for extracting data
            if switch.get_role() == 'PE':
                self._log.debug(self.__class__.__name__, 'Starting to extract VRF information.')
                cmd_vrf = 'sudo docker exec %s bagpipe-looking-glass vpns instances test routes' % switch.get_name()
                extractor_customer = Popen(cmd_vrf, shell=True, stdout=output_file)
                extractors.append(extractor_customer)
                self._log.debug(self.__class__.__name__, 'VRF information have been correctly extracted.')
            self._log.debug(self.__class__.__name__, 'Starting to extract FIB information.')
            cmd_fib = 'sudo docker exec %s ip r s' % switch.get_name()
            extractor_fib = Popen(cmd_fib, shell=True, stdout=output_file)
            extractors.append(extractor_fib)
            self._log.debug(self.__class__.__name__, 'FIB information have been successfully extracted.')
            # Write data on disk
            output_file.flush()
            os.fsync(output_file.fileno())
            # Wait for process termination
            for e in extractors:
                e.wait()
        self._log.info(self.__class__.__name__, 'All data has been successfully extracted.')
        # Notify all observers
        self.notify_all()

    '''
    Run the thread in which this extractor is in execution.
    '''

    def run(self):
        self.extract_data()
