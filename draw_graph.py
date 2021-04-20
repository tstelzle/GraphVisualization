import matplotlib.pyplot as plt
import networkx as nx
import numpy

from graph import Graph as ownGraph

# This example needs Graphviz and either PyGraphviz or pydot
# from networkx.drawing.nx_pydot import graphviz_layout
from networkx.drawing.nx_agraph import graphviz_layout


def convert_edges(graph: ownGraph):
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

    def __init__(self, own_graph: ownGraph):
        self.graph = nx.DiGraph()
        self.edges = convert_edges(own_graph)

        self.graph.add_edges_from(self.edges)

    def __init__(self, graph):
        self.graph = graph
        self.edges = self.graph.edges()

    def get_edges(self):
        return self.edges

    def draw_random_graph(self, digraph=True, labels=False):
        """
        Show a random representation of the graph.
        :param digraph: Should the representation be a digraph; default True
        :return: None
        """
        # could include duplicates
        colors = numpy.random.uniform(0, 1, len(self.graph.nodes))

        pos = nx.circular_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size=500, node_color=colors)
        if labels:
            nx.draw_networkx_labels(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, edgelist=self.edges, arrows=digraph)
        plt.show()

    def draw_tree(self, labels=False):
        pos = graphviz_layout(self.graph, prog="dot", args="")
        plt.figure(figsize=(8, 8))
        nx.draw(self.graph, pos, node_size=250, alpha=0.5, node_color="blue", with_labels=labels)
        # plt.axis("equal")
        # plt.savefig('output/graph.png', dpi=500, bbox_inches=None, format=None)
        plt.show()