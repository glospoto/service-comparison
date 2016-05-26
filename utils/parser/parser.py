import os
import sys
from configobj import ConfigObj

from collector.collector import FactoryCollector
from collector.extractor import FactoryExtractor
from model.metric import Metric
from utils.parser.system import SystemParser
from utils.parser.services import FactoryServiceParser
from utils.log import Logger

"""
This class implements a parser for framework configuration file
"""


class Parser(object):
    def __init__(self):
        # Logger
        self._log = Logger.get_instance()
        # ConfigObj reference
        self._parser = None
        # System configuration parser
        self._system_parser = SystemParser()
        # Service parser factory
        self._factory_service_parser = FactoryServiceParser.get_instance()
        # The service specific parser
        self._service_parser = None
        # The factories for the creation of extractors and collectors
        self._factory_extractor = FactoryExtractor.get_instance()
        self._factory_collector = FactoryCollector.get_instance()
        # All services expressed in the configuration file. Each service is an instance of model.service.Service
        self._services = []

    def __repr__(self):
        return "Parser[ComparisonFramework]"

    '''
    Return the list of all services defined in the configuration file.
    '''

    def get_services(self):
        return self._services

    '''
    This method has in charge the task of parsing the configuration file.
    '''

    def parse(self, config_file):
        # First of all, run the SystemParser
        self._system_parser.parse()
        # Load the configuration file
        configuration_file = os.path.abspath(config_file)
        self._log.debug(self.__class__.__name__, 'Checking if config file %s exists.', configuration_file)
        if os.path.isfile(configuration_file):
            self._log.info(self.__class__.__name__, 'Loading configuration from %s.', configuration_file)
            # Take the absolute path of the configuration file
            self._parser = ConfigObj(infile=configuration_file)
        else:
            self._log.error(self.__class__.__name__,
                            'File %s does not exist; please try again with a valid configuration file.', config_file)
            sys.exit(-1)

        '''
        Starting to load services
        '''
        self._log.debug(self.__class__.__name__, 'Loading services.')
        framework = self._parser['Framework']
        # Variable services contains all services declared in the framework input file corresponding to the section
        # [Framework]
        services = framework['services']
        '''
        Check if configuration file just contains one service or more. Here the problem is that ConfigObj returns
        a string if the value of a key is just an element; it returns a list otherwise. In the former case, transform
        it as a string
        '''
        if not isinstance(services, list):
            s = services
            services = [s]  # Now services list contains all services' name as strings

        # Check if all services declared into framework.cfg are valid.
        self._check_services(services)

        # Load association between alternatives and environments (note that an alternative can be ran in more than one
        # environment
        self._log.debug(self.__class__.__name__, 'Loading environments.')

        '''
        For each service, create a Service object with its alternatives and metrics. Here I'm sure that the service
        is valid (it has been already checked).
        '''
        for service_name in services:
            # Replace space that may be present in the service name
            service_name = service_name.replace(' ', '')
            self._log.debug(self.__class__.__name__,
                            'Service %s is available: create the specific parser.', service_name)
            # Create the specialized service parser
            service_parser = self._system_parser.get_service_parser(service_name)
            self._service_parser = self._factory_service_parser.create_service_parser(service_parser, service_name)
            self._log.info(self.__class__.__name__,
                           'Specialized service parser %s has been successfully created.', self._service_parser)
            # Create the service. Variable s contains an instance of class model.service.Service
            service = self._service_parser.create_service()

            '''
            Load alternatives and metrics based on this service name
            '''
            # service_block is the piece of configuration file containing all stuff related to a service
            service_block = self._parser[service_name]
            # Take alternatives and metrics for this service
            self._log.debug(self.__class__.__name__, 'Loading alternatives for service %s.', service_name)
            alternatives = service_block['alternatives']
            # If the alternative is just one, the ConfigObj does not return a list, but a single object: transform
            # it into a list
            if not isinstance(alternatives, list):
                alternatives = [alternatives]
            self._log.debug(self.__class__.__name__, 'Loading metrics for service %s.', service_name)
            metrics = service_block['metrics']
            # If the metric is just one, the ConfigObj does not return a list, but a single object: transform it
            # into a list
            if not isinstance(metrics, list):
                metrics = [metrics]
            self._log.debug(self.__class__.__name__, 'Loading scenario for service %s.', service_name)
            # Load scenario based on the section 'Scenario' of this service
            # s is an instance of class Service; service is the "configuration block" of the configuration file
            # from which retrieve other configuration information (like alternatives) and alternatives is the list
            # of alternatives declared in the [Service] section in the configuration file.
            self._handle_alternative_and_metric_for_service(service, service_block, alternatives, metrics)
            # Delegate to the specific service parser the ability of parsing the specific scenario
            self._service_parser.parse_scenario(service_block['scenario'])

            '''
            Service has been correctly created: add in to the list of all services
            '''
            self._services.append(service)
            self._log.info(self.__class__.__name__, 'Service %s has been successfully created.', s)

    '''
    Check if all services' names are valid.
    '''

    def _check_services(self, services):
        for service in services:
            if not self._system_parser.service_is_valid(service):
                self._log.error(self.__class__.__name__, 'Service %s is not a valid service; please check its name.',
                                service)
                sys.exit(-1)

    '''
    Check if the association between alternative and environment specified as parameters is correct in accord with
    the associations declared into the file system.xml. Actually, this method also checks if alternatives and
    environments are valid in accord with the system.xml file.
    '''

    def _check_mapping_alternative_to_environment(self, alternative, environment):
        # Check alternative name
        if not self._system_parser.alternative_is_valid(alternative):
            self._log.error(self.__class__.__name__,
                            'Alternative %s is not a valid alternative; please check its name', alternative)
            sys.exit(-1)

        # Check environment name
        if not self._system_parser.environment_is_valid(environment):
            self._log.error(self.__class__.__name__,
                            'Environment %s is not a valid environment; please check its name', environment)
            sys.exit(-1)

        # Now, check if mapping between alternative and environment is correct.
        if self._system_parser.mapping_alternative_to_environment_is_valid(alternative, environment):
            self._log.error(
                self.__class__.__name__,
                'Alternative %s cannot be executed into environment %s; please check your configuration file.',
                alternative, environment)
            sys.exit(-1)

    '''
    This method has in charge the task of creating alternative objects for the service passed as parameter; moreover,
    on that alternative, it has also in charge the task of creating the corresponding scenario
    '''

    def _handle_alternative_and_metric_for_service(self, service, service_block, alternatives, metrics):
        for alternative_name in alternatives:
            # Load the specific parameters for the current alternative
            alternative_parameters = service_block[alternative_name]
            # For each alternative, take the adapter and create the alternative object (represented by adapter in
            # system.xml)
            # Take the adapter for the current alternative
            alternative_adapter = self._system_parser.get_alternative_adapter(alternative_name)
            alternative = service.create_alternative(alternative_name, alternative_adapter, alternative_parameters)
            self._log.info(self.__class__.__name__, 'Alternative %s has been created.', alternative_name)

            # Based on the content of self._environments parsed from configuration file, set the class name of the
            # environment to the alternative object
            environment_name = alternative_parameters['environment']
            # Check the correctness of the association between alternative and environment
            self._check_mapping_alternative_to_environment(alternative_name, environment_name)
            self._log.info(self.__class__.__name__,
                           'Environment %s is valid for alternative %s.', environment_name, alternative_name)
            environment = self._system_parser.get_environment_adapter(environment_name)
            alternative.set_environment(environment)
            self._log.info(self.__class__.__name__,
                           'Environment %s has been successfully associated to alternative %s.',
                           environment_name, alternative_name)

            # Now, for each alternative, handle metrics
            self._handle_metrics_for_alternative(alternative, environment_name, metrics)

    '''
    This method has in charge the task of creating metric objects alternative passed as parameter.
    '''

    def _handle_metrics_for_alternative(self, alternative, environment, metrics):
        for metric_name in metrics:
            self._log.info(self.__class__.__name__, 'Loading metric %s.', metric_name)
            # Load the extractor and collector adapters. They are strings, because the extractor and collector are based
            # both on the metric and the environment to use
            extractor_adapter = self._system_parser.get_extractor_adapter(metric_name)
            # Load the actual adapter, based on this metric and the environment for the selected alternative
            extractor_class = self._factory_extractor.create_extractor(extractor_adapter, environment)
            self._log.info(self.__class__.__name__, 'Extractor %s has been successfully created.', extractor_adapter)
            collector_adapter = self._system_parser.get_collector_adapter(metric_name)
            if collector_adapter is not None:
                collector_class = self._factory_collector.create_collector(collector_adapter, environment)
                self._log.info(self.__class__.__name__, 'Collector %s has been successfully created.',
                               collector_adapter)
            else:
                collector_class = None
                self._log.info(self.__class__.__name__, 'Extractor %s does not need any collectors.', extractor_adapter)
            # Create the metric
            metric = Metric(metric_name, collector_class, extractor_class)
            self._log.info(self.__class__.__name__, 'Metric %s has been successfully created.', metric)
            alternative.add_metric(metric)
            self._log.info(self.__class__.__name__,
                           'Metric %s has been successfully associated to the alternative %s.',
                           metric.get_name(), alternative.get_name())
