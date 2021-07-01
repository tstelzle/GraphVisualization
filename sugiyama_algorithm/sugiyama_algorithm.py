import networkx as nx

from module_graph import Graph
from copy import deepcopy

from module_color import Color


class SugiyamaAlgorithm:

    # TODO Eigene zyklische Graphen erstellen lassen networkx.scale_free_graph
    #   https://networkx.org/documentation/networkx-1.0/reference/generated/networkx.scale_free_graph.html#networkx.scale_free_graph

    def __init__(self):
        self.graph = Graph()

    def __tree_layout(self, nx_graph: nx.Graph, graphml: bool, loop):
        if graphml:
            self.graph = Graph.create_graph_from_graphml(nx_graph, loop=loop)
        else:
            self.graph = Graph.create_graph_from_newick(nx_graph, loop=loop)

    def test_cycle(self):
        has_cycle = self.has_cycle()
        needed_node_names = self.greedy_cycle_removal()
        cyclic_nodes = self.get_cyclic_nodes(needed_node_names)

        if has_cycle and len(cyclic_nodes) > 0:
            return True

        if not has_cycle and len(cyclic_nodes) == 0:
            return True

        print(Color.RED + "Cycle Not Removed" + Color.END)
        raise Exception('Cycle')

    def run_sugiyama(self, nx_graph: nx.Graph, filename: str, graphml=False, test=False):
        """
        :param nx_graph: Networkx Graph, for which the algorithm should be run
        :param filename: str, filename where the plotted graph should be saved
        :param graphml: bool, if the given nx_graph was read from a graphml file
        :param test: bool, True if doctest should be run
        """
        self.__tree_layout(nx_graph, graphml, loop=False)
        if test:
            print("Test Cycle: ", self.test_cycle())
        needed_node_names = self.greedy_cycle_removal()
        self.remove_cyclic_nodes(needed_node_names)
        self.longest_path()
        level_dict = self.graph.get_level_with_nodes()
        for level, nodes in level_dict.items():
            print(level, ":", nodes)
        self.graph.assign_preliminary_x()
        # self.graph.print_nodes_coordinates()
        self.graph.draw_graph(filename=filename, labels=False, scale_x=70, scale_y=15)

    def get_cyclic_nodes(self, needed_node_names):
        """
        Returns a list of the nodes which have to be removed in order that there are no cycles in the graph.
        :param needed_node_names: list, needed nodes in the graph
        :return: list, the nodes which need to be removed
        """
        return [node for node in self.graph.nodes if node.name not in needed_node_names]

    def remove_cyclic_nodes(self, needed_node_names: []):
        # TODO all nodes are needed -> hence greedy_cycle_removal does not work
        # print('Needed Nodes:', needed_node_names)
        cyclic_nodes = self.get_cyclic_nodes(needed_node_names)
        print("Cyclic Nodes: ", cyclic_nodes)
        for node in cyclic_nodes:
            self.graph.remove_node(node)
            print('Removing node', node.name)

    def greedy_cycle_removal(self):
        """
        This method figures out the nodes, which are needed so that there is no cycle in the graph.
        :return: list, List of needed nodes
        """
        copy_graph = deepcopy(self.graph)
        s_1 = []
        s_2 = []
        while copy_graph.nodes:
            sinks_counter, sinks = copy_graph.count_sinks()
            while sinks_counter > 0:
                sink = sinks.pop(0)
                sinks_counter -= 1
                copy_graph.remove_node_by_name(sink)
                s_2.append(sink)
                sinks_counter, sinks = copy_graph.count_sinks()
            sources_counter, sources = copy_graph.count_roots()
            while sources_counter > 0:
                source = sources.pop(0)
                sources_counter -= 1
                copy_graph.remove_node_by_name(source)
                s_1.append(source)
                sources_counter, sources = copy_graph.count_roots()
            if copy_graph.nodes:
                max_value, max_node = copy_graph.get_maximal_degree_difference_node_name()
                copy_graph.remove_node_by_name(max_node)

        return s_1 + s_2

    def longest_path(self):
        m = len(self.graph.nodes)
        sink_counter, sinks = self.graph.count_sinks()
        for sink in sinks:
            node_sink = self.graph.get_node_by_name(sink)
            node_sink.y = m

        no_y_nodes_counter, no_y_nodes = self.graph.get_nodes_without_y()
        while no_y_nodes_counter != 0:
            for node in no_y_nodes:
                neighbour, minimum = node.neighbours_have_y(m)
                if neighbour:
                    node.y = minimum - 1
                    break
            no_y_nodes_counter, no_y_nodes = self.graph.get_nodes_without_y()

    def has_cycle(self):
        reachability = {}
        for node in self.graph.nodes:
            reachable_nodes = []
            active_nodes = []
            active_nodes += node.edges_to.values()
            while active_nodes:
                current_node = active_nodes[0]
                if current_node.name not in reachable_nodes:
                    reachable_nodes.append(current_node.name)
                    active_nodes += current_node.edges_to.values()

                del active_nodes[0]

            reachability[node.name] = reachable_nodes

        has_cycle = False
        for key, value in reachability.items():
            if key in value:
                print(Color.YELLOW, "CYCLE: ", key, ": ", value, Color.END)
                has_cycle = True

        return has_cycle
