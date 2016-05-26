from abc import ABCMeta, abstractmethod
from threading import Thread

import utils.class_for_name as Class
from utils.fs import FileSystem
from utils.log import Logger
from utils.patterns.observer import Observable

"""
Factory for creating extractors' object.
"""


class FactoryExtractor(object):
    __instance = None

    def __init__(self):
        # Logger
        self._log = Logger.get_instance()
        # The reference to the extractor object
        self._extractor = None

    '''
    In accord with Singleton pattern, it returns an instance of this class.
    '''

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = FactoryExtractor()
        return cls.__instance

    '''
    Starting from the name of extractor class and the environment which this extractor will run on, it creates a
    extractor object.
    '''

    def create_extractor(self, extractor_name, environment):
        self._log.info(self.__class__.__name__, 'Starting to create extractor %s for environment %s',
                       extractor_name, environment)
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
        parts = extractor_name.split('.')
        self._log.debug(self.__class__.__name__, 'Isolating class name.')
        # Take the last one, namely the class_name
        class_name = parts[len(parts) - 1]
        self._log.debug(self.__class__.__name__, 'Extractor to load: %s.', environment + class_name)
        # Concat the environment name, obtaining EnvironmentClassName (e.g. MininetLoadDevice)
        parts[len(parts) - 1] = environment + class_name
        # Join the list into a class with modules (e.g. module.module.module.ClassName)
        extractor_class_name = '.'.join(parts)
        self._log.debug(self.__class__.__name__, 'Creating a new instance for %s', extractor_class_name)
        # Load an instance
        self._extractor = Class.for_name(extractor_class_name)
        self._log.info(self.__class__.__name__, 'Extractor %s has been successfully created.', extractor_class_name)
        return self._extractor


"""
Abstract class that model an extractor. An Extractor extends both Thread and Observable object: Thread because the
extraction is ran in a separated thread with respect to the execution of the environment; Observable because when
extraction finishes, the extractor notify its observer for stopping the environment.
"""


class Extractor(Thread, Observable):
    __metaclass__ = ABCMeta

    def __init__(self):
        Thread.__init__(self)
        # This extractor is a observable object, due to the fact that upon extraction finishes, other actions will be
        # undertaken
        Observable.__init__(self)
        # Logger
        self._log = Logger.get_instance()
        # The FileSystem handler
        self._fs = FileSystem.get_instance()
        # The simulation path
        self._simulation_path = None
        # The overlay
        self._overlay = None

    '''
    Return the name of this collector.
    '''

    def get_name(self):
        return self.__class__.__name__

    '''
    This method implements the strategy for collecting data.
    '''

    @abstractmethod
    def extract_data(self):
        pass
