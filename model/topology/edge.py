"""
This class model a basic graph edge. This object may be extended by other classes for specializing its behavior.
"""


class Edge(object):
    def __init__(self, from_node, to_node):
        self._from = from_node
        self._to = to_node

    def __repr__(self):
        return "Link[from=%s, to=%s]" % (self._from, self._to)

    '''
    Get the source node of the edge.
    '''

    def get_from_node(self):
        return self._from

    '''
    Get the destination node of the edge.
    '''

    def get_to_node(self):
        return self._to
