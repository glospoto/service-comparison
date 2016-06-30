#! /usr/bin/python
import argparse

import os
import xml.etree.ElementTree as Xml

INTERESTING_KEYS = ['d100', 'd33']


def add_asn_key(topologies):
    for topology in topologies:
        if topology.endswith('.graphml'):
            print "Processing topology", topology

            ns = "{http://graphml.graphdrawing.org/xmlns}"
            Xml.register_namespace('', 'http://graphml.graphdrawing.org/xmlns')
            Xml.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

            xml = Xml.parse(topology)
            root = xml.getroot()
            graph = root.findall(ns + 'graph')
            # Try to keep <key> tag for asn value
            keys_values_set = root.findall(ns + 'key')
            found = False
            for key in keys_values_set:
                attr_name = key.get('attr.name')
                key_id = key.get('id')
                if key_id not in INTERESTING_KEYS:
                    root.remove(key)
                if not found and attr_name == 'asn':
                    found = True

            # If <key attr.name="asn"> was not found, add it. Otherwise, do nothing.
            if not found:
                asn = Xml.Element('key',
                                  attrib={'attr.name': 'asn', 'attr.type': 'string', 'for': 'node', 'id': 'd100'})
                root.append(asn)

                # Graph element
                graph_element = graph[0]
                # Remove all <data> tags whose key's value is not in INTERESTING_KEYS
                data = graph_element.findall(ns + 'data')
                for d in data:
                    key = d.get('key')
                    if key not in INTERESTING_KEYS:
                        graph_element.remove(d)

                # For each node, add the tag for as
                nodes = graph_element.findall(ns + 'node')
                for node in nodes:
                    el = Xml.Element('data', attrib={'key': 'd100'})
                    el.text = '1'
                    # Remove <data> tags whose key's value is not in INTERESTING_KEYS
                    data = node.findall(ns + 'data')
                    for d in data:
                        key = d.get('key')
                        if key not in INTERESTING_KEYS:
                            node.remove(d)
                    node.append(el)

                # For each edge, remove <data> tags
                edges = graph_element.findall(ns + 'edge')
                for edge in edges:
                    data = edge.findall(ns + 'data')
                    for d in data:
                        key = d.get(key)
                        if key not in INTERESTING_KEYS:
                            edge.remove(d)

                xml.write(topology, xml_declaration=True, encoding='utf-8', method='xml')


def remove_asn_key(topologies):
    for topology in topologies:
        if not topology.endswith('.py'):
            pass

if __name__ == '__main__':
    opts = argparse.ArgumentParser(description='Processing GraphML topology files.',
                                   prog='processing.py', usage='%(prog)s -a add/remove')
    opts.add_argument('-a', '--action', required=True, help='Add or remove \'asn\' key into/from topology files.')

    # Take user's opts
    args = opts.parse_args()
    value = str(args.action)

    # Take all files into topologies folder
    cwd = os.getcwd()
    files = os.listdir(cwd)

    if value == 'add':
        add_asn_key(files)
    elif value == 'remove':
        remove_asn_key(files)
    else:
        print "Unknown value; try again using \'add\' or \'remove\' as value for -a option."
