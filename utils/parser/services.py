from abc import ABCMeta, abstractmethod

from utils.log import Logger
import utils.class_for_name as Class

"""
This file contains all specialized parser for services. Moreover, there is a factory for creating the correct service
parser
"""

"""
This class implements a factory for creating the correct specialized service parser in accord with the service's name
"""


class FactoryServiceParser(object):
    __instance = None

    def __init__(self):
        self._service_parser = None

    def __repr__(self):
        return 'FactoryServiceParser.'

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = FactoryServiceParser()
        return cls.__instance

    '''
    Create an instance of service parser identified by the service_adapter passed as paramter.
    '''

    def create_service_parser(self, service_adapter, service_name):
        self._service_parser = Class.for_name(service_adapter, service_name)
        return self._service_parser


"""
This class models a generic service parser
"""


class ServiceParser(object):
    __metaclass__ = ABCMeta

    def __init__(self, service_name):
        # Logger
        self._log = Logger.get_instance()
        # The service's name
        self._service_name = service_name

    '''
    Create the service.
    '''

    @abstractmethod
    def create_service(self):
        pass
