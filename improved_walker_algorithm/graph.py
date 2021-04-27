
from .node import Node

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

            for key, node_from in node.edges_from.items():
                node.edges_from[key] = self.get_node_by_name(node_from)

    def get_node_by_name(self, node_name):
        for node in self.nodes:
            if node_name is node.name:
                return node

        return None

    def get_level(self, node: Node):
        if node == self.root_node:
            return 0
        level = 1
        parent = node.edges_from[0]
        while self.root_node is not parent:
            level += 1
            parent = parent.edges_from[0]

        return level
