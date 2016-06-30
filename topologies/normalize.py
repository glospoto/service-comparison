#! /usr/bin/env python

import os

import networkx as nx

def load_topologies(path):
	topo_dir = os.path.join(os.getcwd(), path)
	topos = os.listdir(topo_dir)
	return topos

def normalize(topos):
	for topo in topos:
		new_graph = nx.Graph()
		# The list of actual nodes to put into the graph at the end of the 
		# normalization process
		actual_nodes = []
		counter = 1
		print 'Parsing topology', topo
		graph = nx.read_graphml(os.path.join('old', topo))
		nodes = graph.nodes()
		new_graph.add_nodes_from(nodes)
		edges = graph.edges()
		'''
		Check for:
		 1. duplicate routers' names;
		 2. "None" names
		 3. "_" in names
		'''
		for node in nodes:
			label = graph.node[node]['label']

			if label is not None:
				# Replace special characters
				label = label.replace('-', '')
				label = label.replace('_', '')
				label = label.replace(' ', '')
				label = label[:7]
				if _node_present(actual_nodes, label):
					label = 'Custom' + str(counter)
					counter += 1
			else:
				# The name of the node is "None": give another name
				label = 'Custom' + str(counter)
				counter += 1
			new_graph.node[node]['label'] = label
			actual_nodes.append(label)
			# Add all other attributes
			new_graph.node[node]['asn'] = graph.node[node]['asn']
			new_graph.node[node]['device_type'] = graph.node[node]['device_type']
			new_graph.node[node]['ibgp_role'] = graph.node[node]['ibgp_role']
			new_graph.node[node]['vrf_role'] = graph.node[node]['vrf_role']

		# Add nodes and edges to new_graph
		new_graph.add_edges_from(edges)
		nx.write_graphml(new_graph, path=topo, encoding='utf-8', prettyprint=True)

def _node_present(nodes, node):
	present = False
	for n in nodes:
		if n == node:
			present = True
	return present

def check_duplicates(topos):
	for topo in topos:
		if topo.endswith('.graphml'):
			actual_nodes = []
			print 'Parsing topology', topo
			graph = nx.read_graphml(topo)
			nodes = graph.nodes()
			for node in nodes:
				actual_nodes.append(graph.node[node]['label'])
			if len(actual_nodes) > 0:
				label = actual_nodes.pop()
				if not _node_present(actual_nodes, label):
					print 'No duplicates in', topo
				if '_' in label or '-' in label or ' ' in label:
					print 'Found unwanted characters in routers\' names inside', topo

if __name__ == '__main__':
	topos = load_topologies('')
	#normalize(topos)
	check_duplicates(topos)
