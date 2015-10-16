from abc import ABCMeta, abstractmethod

from utils.log import Logger

"""
This abstract class models an alternative for the services.
"""


class Alternative(object):

    __metaclass__ = ABCMeta

    def __init__(self, name):
        # Logger
        self._log = Logger.get_instance()
        # The name of the alternative
        self._name = name

    '''
    Return the name of the alternative.
    '''
    def get_name(self):
        return self._name

    '''
    Create a scenario for this alternative.
    '''
    @abstractmethod
    def create_overlay(self):
        pass

    '''
    Return the overlay associated to this alternative.
    '''
    @abstractmethod
    def get_overlay(self):
        pass

    '''
    Setting up the scenario for this alternative.
    '''
    @abstractmethod
    def setting_up_scenario(self):
        pass

    '''
    Return the scenario associated to this alternative.
    '''
    @abstractmethod
    def get_scenario(self):
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

    '''
    Set the environment for this alternative.
    '''
    @abstractmethod
    def set_environment(self, environment):
        pass

    '''
    Return the environment associated to this alternative.
    '''
    @abstractmethod
    def get_environment(self):
        pass

    '''
    Add a metric to evaluate for this alternative.
    '''
    @abstractmethod
    def add_metric(self, metric):
        pass

    '''
    Return all metrics associated to this alternative.
    '''
    @abstractmethod
    def get_metrics(self):
        pass
