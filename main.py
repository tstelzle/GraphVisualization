import os
import sys

import newick
from newick import read as newick_read

from improved_walker_algorithm import *
from module_graph import *

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

    # Adding root node
    graph_newick.add_node(tree[0], child_position=0)

    while tree:
        node = tree[0]
        node, none_counter = rename_none_node(node, none_counter)
        graph_newick, descendants, none_counter = add_newick_node_and_edge(graph_newick, node, none_counter)
        tree += descendants
        tree.remove(node)

    return graph_newick


def add_newick_node_and_edge(graph: nx.Graph, current_node, none_counter: int):
    """
    Adding the descendants of the current node to the graph and adding the according edge.
    Rename a node if the name is None.
    :param graph: the network x graph to which node and edge should be added
    :param current_node: the current node from the newick graph
    :param none_counter: an integer representing the amount of None node
    :return: (graph, descendants, none_counter)
    """
    descendants = current_node.descendants
    for child_pos in range(len(descendants)):
        descendants[child_pos], none_counter = rename_none_node(descendants[child_pos], none_counter)
        graph.add_node(descendants[child_pos], child_position=child_pos)
        graph.add_edge(current_node, descendants[child_pos])

    return graph, descendants, none_counter


def rename_none_node(node: newick.Node, counter):
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
    # parse_parameters()
    graph = parse_newick_file(os.path.join(graph_directory, 'Phylogeny-Binaer', 'hg38.20way.commonNames.nh'))
    # graph = parse_newick_file(os.path.join(graph_directory, 'Phylogeny-Binaer', '7way.nh'))
    # graph = parse_newick_file(os.path.join(graph_directory, 'Phylogeny-Binaer', 'ce11.26way.commonNames.nh'))
    # graph = parse_graphml_file(os.path.join(graph_directory, 'graphml', 'Checkstyle-6.5.graphml'), digraph=False)
    improved_walker_algorithm = ImprovedWalkerAlgorithm()
    improved_walker_algorithm.run(graph, 'test')

    # graph = parse_graphml_file(os.path.join(graph_directory, 'graphml', 'Checkstyle-6.5.graphml'), digraph=False)
    # draw_networkx_graph(graph, labels=False, filename='output_2')
