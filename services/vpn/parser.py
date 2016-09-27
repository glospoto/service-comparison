from services.vpn.service import VpnService
from utils.parser.services import ServiceParser

"""
This class models a parser specialized in the creation of VPN service
"""


class VpnServiceParser(ServiceParser):
	def __init__(self, service_name):
		ServiceParser.__init__(self, service_name)
		# The service
		self._service = None

	def __repr__(self):
		return self.__class__.__name__

	'''
	This method has in charge the task of creating the specific service.
	'''

	def create_service(self):
		self._log.debug(
			self.__class__.__name__, 'Creating service object for service %s.', self._service_name)
		service = VpnService(self._service_name)
		self._log.info(
			self.__class__.__name__, 
			'Service object for service %s has been successfully created.', self._service_name)
		self._service = service
		return service

	'''
	Parse specific scenario of this service
	'''

	def parse_scenario(self, scenario_params):
		self._log.debug(
			self.__class__.__name__, 'Creating scenario for service %s.', self._service.get_name())
		self._service.create_scenario(scenario_params)
		self._log.info(
			self.__class__.__name__,
			'Scenario for service %s has been successfully created.', self._service.get_name())
