import sys

import networkx as nx

from draw_graph import DrawGraph
from graph import Graph

from newick import read as newick_read


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

    drawing_graph = DrawGraph(g)
    drawing_graph.draw_tree()


def parse_newick_file(filename: str):
    tree = newick_read(filename)

    print(tree)


if __name__ == '__main__':
    # run()
    parse_graphml_file('directed_graph_examples/graphml/Checkstyle-6.5.graphml')
    # parse_newick_file('directed_graph_examples/Phylogeny-Binaer/7way.nh')
    # parse_newick_file('directed_graph_examples/Phylogeny/phyliptree.nh')
