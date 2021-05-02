import networkx as nx
import matplotlib.pyplot as plt

from .node import Node
from module_graph import save_fig


class Graph:
    """
    Class Graph
    """

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.root_node = None
        self.distance = 5

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
            if node_name is node.name:
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
        Therefore this evaluates how many and which node objects are identified as root (have no edges from other nodes).
        :return: (int, [Node])
        """
        root_list = []
        root_counter = 0
        for node in self.nodes:
            if node.root is True:
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
        Draws the current graph from top to bottom. The image is then shown and also saved in the output directory with the specified filename.
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
        plt.gca().invert_xaxis()
        save_fig(filename)
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

        for i in range(1, len(level_dict)+1):
            print(i, level_dict[i])
