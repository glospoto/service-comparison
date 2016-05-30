from abc import ABCMeta, abstractmethod

from utils.fs import FileSystem
from utils.log import Logger

"""
This abstract class models an alternative for the services.
"""


class Alternative(object):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        # Logger
        self._log = Logger.get_instance()
        # FileSystem
        self._fs = FileSystem.get_instance()
        # The name of the alternative
        self._name = name
        # This is a string reference to the class that models the environment. This is NOT a reference to the object!
        self._environment = None
        # Metrics to consider for this alternative. This is a list of model.metric.Metric objects
        self._metrics = []

    '''
    Return the name of the alternative.
    '''

    def get_name(self):
        return self._name

    '''
    Set the environment for this alternative.
    '''

    def set_environment(self, environment):
        self._environment = environment

    '''
    Return the environment associated to this alternative.
    '''

    def get_environment(self):
        return self._environment

    '''
    Add a metric to evaluate for this alternative.
    '''

    def add_metric(self, metric):
        self._metrics.append(metric)

    '''
    Return all metrics associated to this alternative.
    '''

    def get_metrics(self):
        return self._metrics

    '''
    Deploy this alternative over a given scenario
    '''

    @abstractmethod
    def deploy(self, overlay, scenario):
        pass

    '''
    Destroy the scenario associated to this alternative.
    '''

    @abstractmethod
    def destroy(self):
        pass

    '''
    Return the configurator for this alternative.
    '''

    @abstractmethod
    def get_configurator(self):
        pass
