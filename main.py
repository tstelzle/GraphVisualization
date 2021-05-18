import os
import sys

from improved_walker_algorithm import *
from module_parse import *
from module_color import Color
from sugiyama_algorithm import SugiyamaAlgorithm

graph_directory = 'directed_graph_examples'


def parse_parameters():
    if len(sys.argv) > 1:
        for argument in sys.argv:
            if '-' not in argument:
                continue

            if argument == "-wn":
                parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny')
                parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny-Binaer')
            if argument == '-wg':
                parse_and_draw_all_graphml_files_with_improved_walter_algorithm('graphml')
            if argument == "-sn":
                parse_and_draw_all_newick_files_with_sugiyama_algorithm('Phylogeny')
                parse_and_draw_all_newick_files_with_sugiyama_algorithm('Phylogeny-Binaer')
            if argument == "-sg":
                parse_and_draw_all_graphml_files_with_sugiyama_algorithm('graphml')
    else:
        print('No Parameter specified - Don\'t know what to do!')
        exit(1)


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


def parse_and_draw_all_newick_files_with_sugiyama_algorithm(directory: str):
    print(Color.UNDERLINE + 'Parsing Files In', directory + ':', Color.END)
    sugiyama_algorithm_object = SugiyamaAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_newick_graph = parse_newick_file(os.path.join(graph_directory, directory, filename))
        sugiyama_algorithm_object.run(current_newick_graph)


def parse_and_draw_all_graphml_files_with_sugiyama_algorithm(directory: str):
    """
    Parses and draws all graphml files from the examples with the implemented Improved Walker Algorithm.
    (The current examples are not suitable for the Improved Walker Algorithm.
    :param directory: str, directory for the graphml files
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory, ':' + Color.END)
    sugiyama_algorithm_object = SugiyamaAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_graphml_graph = parse_graphml_file_newick_format(os.path.join(graph_directory, directory, filename))
        sugiyama_algorithm_object.run(current_graphml_graph)


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
