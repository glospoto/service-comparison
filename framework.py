import argparse
import os.path

from utils.fs import FileSystem
from utils.log import Logger
from utils.parser.parser import Parser

from loader.environment import EnvironmentLoader
from model.topology.topology import Topology
from model.simulation import Simulation

"""
This is the main framework's class. It has in charge the orchestration of the different operations of the
framework.
"""


class ComparisonFramework(object):
    def __init__(self):
        # Get a logger
        self._log = Logger.get_instance()
        # Get a file system handler
        self._fs = FileSystem.get_instance()
        # Create the parser
        self._parser = Parser()
        # The topology
        self._topology = None
        # Factory loader. For each alternative, a new environment is loaded accordngly with the alternative itself.
        self._loader = EnvironmentLoader()

        # ArgParse
        self._arg = argparse.ArgumentParser(description='Comparison Framework')
        self._arg.add_argument('-c',
                               '--config-file',
                               required=True,
                               help='The framework configuration file.')
        self._arg.add_argument('-t',
                               '--topology',
                               required=True,
                               help='The topology on which framework runs. It must be a GraphML file.')

    def __repr__(self):
        return "Comparison Framework v. 0.1"

    '''
    Initialize the framework, namely take arguments, create the topology and parse the configuration file.
    '''

    def _init(self):
        args = self._arg.parse_args()
        config_file = str(args.config_file)
        topology = str(args.topology)
        topology_path = self._fs.get_absolute_path(topology)
        self._log.info(self.__class__.__name__, 'Creating the topology.')
        self._topology = Topology(topology_path)

        # Parse config_file
        self._log.info(self.__class__.__name__, 'Parsing configuration file.')
        self._parser.parse(config_file)

    '''
    Run the framework
    '''

    def run(self):
        self._init()

        # Run simulation: for each service to evaluate, create a simulation and delegate to the loader 
        # objects the decision about the environment to load based on the alternatives
        services = self._parser.get_services()

        for service in services:
            # For each service, create the overlay. This overlay will be used for all alternatives of the given service
            self._log.debug(self.__class__.__name__, 'Creating overlay for service %s.', service.get_name())
            service.create_overlay(self._topology.get_topology())
            self._log.info(self.__class__.__name__, 'Overlay for service %s has been successfully created.',
                           service.get_name())

            # Create the scenario for the service
            self._log.debug(self.__class__.__name__, 'Building scenario for service %s.', service.get_name())
            service.build_scenario()
            self._log.info(self.__class__.__name__, 'Scenario %s has been correctly built.', service.get_scenario())

            # For each alternative of this service, create a simulation
            for alternative in service.get_alternatives():
                '''
                Loading environment, creating the simulation and running it.
                '''
                self._log.debug(self.__class__.__name__, 'Loading the environment for the alternative %s.',
                                alternative)
                # Load an environment for the current alternative of this service
                environment = self._loader.load(alternative.get_environment())
                self._log.info(self.__class__.__name__,
                               'Environment %s for the alternative %s has been successfully loaded.',
                               environment, alternative.get_name())

                # Create the simulation
                self._log.debug(self.__class__.__name__,
                                'Starting to create a simulation for service %s and alternative %s.',
                                service.get_name(), alternative)
                simulation = Simulation(self._topology, service, environment, alternative)
                self._log.info(self.__class__.__name__,
                               'A new simulation has been created for service %s and alternative %s.',
                               service.get_name(), alternative)
                # Run the simulation
                self._log.debug(self.__class__.__name__, 'Running the simulation.')
                simulation.start()
                simulation.join()
                self._log.info(self.__class__.__name__, 'Simulation has been successfully run.')

            self._log.info(self.__class__.__name__, 'All alternatives for service %s have been successfully tested.',
                           service.get_name())

        self._log.info(self.__class__.__name__, 'All services have been successfully tested; framework will stop.')
