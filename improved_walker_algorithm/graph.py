import networkx as nx
import matplotlib.pyplot as plt

from .node import Node
from module_graph import save_fig


class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.root_node = None
        self.distance = 5

    def print_root_node(self):
        print(self.root_node.name)

    def replace_node_names_with_node_objects(self):
        for node in self.nodes:
            for key, node_to in node.edges_to.items():
                node.edges_to[key] = self.get_node_by_name(node_to)

            node.parent = self.get_node_by_name(node.parent)

    def get_node_by_name(self, node_name):
        for node in self.nodes:
            if node_name is node.name:
                return node

        return None

    def get_level(self, node: Node):
        if node == self.root_node:
            return 1

        return 1 + self.get_level(node.parent)

    def count_roots(self):
        root_list = []
        root_counter = 0
        for node in self.nodes:
            if node.root is True:
                root_counter += 1
                root_list.append(node.name)
        return root_counter, root_list

    def print_root_counter(self):
        print(self.count_roots()[0])

    def print_roots(self):
        print(self.count_roots()[1])

    def print_node_count(self):
        print('Nodes in Graph:', len(self.nodes))

    def get_node_names_with_pos(self):
        node_dict = {}
        for node in self.nodes:
            node_dict[node.name] = (node.x, node.y)

        return node_dict

    def create_node_position_dict(self):
        node_dict = {}
        for node in self.nodes:
            node_dict[node.name] = (node.x, node.y)

        return node_dict

    def draw_graph(self, filename: str):
        node_dict = self.create_node_position_dict()
        nx_graph = nx.DiGraph()
        nx_graph.add_nodes_from(node_dict.keys())

        nx_graph.add_edges_from(self.edges)

        nx.draw(nx_graph, node_dict, with_labels=True)
        save_fig(filename)
        plt.show()

    def print_breadth_first_search(self, node: Node):
        queue = []
        queue.append(node)
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

