import os
import argparse
import sys

import sugiyama_algorithm.sugiyama_nx
from improved_walker_algorithm import *
from module_color import Color
from module_parse import *
from sugiyama_algorithm import SugiyamaAlgorithm

graph_directory = 'directed_graph_examples'


def parse_parameters():
    parser = argparse.ArgumentParser(description='Run graph layout algorithms on given example files.')
    parser.add_argument("-w", "--walker", action="store_true",
                        dest="walker", default=False, help="Improved Walker Algorithm")
    parser.add_argument("-s", "--sugiyama", action="store_true",
                        dest="sugiyama", default=False, help="Sugiyama Algorithm")
    parser.add_argument("-g", "--graphml", action="store_true",
                        dest="graphml", default=False, help="Using Graphml Files")
    parser.add_argument("-n", "--newick", action="store_true",
                        dest="newick", default=False, help="Using Newick Files")
    parser.add_argument("-t", "--tests", action="store_true",
                        dest="tests", default=False, help="Running Tests")
    parser.add_argument("-sx", "--sugiyama-networkx", action="store_true",
                        dest="sugiyama_x", default=False, help="Sugiyama Algorithm With NetworkX")

    options = parser.parse_args()

    if not options.walker and not options.sugiyama and not options.sugiyama_x:
        print(Color.RED, "No Algorithm Specified - STOPPING", Color.END)
        sys.exit()
    if not options.newick and not options.graphml:
        print(Color.RED, "No File Format Specified - STOPPING", Color.END)
        sys.exit()

    if options.walker:
        print(Color.GREEN, "Running Improved Walker Algorithm", Color.END)
        if options.newick:
            parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny', options.tests)
            parse_and_draw_all_newick_files_with_improved_walker_algorithm('Phylogeny-Binaer', options.tests)
        if options.graphml:
            parse_and_draw_all_graphml_files_with_improved_walter_algorithm('graphml', options.tests)

    if options.sugiyama_x:
        print(Color.GREEN, "Running Sugiyama Algorithm With NetworkX", Color.END)
        if options.graphml:
            parse_and_draw_all_graphml_files_with_sugiyama_algorithm_nx('graphml')
        if options.newick:
            parse_and_draw_all_newick_files_with_sugiyama_algorithm_nx('Phylogeny')
            parse_and_draw_all_newick_files_with_sugiyama_algorithm_nx('Phylogeny-Binaer')

    if options.sugiyama:
        print(Color.GREEN, "Running Sugiyama Algorithm", Color.END)
        if options.newick:
            parse_and_draw_all_newick_files_with_sugiyama_algorithm('Phylogeny', options.tests)
            parse_and_draw_all_newick_files_with_sugiyama_algorithm('Phylogeny-Binaer', options.tests)
        if options.graphml:
            parse_and_draw_all_graphml_files_with_sugiyama_algorithm('graphml', options.test)


def parse_and_draw_all_newick_files_with_improved_walker_algorithm(directory: str, test: bool):
    """
    Parses and draws all newick files from the examples with the implemented Improved Walker Algorithm.
    :param directory: str, directory for the newick files
    :param test: bool, True if self implemented should be run
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
                                             filename=os.path.join('Walker', graph_directory, directory, filename),
                                             scale_x=scale_x,
                                             scale_y=scale_y,
                                             test=test)


def parse_and_draw_all_newick_files_with_sugiyama_algorithm(directory: str, test: bool):
    """
    Parses and draws all newick files from the examples with the implemented Sugiyama Algorithm.
    :param directory: str, directory for the newick files
    :param test: bool, True if self implemented should be run
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory + ':', Color.END)
    sugiyama_algorithm_object = SugiyamaAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_newick_graph = parse_newick_file(os.path.join(graph_directory, directory, filename))
        try:
            sugiyama_algorithm_object.run_sugiyama(current_newick_graph,
                                                   filename=os.path.join('Sugiyama',
                                                                         graph_directory, directory, filename),
                                                   test=test)
        except Exception as error:
            if error.args[0] == "Cycle":
                continue


def parse_and_draw_all_graphml_files_with_sugiyama_algorithm(directory: str, test: bool):
    """
    Parses and draws all graphml files from the examples with the implemented Sugiyama Algorithm.
    :param directory: str, directory for the graphml files
    :param test: bool, True if self implemented should be run
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory, ':' + Color.END)
    sugiyama_algorithm_object = SugiyamaAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_graphml_graph = parse_graphml_file(os.path.join(graph_directory, directory, filename))
        try:
            sugiyama_algorithm_object.run_sugiyama(current_graphml_graph,
                                                   filename=os.path.join('Sugiyama', graph_directory, directory,
                                                                         filename),
                                                   graphml=True,
                                                   test=test)
        except Exception as error:
            if error.args[0] == "Cycle":
                continue


def parse_and_draw_all_graphml_files_with_sugiyama_algorithm_nx(directory: str):
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        file_path = os.path.join(graph_directory, directory, filename)
        current_graphml_graph = parse_graphml_file(file_path)
        sugiyama_algorithm_object = sugiyama_algorithm.sugiyama_nx.SugiyamaNX(file_path, current_graphml_graph)
        sugiyama_algorithm_object.run_sugiyama()


def parse_and_draw_all_newick_files_with_sugiyama_algorithm_nx(directory: str):
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        file_path = os.path.join(graph_directory, directory, filename)
        current_graphml_graph = parse_newick_file_by_name(file_path)
        sugiyama_algorithm_object = sugiyama_algorithm.sugiyama_nx.SugiyamaNX(file_path, current_graphml_graph)
        sugiyama_algorithm_object.run_sugiyama()


def parse_and_draw_all_graphml_files_with_improved_walter_algorithm(directory: str, test: bool):
    """
    Parses and draws all graphml files from the examples with the implemented Improved Walker Algorithm.
    (The current examples are not suitable for the Improved Walker Algorithm.)
    :param directory: str, directory for the graphml files
    :param test: bool, True if self implemented should be run
    :return: None
    """
    print(Color.UNDERLINE + 'Parsing Files In', directory, ':' + Color.END)
    improved_walker_algorithm_object = ImprovedWalkerAlgorithm()
    for filename in os.listdir(os.path.join(graph_directory, directory)):
        print(Color.BOLD + os.path.join(graph_directory, directory, filename) + Color.END)
        current_graphml_graph = parse_graphml_file(os.path.join(graph_directory, directory, filename))
        try:
            improved_walker_algorithm_object.run(current_graphml_graph,
                                                 filename=os.path.join('Walker', graph_directory, directory, filename),
                                                 graphml=True,
                                                 test=test)
        except Exception as error:
            if error.args[0] == "Multiple Parents":
                continue


if __name__ == '__main__':
    parse_parameters()
