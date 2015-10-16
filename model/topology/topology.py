import os
import networkx as nx

from model.topology.node import Node
from model.topology.edge import Edge
from model.topology.overlay import TopologyOverlay
from utils.log import Logger

"""
This class class models a topology. A topology object is a list of different overlay, each of which represents a graph
where each node is a specialization of class Node and each edge is a specialization of the class Edge. It allows user to
create topologies with objects that have their behavior related to the service.
"""


class Topology(object):

    def __init__(self, topology):
        self._name = None
        self._overlays = {}
        self._current_overlay = None
        self._topology_as_graphml = topology

        # Get a logger
        self._log = Logger.get_instance()

        # When create a Topology object, add it a Topology Overlay by default.
        self._add_topology_overlay()

    def __repr__(self):
        return "Topology[name=%s, #overlays=%s]" % (self._name, self._overlays)

    '''
    Return the topology read by a GraphML file.
    '''
    def get_topology_from_graphml(self):
        return nx.read_graphml(self._topology_as_graphml)

    '''
    Return all overlays associated to this topology
    '''
    def get_overlays(self):
        return self._overlays

    '''
    Return the current overlay of this topology.
    '''
    def get_current_overlay(self):
        return self._current_overlay

    '''
    Return an overlay starting from its name.
    '''
    def get_overlay(self, name):
        return self._overlays.get(name)

    '''
    Private method for reading a topology starting from a GraphML file.
    '''
    def _read_topology(self):
        return nx.read_graphml(self._topology_as_graphml)

    '''
    Add the first overlay to the topology.
    '''
    def _add_topology_overlay(self):
        self._log.info(self.__class__.__name__, 'Starting to add Topology Overlay to the topology.')
        file_name = os.path.basename(self._topology_as_graphml)
        self._name = file_name.split('.')[0]
        # When a topology is initialized, it adds a PhysicalOverlay to itself
        # Load graphml file
        graph_topology = self._read_topology()
        # Create the overlay
        overlay = TopologyOverlay()
        self._log.debug(self.__class__.__name__, 'Created %s.' % overlay.get_name())
        # For each node in the graph, create a switch
        for node in graph_topology.nodes():
            # Take the id
            name = graph_topology.node[node]['label'].replace(' ', '_')
            node = Node(name)
            # Add switch to the overlay
            overlay.add_vertex(node)
        self._log.debug(self.__class__.__name__, 'Nodes added to %s.', overlay.get_name())
        # Add edge to the topology
        for edge in graph_topology.edges():
            from_node = overlay.get_node((edge[0]))
            to_node = overlay.get_node((edge[1]))
            # Create the edge
            edge = Edge(from_node, to_node)
            # Add the link to the list
            overlay.add_edge(edge)
        self._log.debug(self.__class__.__name__, 'Edges added to %s.', overlay.get_name())
        self._overlays[overlay.get_name()] = overlay
        self._log.info(self.__class__.__name__, '%s correctly added.', overlay.get_name())

    '''
    Add an overlay to the topology.
    '''
    def add_overlay(self, overlay):
        self._overlays[overlay.get_name()] = overlay
        self._current_overlay = overlay
