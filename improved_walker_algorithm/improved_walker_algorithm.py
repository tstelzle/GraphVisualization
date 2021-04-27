import math

import networkx as nx

from .graph import Graph
from .node import Node


def next_left(node: Node):
    if node.edges_to:
        return node.edges_to[0]
    else:
        return node.thread


def next_right(node: Node):
    if node.edges_to:
        return node.edges_to[len(node.edges_to) - 1]
    else:
        return node.thread


def execute_shifts(node: Node):
    shift = 0
    change = 0
    for descending_position in range(len(node.edges_to) - 1, -1, -1):
        node_w = node.edges_to[descending_position]
        node_w.prelim = node_w.prelim + shift
        node_w.mod = node_w.mod + shift
        change = change + node_w.change
        shift = shift + node_w.shift + change


def move_subtree(w_minus: Node, w_plus: Node, shift):
    subtrees = w_plus.number - w_minus.number
    w_plus.change = math.ceil(w_plus.change - shift / subtrees)
    w_plus.shift = w_plus.shift + shift
    w_minus.change = math.ceil(w_minus.change + shift // subtrees)
    w_plus.prelim = w_plus.prelim + shift
    w_plus.mod = w_plus.mod + shift


def ancestor(node_i_minus: Node, node: Node, default_ancestor: Node):
    if node_i_minus.ancestor in node.get_siblings():
        return node_i_minus.ancestor
    else:
        return default_ancestor


class ImprovedWalkerAlgorithm:

    def __init__(self):
        self.graph = Graph()
        self.default_ancestor = None

    def run(self, nx_graph: nx.Graph):
        self.__tree_layout(nx_graph)
        self.__first_walk(self.graph.root_node)
        self.__second_walk(self.graph.root_node, - self.graph.root_node.prelim)

        self.__print_info()

    def __tree_layout(self, nx_graph: nx.Graph):
        graph_nodes = []
        for node in nx_graph.nodes:
            new_node = Node(name=node)
            edges_to = {}
            edges_from = {}
            for edge in nx_graph.edges:
                try:
                    edge_from, edge_to, weight = edge
                except ValueError:
                    edge_from, edge_to = edge
                if edge_from is node:
                    edges_to[len(edges_to)] = edge_to
                elif edge_to is node:
                    edges_from[len(edges_from)] = edge_from

            new_node.edges_to = edges_to
            new_node.edges_from = edges_from
            if new_node.edges_to:
                new_node.default_ancestor = new_node.edges_to[0]

            root = False

            if not edges_from:
                new_node.root = root
                self.graph.root_node = new_node

            graph_nodes.append(new_node)

        self.graph.nodes = graph_nodes
        self.graph.edges = nx_graph.edges

        self.graph.replace_node_names_with_node_objects()

    def __first_walk(self, node: Node):
        if not node.edges_to:
            self.prelim = 0
        else:
            self.default_ancestor = node.edges_to[0]
            for position, ancestor_node in node.edges_to.items():
                self.__first_walk(ancestor_node)
                self.__apportion(ancestor_node, self.default_ancestor)
            execute_shifts(node)
            midpoint = math.ceil((node.edges_to[0].prelim + node.edges_to[len(node.edges_to) - 1].prelim) / 2)

            left_sibling = node.get_left_sibling()
            if left_sibling:
                node.prelim = left_sibling.prelim + self.graph.distance
                node.mod = node.mod - midpoint
            else:
                node.prelim = midpoint

    def __second_walk(self, node: Node, m: int):
        node.x = node.prelim + m
        node.y = self.graph.get_level(node)
        for position, child in node.edges_to.items():
            self.__second_walk(child, m + node.mod)

    def __apportion(self, node: Node, default_ancestor: Node):
        left_sibling = node.get_left_sibling()
        if left_sibling:
            node_i_plus = node
            node_o_plus = node
            node_i_minus = left_sibling
            node_o_minus = node_i_plus.get_siblings()[0]
            s_i_plus = node_i_plus.mod
            s_o_plus = node_o_plus.mod
            s_i_minus = node_i_minus.mod
            s_o_minus = node_i_minus.mod

            while next_right(node_i_minus) and next_left(node_i_plus):
                node_i_minus = next_right(node_i_minus)
                node_i_plus = next_left(node_i_plus)
                node_o_minus = next_left(node_o_minus)
                node_o_plus = next_right(node_o_plus)
                node_o_plus.ancestor = node
                shift = (node_i_minus.prelim + s_i_minus) - (node_i_plus.prelim + s_i_plus) + self.graph.distance
                if shift > 0:
                    move_subtree(ancestor(node_i_minus, node, self.default_ancestor), node, shift)
                    s_i_plus = s_i_plus + shift
                    s_o_plus = s_o_plus + shift
                s_i_minus = s_i_minus + node_i_minus.mod
                s_i_plus = s_i_plus + node_i_plus.mod
                s_o_minus = s_o_minus + node_o_minus.mod
                s_o_plus = s_o_plus + node_o_plus.mod
            if next_right(node_i_minus) and not next_right(node_o_plus):
                node_o_plus.thread = next_right(node_i_minus)
                node_o_plus.mod = node_o_plus.mod + s_i_minus - s_o_plus
            if next_left(node_i_plus) and not next_left(node_o_minus):
                node_o_plus.thread = next_left(node_i_plus)
                node_o_plus.mod = node_o_minus.mod + s_i_plus + s_o_minus
                self.default_ancestor = node

    def __print_info(self):
        for node in self.graph.nodes:
            print(node.name, node, node.x, node.y)
