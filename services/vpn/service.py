import utils.class_for_name as Class

from model.service import Service
from services.vpn.overlay import VpnOverlay
from services.vpn.scenario import VpnScenario
from services.vpn.vpn import Switch, Link
from utils.generator import AddressGenerator

"""
This class specializes class Service for VPN service. It has in charge the task of creating the alternatives under test
for this service.
"""


class VpnService(Service):
    def __init__(self, name):
        Service.__init__(self, name)

    '''
    Set the scenario for this service
    '''

    '''
    Creating an alternative object starting from its adapter
    '''

    def create_alternative(self, alternative_name, alternative_adapter, scenario_parameters):
        self._log.debug(self.__class__.__name__, 'Creating alternative %s.', alternative_name)
        # The pattern of params for the for_name method is: adapter, name of the alternative and all parameters defined
        # in the configuration file
        alternative = Class.for_name(alternative_adapter, name=alternative_name, scenario=scenario_parameters)
        # Add the alternative to the list of alternatives
        self._alternatives.append(alternative)
        self._log.debug(self.__class__.__name__, 'Adding alternative %s to the list of alternatives of service %s.',
                        alternative_name, self._name)
        self._log.info(self.__class__.__name__, 'Alternative %s has been successfully created.', alternative_name)
        return alternative

    '''
    Create the network overlay for this service
    '''

    def create_overlay(self, topology):
        # The VpnOverlay instance
        self._overlay = VpnOverlay()
        # IP generator instance, used to assign subnet to the link
        ip_generator = AddressGenerator.get_instance()
        self._log.debug(self.__class__.__name__, 'Starting to create the overlay for the service %s', self._name)

        # For each node in the topology, create a Switch object in the VpnOverlay
        nodes = topology.nodes()
        for node in nodes:
            # Here, create a node for VPN overlay
            dpid = int(node) + 1  # Avoid dpid=0
            name = topology.node[node]['label']
            role = topology.node[node]['vrf_role']
            switch = Switch(dpid, name, role)
            self._overlay.add_node(switch)
            self._log.debug(self.__class__.__name__,
                            'Switch %s has been successfully created and added to %s', switch, self._overlay.get_name())

        # For each link in the topology, create a Link object in the VpnOverlay
        edges = topology.edges()
        for edge in edges:
            '''
            When getting switches from the overlay, remember to convert the id in the edge tuple into an int value;
            moreover, plus 1 to it, avoiding dpid with value zero.
            '''
            from_switch = self._overlay.get_node(int(edge[0]) + 1)
            from_switch_interface = from_switch.create_interface()
            to_switch = self._overlay.get_node(int(edge[1]) + 1)
            to_switch_interface = to_switch.create_interface()
            # Take a subnet for the link
            subnet = ip_generator.get_next_subnet()
            link = Link(from_switch, to_switch, from_switch_interface, to_switch_interface, subnet)
            self._overlay.add_link(link)
            self._log.debug(self.__class__.__name__,
                            'Link %s has been successfully created and added to %s', link, self._overlay.get_name())

        self._log.info(self.__class__.__name__, 'Overlay %s has been successfully created', self._overlay.get_name())

    '''
    Create the scenario for this service. All alternatives will run on the same scenario
    '''

    def create_scenario(self, scenario_params):
        self._log.debug(self.__class__.__name__, 'Starting to create the scenario for service %s.', self._name)
        self._scenario = VpnScenario(scenario_params)
        self._log.info(self.__class__.__name__, 'Scenario for service %s has been successfully created.', self._name)

    '''
    Build scenario based on the overlay.
    '''

    def build_scenario(self):
        self._log.debug(self.__class__.__name__, 'Starting to build the scenario for service %s.', self._name)
        self._scenario.create(self._overlay)
        self._log.debug(self.__class__.__name__, 'Scenario for service %s has been successfully built.', self._name)
