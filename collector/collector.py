from abc import ABCMeta, abstractmethod
from threading import Thread

import utils.class_for_name as Class
from utils.fs import FileSystem
from utils.log import Logger

"""
Factory for creating extractors' object.
"""


class FactoryCollector(object):
    __instance = None

    def __init__(self):
        # Logger
        self._log = Logger.get_instance()
        # The reference to the collector object
        self._collector = None

    '''
    In accord with Singleton pattern, it returns an instance of this class.
    '''

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = FactoryCollector()
        return cls.__instance

    '''
    Starting from the name of collector class and the environment which this collector will run on, it creates a
    collector object.
    '''

    def create_collector(self, collector_name, environment):
        self._log.info(self.__class__.__name__, 'Starting to create collector %s for environment %s',
                       collector_name, environment)
        '''
        Each extractor depends on the metric to extract and the environment in which the simulation is running. In
        general, each environment has its own way for extracting data, so there will be more implementation for
        the same metric. By convention, a class that models an extractor for a specific environment is called as follow:
        Environment+Metric. For example, to extract device-load metric from mininet, the class will be called
        MininetDeviceLoad. So, for instantiating the extractor, just concatenate the parameter environment to the
        last part of extractor name
        '''
        self._log.debug(self.__class__.__name__, 'Splitting class module.')
        # Split into a list [module, module, module, ..., class_name]
        parts = collector_name.split('.')
        self._log.debug(self.__class__.__name__, 'Isolating class name.')
        # Take the last one, namely the class_name
        class_name = parts[len(parts) - 1]
        self._log.debug(self.__class__.__name__, 'Collector to load: %s.', environment + class_name)
        # Concat the environment name, obtaining EnvironmentClassName (e.g. MininetLoadDevice)
        parts[len(parts) - 1] = environment + class_name
        # Join the list into a class with modules (e.g. module.module.module.ClassName)
        collector_class_name = '.'.join(parts)
        self._log.debug(self.__class__.__name__, 'Creating a new instance for %s', collector_class_name)
        # Load an instance
        self._collector = Class.for_name(collector_class_name)
        self._log.info(self.__class__.__name__, 'Collector %s has been successfully created.', collector_class_name)
        return self._collector


"""
Abstract class that model a collector. A Collector extends Thread: this implies that each collector will be executed in
a separated thread with respect to the execution of the environment.
"""


class Collector(Thread):
    __metaclass__ = ABCMeta

    def __init__(self):
        Thread.__init__(self)
        # Logger
        self._log = Logger.get_instance()
        # Logger
        self._fs = FileSystem.get_instance()

    '''
    Return the name of this collector.
    '''

    def get_name(self):
        return self.__class__.__name__

    '''
    This method implements the strategy for collecting data.
    '''

    @abstractmethod
    def collect_data(self):
        pass
