from abc import ABCMeta, abstractmethod

from loader.env.mininet_simulator import MininetTopology, MininetStartSimulation
import utils.class_for_name as Class
from utils.log import Logger

"""
This class has in charge the task to load the environment.
"""


class EnvironmentLoader(object):

    def __init__(self):
        # self._factory_loader = FactoryLoader()
        self._log = Logger.get_instance()

    def __repr__(self):
        return "EnvironmentLoader"

    '''
    This method loads an environment starting from its class name.
    '''
    def load(self, environment_class_name):
        environment = Class.for_name(environment_class_name)
        self._log.info(
            'EnvironmentLoader', 'Environment %s has been loaded.', environment_class_name)
        return environment

"""
This class models a generic environment.
"""


class Environment(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # Get a logger
        self._log = Logger.get_instance()

    '''
    This method implements the steps for running this environment.
    '''
    @abstractmethod
    def run(self, overlay):
        pass


"""
This class models a Mininet environment, namely an environment in which the creation of configuration files consists
in generating both network script and VPN configuration files in accord with the controller and starting Mininet
itself and controller.
"""


class MininetEnvironment(Environment):
    def __init__(self):
        Environment.__init__(self)
        # Object for directly handler Mininet environment
        self._mininet_topology = None
        self._mininet_starter = None

    def __repr__(self):
        return self.__class__.__name__

    '''
    This method implements the steps for running this environment.
    '''
    def run(self, overlay):
        self._log.info(self.__class__.__name__, 'Initializing the environment')
        self._log.debug(self.__class__.__name__, 'Creating the topology in Mininet, starting from the current overlay.')
        # Create the network
        self._mininet_topology = MininetTopology(overlay)
        self._log.debug(self.__class__.__name__, 'Adding switches to Mininet.')
        # Add switch to the MininetTopology
        self._mininet_topology.add_switches()
        self._log.debug(self.__class__.__name__, 'Adding hosts to Mininet.')
        # Add host to the MininetTopology
        self._mininet_topology.add_hosts()
        self._log.debug(self.__class__.__name__, 'Adding links to Mininet.')
        # Add links to MininetTopology
        self._mininet_topology.add_links()
        # Create a MininetStartSimulationObject
        self._log.debug(self.__class__.__name__, 'Starting a Mininet environment.')
        self._mininet_starter = MininetStartSimulation(self._mininet_topology)
        self._mininet_starter.start()
        self._log.debug(self.__class__.__name__, 'Mininet is now correctly running.')

    '''
    This method implements the steps for stopping this environment.
    '''
    def stop(self):
        self._mininet_starter.stop()
