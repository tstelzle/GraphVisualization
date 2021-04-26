import sys
import os

import networkx as nx

from module_graph import *

from newick import read as newick_read

graph_directory = 'directed_graph_examples'


def parse_parameters():
    if len(sys.argv) > 1:
        for argument in sys.argv:
            if '-' not in argument:
                continue

            if '=' in argument:
                key, value = argument.split('=')
                if key == '-o':
                    run(value)

            if argument == "-g":
                parse_and_draw_all_graphml_files_in_dir('graphml')
            if argument == "-n":
                parse_and_draw_all_newick_files_in_dir('Phylogeny')
                parse_and_draw_all_newick_files_in_dir('Phylogeny-Binaer')
    else:
        print('Missing graph file!')
        exit(1)


def run(graph_filename: str):
    """
    Parses a txt file with a adjacent list representation of a graph and draws the given graph with a random layout.
    :return: None
    """
    digraph = True
    multi_graph = False

    new_graph = Graph()
    new_graph.read_graph_from_file_list(filename=graph_filename, digraph=digraph, multi_graph=multi_graph)
    new_graph.print_edges()
    new_graph.print_nodes()

    new_draw_graph = DrawGraph(new_graph, False)
    new_draw_graph.draw_random_graph(digraph=digraph)


def parse_graphml_file(filename: str, digraph=True):
    """
    Parses a graphml file and return the networkx graph.
    :param filename: str; full path of the to be parsed file
    :param digraph: Bool; is the graph a digraph
    :return: nx.Graph()
    """
    graphml_graph = nx.read_graphml(filename)
    if digraph:
        graphml_graph = graphml_graph.to_directed()

    return graphml_graph


def draw_networkx_graph(nx_graph: nx.Graph, labels, filename: str, tree=False):
    """
    Draws a given networkx graph with a tree or circular layout.
    :param tree: Bool; Drawn as tree
    :param nx_graph: networkx Graph
    :param labels: Bool; Labels to be shown
    :param filename: str; for saving the image
    :return:
    """
    draw_nx_graph = DrawGraph(nx_graph)
    if tree:
        draw_nx_graph.draw_tree(labels=labels, filename=filename)
    else:
        draw_nx_graph.draw_circular_layout(labels=labels, filename=filename)


def parse_newick_file(filename: str, digraph=True):
    """
    Parses a newick file and returns the networkx graph.
    :param filename: str; full path of the to be parsed file
    :param digraph: Bool; is the graph a digraph
    :return: nx.Graph()
    """
    tree = newick_read(filename)

    if digraph:
        graph_newick = nx.DiGraph()
    else:
        graph_newick = nx.Graph

    none_counter = 1

    while tree:
        node = tree[0]
        descendants = node.descendants
        node, none_counter = rename_none_node(node, none_counter)
        graph_newick.add_node(node.name)
        for to_node in descendants:
            to_node, none_counter = rename_none_node(to_node, none_counter)
            graph_newick.add_edge(node.name, to_node.name)

        tree.remove(node)
        tree += descendants

    return graph_newick


def rename_none_node(node, counter):
    """
    Renaming node with no name to differ from other not named node.
    :param node: node to be checked
    :param counter: int; counter for none nodes
    :return: (Node, int)
    """
    if node.name is None:
        node.name = str(node.name) + "_" + str(counter)
        counter += 1
    return node, counter


def parse_and_draw_all_newick_files_in_dir(directory: str):
    """
    Parses and draws all newick files in the given directory.
    :param directory: name of the directory (has to be in the directed_graph_examples directory)
    :return: None
    """
    print('Parsing Files In', directory, ':')
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(os.path.join(graph_directory, directory, filename))
        current_newick_graph = parse_newick_file(os.path.join(graph_directory, directory, filename))
        draw_networkx_graph(current_newick_graph,
                            filename=os.path.join(graph_directory, directory, filename),
                            labels=True,
                            tree=True)


def parse_and_draw_all_graphml_files_in_dir(directory: str):
    """
    Parses and draws all graphml files in the given directory.
    :param directory: name of the directory (has to be in the directed_graph_examples directory)
    :return: None
    """
    print('Parsing Files In', directory, ':')
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(os.path.join(graph_directory, directory, filename))
        current_graphml_graph = parse_graphml_file(os.path.join(graph_directory, directory, filename))
        draw_networkx_graph(current_graphml_graph,
                            filename=os.path.join(graph_directory, directory, filename),
                            labels=False)


if __name__ == '__main__':
    parse_parameters()
