import sys
import os

import networkx as nx

from draw_graph import DrawGraph
from graph import Graph

from newick import read as newick_read

graph_directory = 'directed_graph_examples'


def run():
    graph_filename = ""

    if len(sys.argv) > 1:
        for argument in sys.argv:
            if '=' not in argument:
                continue
            key, value = argument.split("=")
            if key == "-g":
                graph_filename = value
    else:
        print('Missing graph file!')
        exit(1)

    digraph = True
    multi_graph = False

    new_graph = Graph()
    new_graph.read_graph_from_file_list(filename=graph_filename, digraph=digraph, multi_graph=multi_graph)
    new_graph.print_edges()
    new_graph.print_nodes()

    new_draw_graph = DrawGraph(new_graph)
    new_draw_graph.draw_random_graph(digraph=digraph)


def parse_graphml_file(filename: str):
    g = nx.read_graphml(filename)
    g = g.to_directed()
    drawing_graph = DrawGraph(g)
    drawing_graph.draw_circular_layout(labels=False, filename=filename)


def parse_newick_file(filename: str, digraph=True):
    tree = newick_read(filename)

    if digraph:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph

    while tree:
        node = tree[0]
        descendants = node.descendants
        graph.add_node(node.name)
        for to_node in descendants:
            graph.add_edge(node.name, to_node.name)

        tree.remove(node)
        tree += descendants

    drawing_graph = DrawGraph(graph)
    drawing_graph.draw_circular_layout(labels=True, filename=filename)


def parse_and_draw_all_newick_files_in_dir(directory: str):
    print('Parsing Files In', directory, ':')
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(os.path.join(graph_directory, directory, filename))
        parse_newick_file(os.path.join(graph_directory, directory, filename))


def parse_and_draw_all_graphml_files_in_dir(directory: str):
    print('Parsing Files In', directory, ':')
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(os.path.join(graph_directory, directory, filename))
        parse_graphml_file(os.path.join(graph_directory, directory, filename))


if __name__ == '__main__':
    # run()
    parse_and_draw_all_graphml_files_in_dir('graphml')
    # parse_and_draw_all_newick_files_in_dir('Phylogeny')
    # parse_and_draw_all_newick_files_in_dir('Phylogeny-Binaer')
