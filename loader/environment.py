from abc import ABCMeta, abstractmethod

from loader.env.mininet_simulator import MininetTopology, MininetStartSimulation
from loader.env.docker_simulator import Docker
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


"""
This class models a Docker environment, namely an environment in which each node in the network is an instance of a
docker container.
"""


class DockerEnvironment(Environment):
    def __init__(self):
        Environment.__init__(self)
        # Running instances
        self._running_docker_instances = []

    def __repr__(self):
        return self.__class__.__name__

    '''
    This method implements the steps for running this environment.
    '''

    def run(self, overlay):
        self._log.info(self.__class__.__name__, 'Initializing the environment.')
        self._log.info(self.__class__.__name__, 'Starting to create a Docker instance for each node in the overlay.')
        # Create the network
        for node in overlay.get_nodes().values():
            self._log.debug(self.__class__.__name__, 'Creating Docker container for node %s.', node.get_name())
            instance = Docker(node.get_name(), 'scf:v2', '--privileged=True')
            # Add the instance to those running
            self._running_docker_instances.append(instance)
            instance.create()
            self._log.debug(self.__class__.__name__, 'Container for node %s has been correctly created.',
                            node.get_name())
        self._log.info(self.__class__.__name__, 'All Docker instances are now successfully created.')
        # Run all docker instances
        self._log.info(self.__class__.__name__, 'Starting all Docker instances.')
        for instance in self._running_docker_instances:
            self._log.debug(self.__class__.__name__, 'Starting Docker container for node %s.', instance.get_name())
            instance.start()
            self._log.debug(self.__class__.__name__, 'Docker container %s has been successfully started.',
                            instance.get_name())
        self._log.info(self.__class__.__name__, 'All Docker instances are now successfully running.')

    '''
    This method implements the steps for stopping this environment.
    '''

    def stop(self):
        self._log.info(self.__class__.__name__, 'Stopping the environment.')
        for instance in self._running_docker_instances:
            instance.stop()
            instance.remove()
            self._log.debug(self.__class__.__name__, 'Container for node %s has been correctly stopped.',
                            instance.get_name())
        self._log.info(self.__class__.__name__, 'All Docker instances are now successfully stopped.')
