from abc import ABCMeta, abstractmethod

from utils.log import Logger

"""
This class models a basic overlay.
"""


class Overlay(object):

    __metaclass__ = ABCMeta

    def __init__(self, name):
        self._name = name

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_nodes(self):
        pass

    @abstractmethod
    def get_node(self, name):
        pass

    @abstractmethod
    def get_hosts(self):
        pass

    @abstractmethod
    def get_links(self):
        pass

"""
A topology overlay is a graph populated with instances of classes Node and Edge.
"""


class TopologyOverlay(Overlay):

    def __init__(self):
        Overlay.__init__(self, self.__class__.__name__)
        self._vertices = {}
        self._edges = []

        # Get a logger
        self._log = Logger.get_instance()

    def __repr__(self):
        return "Overlay[name=%s, #nodes=%i, #edges=%i]" % (self._name, len(self._nodes), len(self._edges))

    '''
    Return the name of this overlay
    '''
    def get_name(self):
        return self._name

    '''
    Return all nodes in this overlay (in accord with the abstract class Overlay).
    '''
    def get_nodes(self):
        self.get_vertices()

    '''
    Return a node in this overlay (in accord with the abstract class Overlay) starting from its name.
    '''
    def get_node(self, name):
        self.get_vertex(name)

    '''
    Return all hosts in this overlay (in accord with the abstract class Overlay).
    '''
    def get_hosts(self):
        return None

    '''
    Return all links in this overlay (in accord with the abstract class Overlay).
    '''
    def get_links(self):
        self.get_edges()

    '''
    Add a new vertex to this overlay.
    '''
    def add_vertex(self, vertex):
        self._vertices[vertex.get_name()] = vertex
        self._log.debug(self.__class__.__name__, 'Node %s added.', vertex)

    '''
    Return a vertex starting from its name.
    '''
    def get_vertex(self, name):
        return self._vertices.get(name)

    '''
    Return all vertices in this overlay.
    '''
    def get_vertices(self):
        return self._vertices

    '''
    Add a new edge to this overlay.
    '''
    def add_edge(self, edge):
        self._edges.append(edge)
        self._log.debug(self.__class__.__name__, 'Edge %s added.', edge)

    '''
    Return all links in this overlay.
    '''
    def get_edges(self):
        return self._edges
