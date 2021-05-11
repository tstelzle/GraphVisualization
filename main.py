import os
import sys

import newick
from newick import read as newick_read

from improved_walker_algorithm import *
from module_graph import *

graph_directory = 'directed_graph_examples'


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


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
            if argument == "-wn":
                parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny')
                parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny-Binaer')
            if argument == '-wg':
                parse_and_draw_all_graphml_files_with_improved_walter_algorithm('graphml')

    else:
        print('No Parameter specified - Don\'t know what to do!')
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


def parse_graphml_file_newick_format(filename: str, digraph=True):
    """
    Parses a graphml file and return the networkx graph. Forces each node to be in the newick.Node format.
    :param filename: str; full path of the to be parsed file
    :param digraph: Bool; is the graph a digraph
    :return: nx.Graph()
    """
    graphml_graph = nx.read_graphml(filename, node_type=newick.Node)
    if digraph:
        graphml_graph = graphml_graph.to_directed()

    for current_node in graphml_graph.nodes:
        graphml_graph.add_node(current_node, name=node, child_position=0)

    return graphml_graph


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
        tree_node = tree[0]
        tree_node, none_counter = rename_none_node(tree_node, none_counter)
        graph_newick, descendants, none_counter = add_newick_node_and_edge(graph_newick, tree_node, none_counter)
        tree += descendants
        tree.remove(tree_node)

    return graph_newick


def add_newick_node_and_edge(nx_graph: nx.Graph, current_node, none_counter: int):
    """
    Adding the descendants of the current node to the graph and adding the according edge.
    Rename a node if the name is None.
    :param nx_graph: the network x graph to which node and edge should be added
    :param current_node: the current node from the newick graph
    :param none_counter: an integer representing the amount of None node
    :return: (graph, descendants, none_counter)
    """
    descendants = current_node.descendants
    for child_pos in range(len(descendants)):
        descendants[child_pos], none_counter = rename_none_node(descendants[child_pos], none_counter)
        nx_graph.add_node(descendants[child_pos], child_position=child_pos)
        nx_graph.add_edge(current_node, descendants[child_pos])

    return nx_graph, descendants, none_counter


def rename_none_node(node_to_rename: newick.Node, counter):
    """
    Renaming node with no name to differ from other not named node.
    :param node_to_rename: node to be checked
    :param counter: int; counter for none nodes
    :return: (Node, int)
    """
    if node_to_rename.name is None:
        node_to_rename.name = str(node_to_rename.name) + "_" + str(counter)
        counter += 1
    return node_to_rename, counter


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


def parse_and_draw_all_newick_files_with_improved_walker_algorithm(directory: str):
    """
    Parses and draws all newick files from the examples with the implemented Improved Walker Algorithm.
    :param directory: str, directory for the newick files
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory + ':', Color.END)
    improved_walker_algorithm_object = ImprovedWalkerAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_newick_graph = parse_newick_file(os.path.join(graph_directory, directory, filename))
        scale_x = 20
        scale_y = 20
        if 'eboVir' in filename:
            scale_x = 80
            scale_y = 40
        elif '7way' in filename:
            scale_x = 5
            scale_y = 10
        elif 'hg38.100way' in filename or 'phyliptree' in filename:
            scale_x = 60
        elif 'hg38.100way.commonNames' in filename or 'hhg38.100way.scientificNames' in filename:
            scale_x = 100
        elif 'ce11.26way.commonNames' in filename or 'ce11.26way.scientificNames' in filename:
            scale_x = 40
        improved_walker_algorithm_object.run(current_newick_graph,
                                             filename=os.path.join(graph_directory, directory, filename),
                                             scale_x=scale_x,
                                             scale_y=scale_y)


def parse_and_draw_all_graphml_files_with_improved_walter_algorithm(directory: str):
    """
    Parses and draws all graphml files from the examples with the implemented Improved Walker Algorithm.
    (The current examples are not suitable for the Improved Walker Algorithm.
    :param directory: str, directory for the graphml files
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory, ':' + Color.END)
    improved_walker_algorithm_object = ImprovedWalkerAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_graphml_graph = parse_graphml_file_newick_format(os.path.join(graph_directory, directory, filename))
        improved_walker_algorithm_object.run(current_graphml_graph,
                                             filename=os.path.join(graph_directory, directory, filename))


if __name__ == '__main__':
    parse_parameters()
