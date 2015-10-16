#! /usr/bin/python

__author__ = 'gabriele'

import os
import networkx as nx

"""
This script cleans the graphml files (removing unused attribute) and then it assigns to each router in the topology a
specific VPN role (P, PE and CE) in order to make the topology files compatible with both autonetkit and framework for
configuration file (Netkit/Mininet) generation.

Algorithm for assigning roles to routers.
 1. Search all node with degree 1; those node are PE
 2. Each neighbor of a PE node is a P node
 3. Remove P nodes
 4. Check if nodes with degree 1 exist:
   a. if not so, mark as P the node(s) with maximum degree (and remove it/them)
   b. check if there are node with degree 1:
      *. if so, go to 1
      *. else, go to a
 """

"""
This class implements the graphml files' loader.
"""


class Loader(object):
    def __init__(self):
        # Load all topologies in this directory
        self._topologies = []

    def load_topologies(self):
        pwd = os.getcwd()
        files = os.listdir(pwd)
        for topology in files:
            if topology.endswith('.graphml'):
                self._topologies.append(topology)
        return self._topologies

"""
This class models the network graph
"""


class Graph(object):
    pass

"""
This class models a node in the network
"""


class Node(object):
    pass

"""
This class implements the algorithm for role assignment
"""


class AllocationRoleAlgorithm(object):
    def __init__(self, graph):
        self._graph = graph

    def get_graph_with_roles(self):
        return self._graph

    # Return the node with max degree in the app graph
    @staticmethod
    def _get_max_degree_node(graph):
        # The node with max degree
        node = None
        # The temporary node with max degree
        tmp_node = None
        nodes = graph.nodes()
        for n in nodes:
            if tmp_node is None:
                tmp_node = n
                node = n
            else:
                if nx.degree(graph, n) > nx.degree(graph, tmp_node):
                    tmp_node = n
                    node = n
        #print 'Node with max degree: %s' % node
        return node

    # Return a node with degree 1
    @staticmethod
    def _get_nodes_with_degree_one(graph):
        node = []
        nodes = graph.nodes()
        for n in nodes:
            if nx.degree(graph, n) == 1:
                node.append(n)
        return node

    # Return True if a PE node already has a P neighbor
    def _has_p_neighbors(self, pe_node):
        has_p_neighbor = False
        neighbors = self._graph.neighbors(pe_node)
        for neighbor in neighbors:
            if self._graph.node[neighbor]['vrf_role'] == 'P':
                has_p_neighbor = True
        return has_p_neighbor

    def allocate_role(self):
        # Make a copy of the graph
        graph = nx.create_empty_copy(self._graph, with_nodes=True)
        graph.add_edges_from(self._graph.edges())

        while len(graph.nodes()) > 0:
            # Try to get a node with degree 1
            nodes = self._get_nodes_with_degree_one(graph)
            if len(nodes) > 0:
                for node in nodes:
                    #if not self._has_p_neighbors(node):
                    # Mark as PE
                    self._graph.node[node]['vrf_role'] = 'PE'
                    # Mark neighbor as P
                    neighbors = graph.neighbors(node)
                    for neighbor in neighbors:
                        self._graph.node[neighbor]['vrf_role'] = 'P'
                graph.remove_node(node)
                graph.remove_nodes_from(neighbors)
                    #else:
                        # Mark as P and remove
                    #    self._graph.node[node]['vrf_role'] = 'P'
                    #    print ' - Mark %s as P' % node
                    #    graph.remove_node(node)
            else:
                node_with_max_degree = self._get_max_degree_node(graph)
                if node_with_max_degree is not None:
                    self._graph.node[node_with_max_degree]['vrf_role'] = 'P'
                    graph.remove_node(node_with_max_degree)

"""
This class implements the cleaner for graphml files that represent the topologies
"""


class Cleaner(object):
    def __init__(self):
        self._graph = nx.Graph()

    def get_cleaned_graph(self):
        return self._graph

    # topology is an instance of nx.Graph class
    def clean(self, graph):
        self._graph.clear()
        # Add nodes from the original graph
        nodes = graph.nodes()
        self._graph.add_nodes_from(nodes)
        # From original nodes, only take the label value
        for node in nodes:
            label = graph.node[node]['label']
            self._graph.node[node]['label'] = label
            # Add the device_type attribute
            self._graph.node[node]['asn'] = '1'
            self._graph.node[node]['device_type'] = 'router'
            self._graph.node[node]['ibgp_role'] = 'Peer'
        # Add edges from the original graph
        edges = graph.edges()
        self._graph.add_edges_from(edges)


"""
This class represents this "small system" and it has in charge the task of cleaning the graphml file and running the
algorithm over the topology.
"""


class Mining(object):
    def __init__(self):
        # For loading all graphml files
        self._loader = Loader()
        # For cleaning graphml files from unused {graph,node,edge} attribute
        self._cleaner = Cleaner()

    def run(self):

        topologies = self._loader.load_topologies()
        for t in topologies:
            print 'Mining of topology %s' % t
            graph = nx.read_graphml(t)
            self._cleaner.clean(graph)
            cleaned_graph = self._cleaner.get_cleaned_graph()
            # Run allocation algorithm over the cleaned graph
            allocator = AllocationRoleAlgorithm(cleaned_graph)
            allocator.allocate_role()
            nx.write_graphml(allocator.get_graph_with_roles(), path=t, encoding='utf-8', prettyprint=True)
        """
        print '*** Topology: Aarnet'
        graph = nx.read_graphml('Aarnet.graphml')
        self._cleaner.clean(graph)
        cleaned_graph = self._cleaner.get_cleaned_graph()
        # Run allocation algorithm over the cleaned graph
        allocator = AllocationRoleAlgorithm(cleaned_graph)
        allocator.allocate_role()
        nx.write_graphml(allocator.get_graph_with_roles(), path='Aarnet.graphml', encoding='utf-8', prettyprint=True)

        print '*** Topology: Abvt'
        graph = nx.read_graphml('Abvt.graphml')
        self._cleaner.clean(graph)
        cleaned_graph = self._cleaner.get_cleaned_graph()
        # Run allocation algorithm over the cleaned graph
        allocator = AllocationRoleAlgorithm(cleaned_graph)
        allocator.allocate_role()
        nx.write_graphml(allocator.get_graph_with_roles(), path='Abvt.graphml', encoding='utf-8', prettyprint=True)
        """

if __name__ == '__main__':
    system = Mining()
    system.run()