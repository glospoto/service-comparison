"""
This class model a basic graph node. This object may be extended by other classes for specializing 
its behavior.
"""


class Node(object):
	def __init__(self, name):
		self._name = name

	def __repr__(self):
		return "SimpleNode[name=%s]" % self._name

	'''
	Return the name of the node.
	'''

	def get_name(self):
		return self._name
