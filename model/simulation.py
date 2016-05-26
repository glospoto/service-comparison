from threading import Thread
import os
import time

from utils.log import Logger
from utils.fs import FileSystem

"""
This class models a simulation. A simulation consists of a folder in which frameworks stores some useful information.
All simulations are contained in the folder "simulation" and it has the following structure:
 - simulation/
   - service_name/
     - alternative1
       - timestamp/
     - alternative2/
       - timestamp/
     - ...
"""


class Simulation(Thread):
    def __init__(self, topology, service, environment, alternative):
        Thread.__init__(self)
        """ Utils objects """
        # Get the object for filesystem handling
        self._fs = FileSystem.get_instance()
        # Logger
        self._log = Logger.get_instance()

        # Root simulation path (simulation/)
        self._root_simulation_path = self._fs.get_simulations_folder()
        # Specific simulation path (simulation/service_name/timestamp/)
        self._simulation_path = None

        # The topology
        self._topology = topology
        # Service to evaluate
        self._service = service
        # The environment in which this simulation is running
        self._environment = environment
        # The alternative of the service to evaluate
        self._alternative = alternative
        # The metrics to evaluate during this simulation
        self._metrics = alternative.get_metrics()
        # Extractor count. This variable is used to keep track of how many extractors notified this object
        self._extractor_number = len(self._metrics)
        self._extractor_count = 0
        # Initialize the simulation
        self._init()

    def __repr__(self):
        return "Simulation[service=%s, alternative=%s]" % (self._service, self._alternative)

    '''
    Private method useful for initialize internal structures of this class.
    '''

    def _init(self):
        # Check if the simulation folder exists
        if not self._fs.path_exists(self._root_simulation_path):
            self._fs.make_dir(self._root_simulation_path)
            self._log.info(self.__class__.__name__, 'Simulation folder misses; it has been just created.')
        else:
            self._log.debug(self.__class__.__name__, 'Simulation folder exists.')
        # Create a folder for this simulation (simulations/service/alternative/) up to the name of the alternative
        alternative_path = self._fs.join(
            self._root_simulation_path, self._service.get_name().lower(), self._alternative.get_name())
        if not self._fs.exists(alternative_path):
            self._log.debug(self.__class__.__name__,
                            'Creating a folder for simulating service %s.', self._service.get_name())
            self._fs.make_dir(alternative_path)
            self._log.info(self.__class__.__name__, 'A folder for simulating service %s has been successfully created.',
                           self._service.get_name())
        else:
            self._log.debug(
                self.__class__.__name__, 'Service folder inside %s already exists; create folders for environment.',
                self._simulation_path)
        # Create the last level of folder (timestamp based)
        self._simulation_path = self._fs.join(alternative_path, time.strftime('%Y%m%d%H%M%S', time.localtime()))
        self._log.debug(self.__class__.__name__, 'Creating folder for this simulation.')
        self._fs.make_dir(self._simulation_path)
        self._log.info(self.__class__.__name__, 'Folder for this simulation has been successfully created.')

    '''
    Return the topology which the simulation is running on.
    '''

    def get_topology(self):
        return self._topology

    '''
    Return the service under test.
    '''

    def get_service(self):
        return self._service

    '''
    Return the alternative under test.
    '''

    def get_alternative(self):
        return self._alternative

    '''
    Return the path in which framework will store all data about this simulation.
    '''

    def get_simulation_path(self):
        return self._simulation_path

    '''
    Execute extractors, if needed
    '''

    def _execute_collectors(self):
        # The list of activated collectors
        activated_collectors = []
        self._log.debug(self.__class__.__name__, 'Preparing the execution of collectors.')
        # First of all, for each metric of this simulation, run a collector if it is needed
        for metric in self._metrics:
            collector = metric.get_collector()
            if collector is not None:
                if collector.get_name() not in activated_collectors:
                    self._log.debug(self.__class__.__name__,
                                    'A new collector %s has been detected; start it.', collector.get_name())
                    collector.start()
                    self._log.debug(self.__class__.__name__,
                                    'Collector %s has been successfully started.', collector.get_name())
                    # Put the collector into the list of activated collectors
                    activated_collectors.append(collector.get_name())
                    self._log.debug(self.__class__.__name__,
                                    'Collector %s has been added to the list of activated collectors.',
                                    collector.get_name())
                else:
                    self._log.debug(self.__class__.__name__,
                                    'Collector %s has been already started.', collector.get_name())
            else:
                self._log.debug(self.__class__.__name__, 'No collectors are required for metric %s.', metric.get_name())
        self._log.info(self.__class__.__name__, 'All collectors have been successfully started.')

    '''
    Start the environment and the alternative's scenario running on top of it
    '''

    def _start_environment(self):
        self._log.debug(self.__class__.__name__, 'Preparing the environment %s to be executed.', self._environment)
        self._environment.run(self._service.get_overlay())
        self._log.debug(self.__class__.__name__, 'Environment %s has been successfully started.', self._environment)

    '''
    Execute extractors for all metrics
    '''

    def _execute_extractors(self):
        self._log.debug(self.__class__.__name__, 'Preparing the execution of all extractors.')
        # At the end of the simulation, run extractor for each metric
        for metric in self._metrics:
            extractor = metric.get_extractor()
            self._log.debug(self.__class__.__name__, 'Extractor %s has been loaded.', extractor.get_name())
            extractor.set_simulation_path(self._simulation_path)
            extractor.set_overlay(self._service.get_overlay())
            extractor.add_observer(self)
            self._log.debug(self.__class__.__name__, 'Extractor %s is now going in execution.', extractor.get_name())
            extractor.start()
            extractor.join()
            self._log.debug(self.__class__.__name__, 'Extractor %s has been successfully started.',
                            extractor.get_name())
        self._log.info(self.__class__.__name__, 'All extractor have been successfully started.')

    '''
    Run the simulation
    '''

    def run(self):
        self._log.debug(self.__class__.__name__, 'Preparing the execution of the simulation.')
        self._execute_collectors()
        self._start_environment()
        self._execute_extractors()
        self._log.info(self.__class__.__name__, 'Simulation has been successfully started.')

    '''
    This method is implemented in accord with Observer pattern. It observes the extractor: when all extractors ends
    their task, the update method will stop the environment.
    '''

    def update(self):
        self._extractor_count += 1
        if self._extractor_count == self._extractor_number:
            self._log.debug(self.__class__.__name__,
                            'All extractors done; starting to stop alternative %s and environment %s.',
                            self._alternative.get_name(), self._environment)
            self._alternative.destroy()     # TODO check it!
            self._log.debug(self.__class__.__name__, 'Alternative %s has been successfully stopped.',
                           self._alternative.get_name())
            self._environment.stop()
            self._log.debug(self.__class__.__name__, 'Environment %s has been successfully stopped.', self._environment)
            self._extractor_count = 0
            self._log.info(self.__class__.__name__, 'Alternative %s and environment %s have been successfully stopped.',
                           self._alternative.get_name(), self._environment)
