from abc import ABCMeta, abstractmethod

from utils.log import Logger

"""
This class models a service that framework is able to test. A service is an object with a name and 
a set of alternatives to evaluate.
"""


class Service(object):
	__metaclass__ = ABCMeta

	def __init__(self, name):
		# The logger
		self._log = Logger.get_instance()
		# The name of the service
		self._name = name
		# the overlay associated to this service
		self._overlay = None
		# The scenario associated to this service
		self._scenario = None
		# The list of alternatives for this scenario
		self._alternatives = []

	def __repr__(self):
		return "Service[name=%s, alternatives=%s]" % (self._name, self._alternatives)

	'''
	Return the name of this service.
	'''

	def get_name(self):
		return self._name

	'''
	Return the overlay associated to this service
	'''

	def get_overlay(self):
		return self._overlay

	'''
	Return the scenario associated to this service
	'''

	def get_scenario(self):
		return self._scenario

	'''
	Return all alternatives defined for this service.
	'''

	def get_alternatives(self):
		return self._alternatives

	'''
	Create an alternative for this service starting from its adapter, its name and its configuration 
	parameters.
	'''

	@abstractmethod
	def create_alternative(self, alternative_name, alternative_adapter, scenario_parameters):
		pass

	'''
	Create the overlay for this service. This overlay will be used to evaluate all alternatives of 
	this service.
	'''

	@abstractmethod
	def create_overlay(self, topology):
		pass

	'''
	Create the scenario for this service. All alternatives will run on the same scenario.
	'''

	@abstractmethod
	def create_scenario(self, scenario_params):
		pass

	'''
	Build the scenario based on the overlay.
	'''

	@abstractmethod
	def build_scenario(self):
		pass
