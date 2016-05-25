import os
import shutil

from loader.env.controller import ControllerStarter
from model.alternative import Alternative

from services.vpn.configurator import Rm3SdnVpnConfigurator, MplsBgpVpnConfigurator
from services.vpn.overlay import VpnOverlay
from services.vpn.vpn import Switch, Link

"""
This class implements the rm3-sdn-vpn's alternative.
"""


class Rm3SdnVpnAlternative(Alternative):
    def __init__(self, name, **kwargs):
        Alternative.__init__(self, name)
        # This is an instance of services.vpn.configurator.Rm3SdnVpnConfigurator
        self._configurator = Rm3SdnVpnConfigurator()
        # Parameters
        params = kwargs.get('scenario')
        # To start the controller
        self._controller = None
        # Controller path
        self._controller_path = params['controller_path']
        # Controller executable file
        self._controller_cmd = params['controller_cmd']

    def __repr__(self):
        return 'Alternative[name=%s, metrics=%s]' % (self._name, self._metrics)

    '''
    Create the scenario associated to this alternative.
    '''

    def deploy(self, overlay, scenario):
        # Generate the configuration file
        self._configurator.configure(overlay, scenario)
        # TODO: move this instructions into FileSystem class
        shutil.copy('tmp/' + self._configurator.get_system_config_file(), os.path.expanduser(self._controller_path) + 'conf/')
        shutil.copy('tmp/' + self._configurator.get_vpns_config_file(), os.path.expanduser(self._controller_path) + 'conf/vpns/')
        # Start the controller
        self._controller = ControllerStarter(self._controller_path, self._controller_cmd)
        self._controller.start()

    '''
    Destroy the scenario associated to this alternative.
    '''

    def destroy(self):
        # Stop the controller
        self._controller.stop()

    '''
    Return the configurator associated to this alternative.
    '''

    def get_configurator(self):
        return self._configurator


"""
This class implements the mpls-bgp-vpn's alternative.
"""


class MplsBgpVpnAlternative(Alternative):
    def __init__(self, name, *args, **kwargs):
        Alternative.__init__(self, name)
        # This is an instance of services.vpn.overlay.VpnOverlay
        self._overlay = VpnOverlay()
        # This is an instance of services.vpn.scenario.MplsBgpVpnScenario
        self._scenario = MplsBgpVpnScenario(*args, **kwargs)  # TODO
        # This is an instance of services.vpn.configurator.MplsBgpVpnConfigurator
        self._configurator = MplsBgpVpnConfigurator()  # TODO
        # This is a string reference to the class that models the environment. This is NOT a reference to the object!
        self._environment = None
        # Metrics to consider for this alternative. This is a list of model.metric.Metric objects
        self._metrics = []

    def __repr__(self):
        return 'Alternative[name=%s, scenario=%s, metrics=%s]' % (self._name, self._scenario.get_name(), self._metrics)

    '''
    Create the overlay for this alternative.
    '''

    def create_overlay(self, topology):
        """
        Remember that is important to keep coherence between host-pe interface associations in the generation of network
        and the interface written into the VPNs' configuration file. For this reason, the steps will be:
         1. add switch to the overlay
         2. generate the VPNs
         3. add host to the overlay
         4. add all links to the overlay, starting from the links between hosts and PEs
        """

        # Step 1: add nodes to the overlay
        nodes = topology.nodes()
        for node in nodes:
            # Here, create a node for VPN overlay
            dpid = int(node) + 1
            name = topology.node[node]['label']
            role = topology.node[node]['vrf_role']
            switch = Switch(dpid, name, role)
            self._overlay.add_node(switch)
            self._log.debug(self.__class__.__name__,
                            'Switch %s created and added to %s', switch, self._overlay.get_name())

        # Step 2 and 3: generate VPNs and add hosts to the overlay (actually, links between hosts and PEs are added
        # inside this method: generalize this procedure!!! Fixme.
        # In this alternative, I do not have to configure anything
        # self._configurator.create_vpns(self._overlay, self._scenario.get_number_of_vpns())

        # Step 4: add links to the overlay; these links are only refereed to switches interconnections.
        edges = topology.edges()
        for edge in edges:
            '''
            When getting switches from the overlay, remember to convert the id in the edge tuple into an int value;
            moreover, plus 1 to it, avoiding dpid with value zero.
            '''
            from_switch = self._overlay.get_node(int(edge[0]) + 1)
            to_switch = self._overlay.get_node(int(edge[1]) + 1)
            link = Link(from_switch, to_switch)
            self._overlay.add_link(link)
            self._log.debug(self.__class__.__name__,
                            'Link %s created and added to %s', link, self._overlay.get_name())

        return self._overlay

    '''
    Create the scenario associated to this alternative.
    '''

    def setting_up_scenario(self):
        # Generate the configuration file
        self._configurator.write_configurations(self._overlay)
        # Start the scenario
        self._scenario.start()

    '''
    Return the scenario associated with this alternative.
    '''

    def get_scenario(self):
        return self._scenario

    '''
    Destroy the scenario associated to this alternative.
    '''

    def destroy(self):
        self._scenario.destroy()

    '''
    Return the configurator associated to this alternative.
    '''

    def get_configurator(self):
        return self._configurator
