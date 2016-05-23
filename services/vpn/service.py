from model.service import Service
import utils.class_for_name as Class

"""
This class specializes class Service for VPN service. It has in charge the task of creating the alternatives under test
for this service.
"""


class VpnService(Service):
    def __init__(self, name):
        Service.__init__(self, name)

    '''
    Creating an alternative object starting from its adapter
    '''

    def create_alternative(self, alternative_name, alternative_adapter, scenario_parameters):
        self._log.info(self.__class__.__name__, 'Creating alternative %s.', alternative_name)
        # The pattern of params for the for_name method is: adapter, name of the alternative and all parameters defined
        # in the configuration file
        alternative = Class.for_name(alternative_adapter, name=alternative_name, scenario=scenario_parameters)
        # Add the alternative to the list of alternatives
        self._alternatives.append(alternative)
        self._log.debug(self.__class__.__name__, 'Adding alternative %s to the list of alternatives of service %s.',
                        alternative_name, self._name)
        self._log.info(self.__class__.__name__, 'Alternative %s has been correctly created.', alternative_name)
        return alternative
