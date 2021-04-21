import matplotlib.pyplot as plt
import networkx as nx
import numpy
import os

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


def create_missing_dir(path):
    """
    Creates missing directories. Skips if the directory already exists.
    :param path: str; Directory path
    :return: None
    """
    if not (os.path.exists(path) and os.path.isdir(path)):
        os.makedirs(path)


def save_fig(fig_name: str):
    """
    Function to save a plt figure with the given figure name.
    :param fig_name: str; Filename for the saved figure
    :return: None
    """
    directories = '/'.join(fig_name.split('/')[:-1])
    create_missing_dir('output/' + directories)
    plt.savefig('output/' + fig_name + '.png', dpi=500, bbox_inches=None, format=None)


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
        """
        Returns a list of all the edges within the graph
        :return: []
        """
        return self.edges

    def is_directed(self):
        """
        Returns the graph is a digraph.
        :return: Bool
        """
        return self.graph.is_directed()

    def draw_random_graph(self, digraph=True, labels=False, filename='random'):
        """
        Show a random representation of the graph.
        :param filename: filename for the figure
        :param labels: Should the labels for the nodes be drawn
        :param digraph: Should the representation be a digraph; default True
        :return: None
        """
        # could include duplicates
        colors = numpy.random.uniform(0, 1, len(self.graph.nodes))

        pos = nx.random_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size=500, node_color=colors)
        if labels:
            nx.draw_networkx_labels(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, edgelist=self.edges, arrows=digraph)
        save_fig(filename)
        plt.show()

    def draw_circular_layout(self, digraph=True, labels=False, filename='circular'):
        """
        Show a circular representation of the graph.
        :param filename: filename for the figure
        :param labels: Should the labels for the nodes be drawn
        :param digraph: Should the representation be a digraph; default True
        :return: None
        """
        colors = numpy.random.uniform(0, 1, len(self.graph.nodes))

        pos = nx.circular_layout(self.graph, scale=1)
        nx.draw_networkx_nodes(self.graph, pos, cmap=plt.get_cmap('jet'), node_size=50, node_color=colors)
        if labels:
            nx.draw_networkx_labels(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, edgelist=self.edges, arrows=digraph)
        save_fig(filename)
        plt.show()

    def draw_tree(self, labels=False, filename='tree'):
        """
        Show a graphvis (tree) representation of the graph.
        :param filename: filename for the figure
        :param labels: Should the labels for the nodes be drawn
        :param digraph: Should the representation be a digraph; default True
        :return: None
        """
        pos = graphviz_layout(self.graph, prog="dot", args="")
        plt.figure(figsize=(8, 8))
        nx.draw(self.graph, pos, node_size=250, alpha=0.5, node_color="blue", with_labels=labels)
        save_fig(filename)
        plt.show()
