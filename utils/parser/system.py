import sys
import xml.etree.ElementTree as XmlParser

from utils.log import Logger

"""
This class implements a parser for conf/system.xml file. That file contains all available alternatives, all association
between alternatives and environments, namely in which environment an alternative can be execute and all available
metrics.
"""


class SystemParser(object):
    def __init__(self):
        # Reference to the file to parse
        self._parser = XmlParser.parse('conf/system.xml')
        # Logger
        self._log = Logger.get_instance()
        # All services. This is a map<name, parser_adapter>
        self._services = {}
        # Mapping between services and alternatives. This is a map<service_name, list(alternative_name)>
        self._service_to_alternatives = {}
        # All alternatives. This is a map<name, alternative_adapter>
        self._alternatives = {}
        # All metrics. This is a list
        self._metrics = []
        # Mapping between metric and collector adapter. This is a map<metric_name, collector_adapter_name>
        self._metric_to_collector = {}
        # Mapping between metric and extractor adapter. This is a map<metric_name, extractor_adapter_name>
        self._metric_to_extractor = {}
        # All environments. This is a map<env_name, adapter>
        self._environments = {}
        # Mapping between environments and alternatives. This is a map<env_name, list(alternative_name)>
        self._environment_to_alternatives = {}

    '''
    This method return a parser for the given service
    '''
    def get_service_parser(self, service_name):
        return self._services.get(service_name)

    '''
    This method return an adapter for the given alternative
    '''
    def get_alternative_adapter(self, alternative_name):
        return self._alternatives.get(alternative_name)

    '''
    This method return an environment adapter
    '''
    def get_environment_adapter(self, environment_name):
        return self._environments.get(environment_name)

    '''
    This method return an extractor adapter
    '''
    def get_extractor_adapter(self, metric_name):
        return self._metric_to_extractor.get(metric_name)

    '''
    This method return a collector adapter
    '''
    def get_collector_adapter(self, metric_name):
        return self._metric_to_collector.get(metric_name)

    '''
    Check if a service is valid in accord with system.xml file
    '''
    def service_is_valid(self, service_name):
        return service_name in self._services.keys()

    '''
    Check if an alternative is valid in accord with the system.xml file
    '''
    def alternative_is_valid(self, alternative_name):
        return alternative_name in self._alternatives.keys()

    '''
    Check if an environment is valid in accord with the system.xml file
    '''
    def environment_is_valid(self, environment_name):
        return environment_name in self._environments.keys()

    '''
    Check if alternative can be executed into environment
    '''
    def mapping_alternative_to_environment_is_valid(self, alternative, environment):
        success = False
        # Try to catch tha alternative list supported by environment
        alternatives = self._environment_to_alternatives.get(environment, None)
        if alternatives is not None:
            if alternative in alternatives:
                success = True
        return success

    '''
    Parse the system.xml file, loading services, alternatives, metrics and environments.
    '''
    def parse(self):
        root = self._parser.getroot()
        # Get all macro-block from the root
        services = root.find('services')
        metrics = root.find('metrics')
        environments = root.find('environments')

        self._parse_services(services)
        self._parse_metrics(metrics)
        self._parse_environments(environments)

    '''
    Method for parsing all services
    '''
    def _parse_services(self, services):
        self._log.info(self.__class__.__name__, 'Parsing services.')
        # For each service, add an entry into _services map
        for service in services:
            name = service.attrib.get('name')
            parser = service.attrib.get('parser')
            if name in self._services.keys():
                self._log.error(self.__class__.__name__,
                                'Service %s has been already defined; please, use another name.', name)
                sys.exit(-1)
            self._log.debug(self.__class__.__name__, 'Service %s has been loaded.', name)
            self._services[name] = parser
            # Now parse all alternatives for this service
            self._parse_alternatives_for_service(service, name)

    '''
    Support method for parsing services' alternatives
    '''
    def _parse_alternatives_for_service(self, service, service_name):
        self._log.info(self.__class__.__name__, 'Parsing alternatives for service %s.', service_name)
        # Take alternatives for this service
        alternatives = service.find('alternatives')
        # For each alternative, add an entry into _alternatives map
        for alternative in alternatives:
            name = alternative.attrib.get('name')
            # If alternative's name is already defined, report error and exit.
            if name in self._alternatives:
                self._log.error(self.__class__.__name__,
                                'Alternative %s has been already defined; please, use another name.', name)
                sys.exit(-1)
            # If alternative's name is correct, continue to parse the alternative
            self._log.debug(self.__class__.__name__, 'Alternative %s has been loaded.', name)
            # Load alternative's adapter
            adapter = alternative.attrib.get('adapter')
            self._log.debug(self.__class__.__name__, 'Alternative adapter %s for alternative %s has been loaded.',
                            adapter, name)
            # Add this alternative to the map of alternatives
            self._alternatives[name] = adapter
            # Finally, add alternative to the list of alternatives of this service
            # Get alternatives for this service
            alternatives_for_service = self._service_to_alternatives.get(service_name, None)
            # If alternatives_for_service is None, create the list and add the alternative
            if alternatives_for_service is None:
                alternatives_for_service = [name]
            # Otherwise, take the list and append the alternative name
            else:
                alternatives_for_service.append(name)
            # Re-add the list to the service_to_alternatives map
            self._service_to_alternatives[service_name] = alternatives_for_service

    '''
    Method for parsing all metrics
    '''
    def _parse_metrics(self, metrics):
        # For each metric, add an entry into _metrics map
        for metric in metrics:
            name = metric.attrib.get('name')
            # If alternative's name is already defined, report error and exit.
            if name in self._metrics:
                self._log.error(self.__class__.__name__,
                                'Metric %s has been already defined; please, use another name.', name)
                sys.exit(-1)
            # If metric's name is correct, continue to parse the metric
            self._log.debug(self.__class__.__name__, 'Metric %s has been loaded.', name)
            self._metrics.append(name)
            # Load extractor adapter
            extractor_adapter = metric.attrib.get('extractor_adapter')
            self._log.debug(self.__class__.__name__, 'Extractor adapter %s for metric %s has been loaded.',
                            extractor_adapter, name)
            self._metric_to_extractor[name] = extractor_adapter
            # Try to load the collector adapter (an alternative may not have a collector)
            collector_adapter = metric.attrib.get('collector_adapter')
            if collector_adapter is not None:
                self._log.debug(self.__class__.__name__, 'Collector adapter %s for metric %s has been loaded.',
                                collector_adapter, name)
                self._metric_to_collector[name] = collector_adapter
            else:
                self._log.debug(self.__class__.__name__, 'Metric %s has not a collector adapter.', name)

    '''
    Method for parsing all environments
    '''
    def _parse_environments(self, environments):
        self._log.info(self.__class__.__name__, 'Parsing environments.')
        # For each environment, add entries into _environments and environment_to_alternatives' maps
        for environment in environments:
            name = environment.attrib.get('name')
            adapter = environment.attrib.get('adapter')
            # If environment's name is already defined, report error and exit.
            if name in self._environments.keys():
                self._log.error(self.__class__.__name__,
                                'Environment %s has been already defined; please, use another name.', name)
                sys.exit(-1)
            self._log.debug(self.__class__.__name__, 'Environment %s with adapter %s has been loaded.', name, adapter)
            self._environments[name] = adapter
            mappings = environment.findall('alternative')
            alternatives = []
            for mapping in mappings:
                alternative_name = mapping.attrib.get('name')
                alternatives.append(alternative_name)
                self._log.debug(self.__class__.__name__, 'Alternatives %s are going to added to environment %s.',
                                alternatives, name)
            self._environment_to_alternatives[name] = alternatives
