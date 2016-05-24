from abc import ABCMeta, abstractmethod

from utils.fs import FileSystem
from utils.log import Logger

"""
This class models a generic configurator.
"""


class Configurator(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # FileSystem handler
        self._fs = FileSystem.get_instance()
        # Logger
        self._log = Logger.get_instance()

    '''
    Return the name of this configurator.
    '''

    @abstractmethod
    def get_name(self):
        pass
