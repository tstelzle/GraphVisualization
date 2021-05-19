import networkx as nx

from module_graph import Graph
from copy import deepcopy


class SugiyamaAlgorithm:

    def __init__(self):
        self.graph = Graph()

    def __tree_layout(self, nx_graph: nx.Graph):
        self.graph = Graph.create_graph_from_nx(nx_graph)

    def run(self, nx_graph: nx.Graph):
        self.__tree_layout(nx_graph)
        needed_nodes = self.greedy_cycle_removal()
        self.remove_cyclic_nodes(needed_nodes)
        self.longest_path()
        self.graph.print_nodes_coordinates()

    def remove_cyclic_nodes(self, needed_nodes: []):
        needed_nodes_names = [node.name for node in needed_nodes]
        print('Needed Nodes:', needed_nodes_names)
        cyclic_nodes = [node for node in self.graph.nodes if node.name not in needed_nodes_names]
        for node in cyclic_nodes:
            self.graph.remove_node(node)
            print('Removing node', node.name)

    def greedy_cycle_removal(self):
        copy_graph = deepcopy(self.graph)
        s_1 = []
        s_2 = []
        while copy_graph.nodes:
            sinks_counter, sinks = copy_graph.count_sinks()
            while sinks_counter > 0:
                sink = sinks[0]
                copy_graph.remove_node(sink)
                s_2.append(sink)
                sinks_counter, sinks = copy_graph.count_sinks()
            sources_counter, sources = copy_graph.count_roots()
            while sources_counter > 0:
                source = sources[0]
                copy_graph.remove_node(source)
                s_1.append(source)
                sources_counter, sources = copy_graph.count_roots()
            if copy_graph.nodes:
                max_value, max_node = self.graph.get_maximal_degree_difference_node()
                copy_graph.remove_node(max_node)

        return s_1 + s_2

    def longest_path(self):
        m = len(self.graph.nodes)
        sink_counter, sinks = self.graph.count_sinks()
        for sink in sinks:
            sink.y = m

        no_y_nodes_counter, no_y_nodes = self.graph.get_nodes_without_y()
        while no_y_nodes_counter != 0:
            for node in no_y_nodes:
                neighbour, minimum = node.neighbours_have_y(m)
                if neighbour:
                    node.y = minimum - 1
                    continue
            no_y_nodes_counter, no_y_nodes = self.graph.get_nodes_without_y()
