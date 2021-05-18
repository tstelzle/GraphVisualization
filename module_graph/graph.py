import os
import sys

import networkx as nx
import matplotlib.pyplot as plt

from .node import Node


class Graph:
    """
    Class Graph
    """

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.root_node = None
        self.distance = 5

    @staticmethod
    def create_graph_from_nx(nx_graph: nx.Graph, parent=False):
        graph = Graph()
        graph_nodes = []
        new_edges = []
        not_copied_edges = True
        for node in nx_graph.nodes.items():
            new_node = Node(name=node[0].name)
            new_node.number = node[1]['child_position']
            edges_to = {}
            edges_from = {}
            parent_counter = 0
            for edge in nx_graph.edges:
                try:
                    edge_from, edge_to, weight = edge
                except ValueError:
                    edge_from, edge_to = edge
                if not_copied_edges:
                    new_edges.append((edge_from.name, edge_to.name))
                if edge_from.name is node[0].name:
                    child_pos = [node[1]['child_position'] for node in nx_graph.nodes.items() if node[0] == edge_to][0]
                    edges_to[child_pos] = edge_to.name
                elif edge_to.name is node[0].name:
                    edges_from[parent_counter] = edge_from.name
                    parent_counter += 1
            not_copied_edges = False

            new_node.edges_to = edges_to
            new_node.edges_from = edges_from

            graph_nodes.append(new_node)

        graph.nodes = graph_nodes
        graph.edges = new_edges

        graph.replace_node_names_with_node_objects()

        Graph.check_roots(graph)

        if parent:
            graph.initialize_parent(graph)

        return graph

    @staticmethod
    def create_missing_dir(path):
        """
        Creates missing directories. Skips if the directory already exists.
        :param path: str; Directory path
        :return: None
        """
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.makedirs(path)

    @staticmethod
    def save_fig(fig_name: str):
        """
        Function to save a plt figure with the given figure name.
        :param fig_name: str; Filename for the saved figure
        :return: None
        """
        directories = '/'.join(fig_name.split('/')[:-1])
        Graph.create_missing_dir('output/' + directories)
        plt.savefig('output/' + fig_name + '.png', dpi=500, bbox_inches=None, format=None)

    @staticmethod
    def check_roots(graph):
        root_counter, roots = graph.count_roots()
        if root_counter == 1:
            root = graph.get_node_by_name(roots[0])
            root.root = True
            graph.root_node = root
        else:
            print('Inserting Mega Root')
            mega_root = Node('mega_root')
            root_counter = 0
            for current_root_name in roots:
                current_root = graph.get_node_by_name(current_root_name)
                current_root.edges_from[0] = mega_root.name
                mega_root.edges_to[root_counter] = current_root_name
                root_counter += 1
                graph.edges.append((mega_root.name, current_root_name))
            graph.nodes.append(mega_root)

        return graph

    @staticmethod
    def initialize_parent(graph):
        for node in graph.nodes:
            if len(node.edges_from) == 1:
                node.parent = graph.get_node_by_name(node.edges_from[0])
            if len(node.edges_from) > 1:
                print('The node', node.name, 'has multiple parents.\nStopping!')
                sys.exit(1)

        return graph

    def print_root_node(self):
        """
        Prints the name of the root node of the graph.
        :return: None
        """
        print(self.root_node.name)

    def replace_node_names_with_node_objects(self):
        """
        Iterates over the node list and replaces the name strings with the node objects.
        :return: None
        """
        for node in self.nodes:
            for key, node_to in node.edges_to.items():
                node.edges_to[key] = self.get_node_by_name(node_to)

            node.parent = self.get_node_by_name(node.parent)

    def get_node_by_name(self, node_name):
        """
        Finds the node by name and returns the belonging object.
        :param node_name: str
        :return: ?Node
        """
        for node in self.nodes:
            if node_name == node.name:
                return node

        return None

    def get_level(self, node: Node):
        """
        Returns the level of the node. The level is the length of the pass to the root node.
        :param node: Node
        :return: int
        """
        if node == self.root_node:
            return 1

        return 1 + self.get_level(node.parent)

    def count_roots(self):
        """
        This method is for debugging purposes. Some graphs were misread and had multiple root nodes.
        Therefore this evaluates how many and which node objects are identified as root
        (have no edges from other nodes).
        :return: (int, [Node])
        """
        root_list = []
        root_counter = 0
        for node in self.nodes:
            if len(node.edges_from) == 0:
                root_counter += 1
                root_list.append(node.name)
        return root_counter, root_list

    def print_root_counter(self):
        """
        Prints the amount of root nodes (without edges from other nodes) in the graph.
        :return: None
        """
        print(self.count_roots()[0])

    def print_roots(self):
        """
        Prints a list of nodes, which are identified as root nodes (without edges from other nodes).
        :return: None
        """
        print(self.count_roots()[1])

    def print_node_count(self):
        """
        Prints the amount of nodes in the graph.
        :return: None
        """
        print('Nodes in Graph:', len(self.nodes))

    def get_node_names_with_pos(self):
        """
        Creates a dictionary with the node name as key and the value is a tuple of x,y position.
        :return: dict
        """
        node_dict = {}
        for node in self.nodes:
            node_dict[node.name] = (node.x, node.y)

        return node_dict

    def draw_graph(self, filename: str, scale_x=10, scale_y=10):
        """
        Draws the current graph from top to bottom. The image is then shown and
        also saved in the output directory with the specified filename.
        The scale parameters define the size of the image.
        :param filename: str, Filename for the images
        :param scale_x: int
        :param scale_y: int
        :return: None
        """
        node_dict = self.get_node_names_with_pos()
        nx_graph = nx.DiGraph()
        nx_graph.add_nodes_from(node_dict.keys())

        nx_graph.add_edges_from(self.edges)

        plt.figure(1, figsize=(scale_x, scale_y))
        nx.draw(nx_graph, node_dict, with_labels=True)
        plt.gca().invert_yaxis()
        Graph.save_fig(filename)
        plt.show()

    def print_breadth_first_search(self, node: Node):
        """
        Prints a list for each level with the belonging node names. The tree is traversed with Breadth First Search.
        :param node: node
        :return: None
        """
        queue = [node]
        labeled_queue = [node]
        level_dict = {}
        while queue:
            current_node = queue[0]
            queue.remove(current_node)
            current_level = self.get_level(current_node)
            if current_level in level_dict:
                level_dict[current_level].append(current_node.name)
            else:
                level_dict[current_level] = [current_node.name]
            for pos, child in current_node.edges_to.items():
                if child not in labeled_queue:
                    labeled_queue.append(child)
                    queue.append(child)

        for i in range(1, len(level_dict) + 1):
            print(i, level_dict[i])

    def count_sinks(self):
        node_list = self.nodes
        sinks = []
        for node in node_list:
            if len(node.edges_to) == 0:
                sinks.append(node)

        return len(sinks), sinks

    def remove_node(self, node: Node):
        # node = self.get_node_by_name(node_name)
        self.nodes.remove(node)

        for edge_from, edge_to in self.edges:
            if node.name == edge_from or node.name == edge_to:
                self.edges.remove((edge_from, edge_to))

        for node in self.nodes:
            if node.parent not in self.nodes:
                node.parent = None
            deletion_counter = 0
            for child_number, child_node in node.edges_to.items():
                if child_node not in self.nodes:
                    deletion_counter += 1
                    node.update_position(child_number)
            while deletion_counter != 0:
                del node.edges_to[len(node.edges_to) -1]
                deletion_counter -= 1

    def get_maximal_degree_difference_node(self):
        maximum = None
        maximum_value = None
        for node in self.nodes:
            adjacent_difference = len(node.edges_from) - len(node.edges_to)
            if maximum_value is None or adjacent_difference > maximum_value:
                maximum_value = adjacent_difference
                maximum = node

        return maximum_value, maximum
