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
        node_w.prelim += shift
        node_w.mod += shift
        change += node_w.change
        shift += node_w.shift + change


def move_subtree(w_minus: Node, w_plus: Node, shift):
    subtrees = w_plus.number - w_minus.number
    w_plus.change -= shift / subtrees
    w_plus.shift += shift
    w_minus.change += shift / subtrees
    w_plus.prelim += shift
    w_plus.mod += shift


def ancestor(node_i_minus: Node, node: Node, default_ancestor: Node):
    siblings_names = [node.name for node in node.get_siblings().values()]
    if node_i_minus.ancestor.name in siblings_names and node_i_minus is not node:
        return node_i_minus.ancestor
    else:
        return default_ancestor


class ImprovedWalkerAlgorithm:
    """
    Class Improved Walker Algorithm
    """

    def __init__(self):
        self.graph = Graph()
        self.default_ancestor = None

    def run(self, nx_graph: nx.Graph, filename: str, scale_x=10, scale_y=10):
        """
        Starts the Improved Walker Algorithm
        :param nx_graph: Networkx Graph, for which the algorithm should be run
        :param filename: str, Filename for the to be saved image
        :param scale_x: int, x scale for the image
        :param scale_y: int, y scale for the image
        :return:
        """
        self.__tree_layout(nx_graph)
        self.__first_walk(self.graph.root_node)
        self.__second_walk(self.graph.root_node, self.graph.root_node.prelim)
        self.graph.draw_graph(filename, scale_x=scale_x, scale_y=scale_y)

        self.__print_nodes_coordinates()

    def __tree_layout(self, nx_graph: nx.Graph):
        graph_nodes = []
        new_edges = []
        for node in nx_graph.nodes.items():
            new_node = Node(name=node[0].name)
            new_node.number = node[1]['child_position']
            edges_to = {}
            parent = None
            for edge in nx_graph.edges:
                try:
                    edge_from, edge_to, weight = edge
                except ValueError:
                    edge_from, edge_to = edge
                new_edges.append((edge_from.name, edge_to.name))
                if edge_from.name is node[0].name:
                    child_pos = [node[1]['child_position'] for node in nx_graph.nodes.items() if node[0] == edge_to][0]
                    edges_to[child_pos] = edge_to.name
                elif edge_to.name is node[0].name:
                    parent = edge_from.name

            new_node.edges_to = edges_to
            new_node.parent = parent

            if not parent:
                new_node.root = True
                self.graph.root_node = new_node

            graph_nodes.append(new_node)

        self.graph.nodes = graph_nodes
        self.graph.edges = new_edges

        self.graph.replace_node_names_with_node_objects()

    def __first_walk(self, node_v: Node):
        if not node_v.edges_to:
            left_sibling = node_v.get_left_sibling()
            if left_sibling:
                node_v.prelim = left_sibling.prelim + self.graph.distance
            else:
                self.prelim = 0
        else:
            default_ancestor = node_v.edges_to[0]
            for i in range(len(node_v.edges_to)):
                node_w = node_v.edges_to[i]
                self.__first_walk(node_w)
                default_ancestor = self.__apportion(node_w, default_ancestor)
            execute_shifts(node_v)
            midpoint = (node_v.edges_to[0].prelim + node_v.edges_to[len(node_v.edges_to) - 1].prelim) / 2

            left_sibling = node_v.get_left_sibling()
            if left_sibling:
                node_v.prelim = left_sibling.prelim + self.graph.distance
                node_v.mod = node_v.prelim - midpoint
            else:
                node_v.prelim = midpoint

    def __second_walk(self, node: Node, m: int):
        node.x = node.prelim + m
        node.y = self.graph.get_level(node)
        for position, child in node.edges_to.items():
            self.__second_walk(child, m + node.mod)

    def __apportion(self, node_v: Node, default_ancestor: Node):
        left_sibling = node_v.get_left_sibling()
        if left_sibling:
            node_i_plus = node_v
            node_o_plus = node_v
            node_i_minus = left_sibling
            node_o_minus = node_i_plus.get_left_most_sibling()
            s_i_plus = node_i_plus.mod
            s_o_plus = node_o_plus.mod
            s_i_minus = node_i_minus.mod
            s_o_minus = node_o_minus.mod

            while next_right(node_i_minus) and next_left(node_i_plus):
                node_i_minus = next_right(node_i_minus)
                node_i_plus = next_left(node_i_plus)
                node_o_minus = next_left(node_o_minus)
                node_o_plus = next_right(node_o_plus)
                node_o_plus.ancestor = node_v
                shift = (node_i_minus.prelim + s_i_minus) - (node_i_plus.prelim + s_i_plus) + self.graph.distance
                if shift > 0:
                    ancestor_node = ancestor(node_i_minus, node_v, default_ancestor)
                    move_subtree(ancestor_node, node_v, shift)
                    s_i_plus += shift
                    s_o_plus += shift
                s_i_minus += node_i_minus.mod
                s_i_plus += node_i_plus.mod
                s_o_minus += node_o_minus.mod
                s_o_plus += node_o_plus.mod
            if next_right(node_i_minus) and not next_right(node_o_plus):
                node_o_plus.thread = next_right(node_i_minus)
                node_o_plus.mod += s_i_minus - s_o_plus
            if next_left(node_i_plus) and not next_left(node_o_minus):
                node_o_minus.thread = next_left(node_i_plus)
                node_o_minus.mod += s_i_plus + s_o_minus
                default_ancestor = node_v

        return default_ancestor

    def __print_infos(self):
        """
        This method is for debugging.
        Prints the current nodes by depth in graph.
        Prints all nodes with coordinates.
        Prints the amount of root nodes (without edges from other nodes).
        Prints the amount of nodes in the graph
        :return: None
        """
        self.graph.print_breadth_first_search(self.graph.root_node)
        self.__print_nodes_coordinates()
        self.graph.print_root_counter()
        self.graph.print_node_count()

    def __print_nodes_coordinates(self):
        """
        Prints all nodes with their coordinates.
        :return: None
        """
        for node in self.graph.nodes:
            print(node.name, node.x, node.y)
