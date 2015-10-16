import argparse
import os.path

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
        # Create the parser
        self._parser = Parser()
        # The topology
        self._topology = None
        # Factory loader. For each alternative, a new environment is loaded in accord with the alternative itself.
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
        topology_path = os.path.abspath(topology)
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

        # Run simulation: for each service to evaluate, create a simulation and delegate to the loader objects
        # the decision about the environment to load based on the alternatives
        services = self._parser.get_services()

        for service in services:
            # For each alternative of this service, create a simulation
            for alternative in service.get_alternatives():
                '''
                Creating overlay and adding it to the topology object.
                '''
                self._log.info(self.__class__.__name__, 'Creating overlay for alternative %s.', alternative.get_name())
                # Creating the overlay for current alternative
                overlay = alternative.create_overlay(self._topology.get_topology_from_graphml())
                self._log.info(self.__class__.__name__, 'Adding overlay %s for alternative %s to the topology.',
                               overlay.get_name(), alternative.get_name())
                self._topology.add_overlay(overlay)

                '''
                Loading environment, creating the simulation and running it.
                '''
                self._log.info(self.__class__.__name__, 'Loading the environment for the alternative %s.', alternative)
                # Load an environment for the current alternative of this service
                environment = self._loader.load(alternative.get_environment())
                # Create the simulation
                simulation = Simulation(self._topology, service, environment, alternative)
                self._log.info(
                    self.__class__.__name__,
                    'A new simulation has been created for service %s and alternative %s.',
                    service.get_name(), alternative)
                # Run the simulation
                simulation.start()
                simulation.join()

            self._log.info(self.__class__.__name__, 'All alternatives for service %s have been successfully tested.',
                           service.get_name())

        self._log.info(self.__class__.__name__, 'All services have been successfully tested; framework will stop.')
