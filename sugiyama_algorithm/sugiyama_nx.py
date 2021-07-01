import copy
import os

import matplotlib.pyplot as plt
import networkx as nx

import module_graph as my_graph
from module_color import *


class SugiyamaNX:

    def __init__(self, filename: str, graph: nx.DiGraph):
        self.filename = filename
        self.graph = graph

    def run_sugiyama(self):
        self.remove_loops()
        node_order = self.greedy_cycle_removal()
        self.revert_edges(node_order)
        self.longest_path()
        self.add_dummy_vertices()
        self.assign_prelim_x()
        self.draw_graph()

    def add_dummy_vertices(self):
        edges_to_add = []
        edges_to_remove = []

        # TODO there was an error with 'dictionary changed size during iteration'
        #  -> could not find it
        #  -> this is the solution
        edges = copy.deepcopy(self.graph.edges)

        for edge in edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge

            y_attributes = nx.get_node_attributes(self.graph, 'y')
            child_position_attributes = nx.get_node_attributes(self.graph, 'child_position')
            difference = y_attributes[edge_to] - y_attributes[edge_from]
            if difference != 1:
                self.graph.remove_edge(edge_from, edge_to)
                edges_to_remove.append((edge_from, edge_to))
                node_counter = 1
                current_node = edge_from
                while difference > 1:
                    new_node_name = "dummy" + str(node_counter) + "_" + edge_from
                    if node_counter == 1:
                        child_position = child_position_attributes[edge_to]
                    else:
                        child_position = 0
                    self.graph.add_node(new_node_name,
                                        y=y_attributes[edge_from] + node_counter,
                                        name=new_node_name,
                                        child_position=child_position)
                    edges_to_add.append((current_node, new_node_name))
                    self.graph.add_edge(current_node, new_node_name, weight=1)
                    current_node = new_node_name
                    difference -= 1
                    node_counter += 1
                    y_attributes = nx.get_node_attributes(self.graph, 'y')
                    child_position_attributes = nx.get_node_attributes(self.graph, 'child_position')

    # def global_sifting(self, sifting_rounds: int):
    #     block_list = []
    #     for p in range(sifting_rounds):
    #         for a in block_list:
    #             block_list = self.sifting_step(block_list, a)
    #
    #     for node in self.graph.nodes:
    #         self.graph.add_node(node, pi=)

    def remove_loops(self):
        edges_to_remove = []

        for edge in self.graph.edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            if edge_from == edge_to:
                edges_to_remove.append(edge_from)

        for edge in edges_to_remove:
            self.graph.remove_edge(edge, edge)

    def revert_edges(self, node_order: [str]):
        reverting_edges = []
        weight = 1

        for edge in self.graph.edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            if node_order.index(edge_from) < node_order.index(edge_to):
                reverting_edges.append(edge)

        for edge in reverting_edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            self.graph.remove_edge(edge_from, edge_to)
            self.graph.add_edge(edge_to, edge_from, weight=weight)

    def greedy_cycle_removal(self):
        copy_graph = copy.deepcopy(self.graph)
        s_1 = []
        s_2 = []
        while len(copy_graph.nodes) != 0:
            sink_counter, sinks = self.get_sinks(copy_graph)
            while sink_counter != 0:
                sink = sinks.pop(0)
                sink_counter -= 1
                s_2.insert(0, sink)
                copy_graph.remove_node(sink)
                sink_counter, sinks = self.get_sinks(copy_graph)

            root_counter, roots = self.get_roots(copy_graph)
            while root_counter != 0:
                root = roots.pop(0)
                root_counter -= 1
                s_1.append(root)
                copy_graph.remove_node(root)
                root_counter, roots = self.get_roots(copy_graph)

            if len(copy_graph.nodes) != 0:
                max_node, max_difference = self.get_max_degree_difference_node(copy_graph)
                s_1.append(max_node)
                copy_graph.remove_node(max_node)

        return s_1 + s_2

    def get_level_dic(self):
        y_attributes = nx.get_node_attributes(self.graph, 'y')
        level_dic = {}
        for node in y_attributes.keys():
            level = y_attributes[node]
            if level in level_dic:
                level_dic[level].append(node)
            else:
                level_dic[level] = [node]

        return level_dic

    def assign_prelim_x(self):
        level_dic = self.get_level_dic()
        node_distance = 10
        for level in level_dic.keys():
            node_position = 0
            for node in level_dic[level]:
                self.graph.add_node(node, x=node_position)
                node_position += node_distance

    def longest_path(self):
        node_amount = len(self.graph.nodes)
        sink_counter, sinks = self.get_sinks(self.graph)
        for sink in sinks:
            self.graph.add_node(sink, y=node_amount)

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        non_y_attributes = [node for node in self.graph.nodes if node not in y_attributes.keys()]
        while len(non_y_attributes) != 0:
            for node in non_y_attributes:
                adjacent_successors = list(self.graph.successors(node))
                if all(elem in y_attributes.keys() for elem in adjacent_successors):
                    min_y = node_amount
                    for suc in adjacent_successors:
                        if y_attributes[suc] < min_y:
                            min_y = y_attributes[suc]
                    y_attributes[node] = min_y - 1
                    non_y_attributes = [node for node in self.graph.nodes if node not in y_attributes.keys()]
                    break
        nx.set_node_attributes(self.graph, y_attributes, "y")

    @staticmethod
    def get_max_degree_difference_node(graph: nx.Graph):
        max_difference = -1
        max_node = None
        for node in graph.nodes:
            max_in = graph.in_degree(node)
            max_out = graph.out_degree(node)
            difference = abs(max_in - max_out)
            if difference > max_difference:
                max_difference = difference
                max_node = node

        return max_node, max_difference

    @staticmethod
    def get_sinks(graph: nx.DiGraph):
        sinks = []
        for node in graph.nodes:
            if graph.out_degree(node) == 0:
                sinks.append(node)

        return len(sinks), sinks

    @staticmethod
    def get_roots(graph: nx.Graph):
        roots = []
        for node in graph.nodes:
            if graph.in_degree(node) == 0:
                roots.append(node)

        return len(roots), roots

    def draw_graph(self, scale_x=70, scale_y=15, labels=False):
        """
        Draws the current graph from top to bottom. The image is then shown and
        also saved in the output directory with the specified filename.
        The scale parameters define the size of the image.
        :param labels: bool, print labels if True
        :param scale_x: int
        :param scale_y: int
        :return: None
        """
        pos_dict = {}

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        x_attributes = nx.get_node_attributes(self.graph, 'x')
        for node in self.graph.nodes:
            pos_dict[node] = (x_attributes[node], y_attributes[node])

        plt.figure(1, figsize=(scale_x, scale_y))
        nx.draw(self.graph, pos_dict, with_labels=labels)
        plt.gca().invert_yaxis()
        my_graph.save_fig(fig_name=os.path.join("Sugiyama", self.filename))
        plt.show()

    def has_cycle(self):
        reachability = {}
        for node in self.graph.nodes:
            reachable_nodes = []
            active_nodes = []
            active_nodes += list(self.graph.successors(node))
            while active_nodes:
                current_node = active_nodes[0]
                if current_node not in reachable_nodes:
                    reachable_nodes.append(current_node)
                    active_nodes += list(self.graph.successors(current_node))

                del active_nodes[0]

            reachability[node] = reachable_nodes

        has_cycle = False
        cycle_amount = 0
        for key, value in reachability.items():
            if key in value:
                cycle_amount += 1
                print(Color.YELLOW, "CYCLE: ", key, ": ", value, Color.END)
                has_cycle = True

        print(Color.RED, "Cycles: ", cycle_amount, Color.END)

        return has_cycle
