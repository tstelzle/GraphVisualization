import sys

from draw_graph import DrawGraph
from own_graph import OwnGraph


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

    new_graph = OwnGraph()
    new_graph.read_graph_from_file_list(filename=graph_filename, digraph=digraph, multi_graph=multi_graph)
    new_graph.print_edges()
    new_graph.print_nodes()

    new_draw_graph = DrawGraph(new_graph)
    new_draw_graph.draw_random_graph(digraph=digraph)


if __name__ == '__main__':
    run()
