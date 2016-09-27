from model.scenario import Scenario
from services.vpn.vpn import VirtualPrivateNetwork, Host, Link, Site
from utils.generator import AddressGenerator

"""
This class implements the scenario for the VPN service. In this case, scenario simply consists of 
the number of VPNs in the network
"""


class VpnScenario(Scenario):
	def __init__(self, scenario_params):
		Scenario.__init__(self)
		self._name = self.__class__.__name__
		# The number of the VPNs in the network
		self._number_of_vpns = int(scenario_params['number_of_vpns'])
		# All VPNs in the network
		self._vpns = {}

	def __repr__(self):
		return 'Scenario[name=%s, #VPNs=%s]' % (self._name, self._number_of_vpns)

	'''
	Return the name of the scenario
	'''

	def get_name(self):
		return self._name

	'''
	Return all VPNs in the scenario
	'''

	def get_vpns(self):
		return self._vpns

	'''
	Create the scenario
	'''

	def create(self, overlay):
		# Create the VPNs
		for i in range(0, self._number_of_vpns):
			name = 'vpn-' + str(i+1)
			vpn = VirtualPrivateNetwork(name)
			self._log.debug(self.__class__.__name__, 'VPN %s has been created', name)
			# Take two random PEs
			pes = overlay.get_two_random_pes()
			# Create sites
			self._log.debug(
				self.__class__.__name__, 
				'Starting to creates the sites for VPN %s.', vpn.get_name())
			vpn.add_site(self._create_site(vpn, pes[0], overlay, i))
			vpn.add_site(self._create_site(vpn, pes[1], overlay, i))
			self._log.debug(self.__class__.__name__, 'Sites have been successfully created.')

			# Add VPN to the map of VPNs
			self._vpns[name] = vpn
		self._log.info(self.__class__.__name__, 'All VPNs have been successfully created.')

	'''
	Create a site for a VPN
	'''

	def _create_site(self, vpn, pe, overlay, i):
		# IP generator
		ip_generator = AddressGenerator.get_instance()
		# First of all, create an host for this site
		# IP addresses for the hosts
		self._log.debug(
			self.__class__.__name__, 'Starting to create a new site for VPN %s.', vpn.get_name())
		self._log.debug(self.__class__.__name__, 'Generating IP address for the host.')
		h_ip = ip_generator.generate_ip_address()
		host = Host('h' + str(i) + '_' + pe.get_name(), h_ip)
		self._log.debug(
			self.__class__.__name__, 'Host %s has been successfully generated.', host.get_name())
		# Add host to the overlay
		overlay.add_host(host)
		self._log.debug(
			self.__class__.__name__, 'Host %s has been added to the overlay.', host.get_name())
		host.set_pe(pe)
		self._log.debug(
			self.__class__.__name__, 'Host %s has been connected to its PE.', host.get_name())
		# Add this host to the VPN
		vpn.add_host(host)
		self._log.debug(self.__class__.__name__, 'Host %s has been added to the VPN %s.',
						host.get_name(), vpn.get_name())
		# Create a new interface for this switch
		pe_interface_name = pe.create_interface()
		self._log.debug(
			self.__class__.__name__, 
			'A new interface for %s has been successfully created.', pe.get_name())
		# Being a PE node, also set the loopback address
		pe.set_loopback(ip_generator.get_next_loopback())
		self._log.debug(
			self.__class__.__name__,
			'A loopback address has been successfully associated to switch %s.', pe.get_name())
		# Finally, create a Link object between host and PE and add it to the overlay
		link = Link(
			host, pe, host.get_interface_name(), pe_interface_name, ip_generator.get_next_subnet())
		self._log.debug(self.__class__.__name__, 'Link %s has been created.', link)
		overlay.add_link(link)
		self._log.debug(self.__class__.__name__,
						'Link %s created and added to %s', link, overlay.get_name())
		site = Site(vpn, pe, pe_interface_name, ip_generator.get_subnet_from_ip(host.get_ip()))
		self._log.info(self.__class__.__name__, 'Site %s has been successfully created.', site)

		return site

	'''
	Destroy the scenario
	'''

	def destroy(self):
		pass
