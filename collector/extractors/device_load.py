from abc import ABCMeta, abstractmethod
from subprocess import Popen
import os
import time

from collector.extractor import Extractor
from utils.fs import FileSystem

"""
This class models a device load extractor. This kind of extractor has in charge the task of dumping the routing tables.
"""


class DeviceLoad(Extractor):

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
This class implements an extractor for measuring the device load in terms of how many entries are installed inside the
routing table. Being an implementation for Mininet, this extractor simply runs an ovs-ofctl dump-flows command on each
switch in the overlay, and it stores the output inside the extractor folder.
"""


class MininetDeviceLoad(DeviceLoad):
    def __init__(self):
        DeviceLoad.__init__(self)
        # Folder in which all extracred data will be stored
        self._extractor_folder = 'device-load'
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
    Set the overlay which the simulation is running on.
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
        switches = self._overlay.get_nodes()
        # Probably put here the creation of the folder which will contain all datapaths' flow tables.
        for switch in switches.values():
            self._log.debug(self.__class__.__name__, 'Extracting routing table from %s', switch.get_name())
            # Command for extracting data
            cmd = 'sudo ovs-ofctl -O OpenFlow13 dump-flows ' + switch.get_name()
            # File into the simulation folder in which storing data
            output_file_name = self._simulation_path + '/' + self._extractor_folder + '/' + switch.get_name() + '.data'
            # Create a file starting from its name
            output_file = open(output_file_name, 'w')
            self._log.debug(self.__class__.__name__, 'Starting to write the convergence time into extractor folder.')
            # Create a new subprocess whose output will be redirect into output_file
            extractor = Popen(args=cmd, stdout=output_file, shell=True)
            # Write data on disk
            output_file.flush()
            os.fsync(output_file.fileno())
            # Wait for process termination
            extractor.wait()
        self._log.info(self.__class__.__name__, 'All data has been correctly extracted.')
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
        # Folder in which all extracred data will be stored
        self._extractor_folder = 'device-load'
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
        # Create extractor's folder # Fixme Move into FileSystem
        os.makedirs(self._simulation_path + '/' + self._extractor_folder)

    '''
    Set the overlay which the simulation is running on.
    '''
    def set_overlay(self, overlay):
        self._overlay = overlay

    '''
    Start the process of extracting data.
    '''
    def extract_data(self):
        # First of all, sleep for 1 minute
        self._log.info(self.__class__.__name__, 'Sleeping waiting for data to extract.')
        time.sleep(10)
        self._log.info(self.__class__.__name__, 'I woke up. I am starting to extract data.')
        switches = self._overlay.get_nodes()
        # Probably put here the creation of the folder which will contain all datapaths' flow tables.
        for switch in switches.values():
            self._log.debug(self.__class__.__name__, 'Extracting routing table from %s', switch.get_name())
            # Command for extracting data
            if switch.get_role() == 'PE':
                print '################################# Get BGP table'
            print '######################### GET OSPF table'
        #     cmd = 'sudo ovs-ofctl -O OpenFlow13 dump-flows ' + switch.get_name()
        #     # File into the simulation folder in which storing data
        #     output_file_name = self._simulation_path + '/' + self._extractor_folder + '/' + switch.get_name() + '.data'
        #     # Create a file starting from its name
        #     output_file = open(output_file_name, 'w')
        #     self._log.debug(self.__class__.__name__, 'Starting to write the convergence time into extractor folder.')
        #     # Create a new subprocess whose output will be redirect into output_file
        #     extractor = Popen(args=cmd, stdout=output_file, shell=True)
        #     # Write data on disk
        #     output_file.flush()
        #     os.fsync(output_file.fileno())
        #     # Wait for process termination
        #     extractor.wait()
        self._log.info(self.__class__.__name__, 'All data has been correctly extracted.')
        # Notify all observers
        self.notify_all()

    '''
    Run the thread in which this extractor is in execution.
    '''
    def run(self):
        self.extract_data()