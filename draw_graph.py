import matplotlib.pyplot as plt
import networkx as nx
import numpy

from own_graph import OwnGraph


def convert_edges(graph: OwnGraph):
    """
    Converts the edges from the OwnGraph to match the nx graph packages
    :param graph: OwnGraph
    :return: [(from, to)]
    """
    edges = []
    for edge in graph.get_edge_list():
        edges.append((edge['from'], edge['to']))

    return edges


class DrawGraph:
    """
    This class is used to draw object of OwnGraph.
    """

    def __init__(self, own_graph: OwnGraph):
        self.graph = nx.DiGraph()
        self.edges = convert_edges(own_graph)

        self.graph.add_edges_from(self.edges)

    def draw_random_graph(self, digraph=True):
        """
        Show a random representation of the graph.
        :param digraph: Should the representation be a digraph; default True
        :return: None
        """
        # could include duplicates
        colors = numpy.random.uniform(0, 1, len(self.graph.nodes))

        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size=500, node_color=colors)
        nx.draw_networkx_labels(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, edgelist=self.edges, arrows=digraph)
        plt.show()
