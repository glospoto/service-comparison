from abc import ABCMeta, abstractmethod

from utils.fs import FileSystem
from utils.log import Logger

"""
This class models a basic scenario object. A scenario is a collection of information defined in the configuration file;
through the manipulation of those information, this class will be able to run different components.
"""


class Scenario(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # The reference to the FileSystem object, useful for writing configuration in tmp folder
        self._fs = FileSystem.get_instance()
        # Logger
        self._log = Logger.get_instance()

    '''
    Return the name of this scenario.
    '''

    @abstractmethod
    def get_name(self):
        pass

    '''
    Start this scenario.
    '''

    @abstractmethod
    def create(self, overlay):
        pass

    '''
    Destroy this scenario
    '''

    @abstractmethod
    def destroy(self):
        pass
