import networkx as nx
import newick


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
        graphml_graph.add_node(current_node, name=current_node, child_position=0)

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


def parse_newick_file(filename: str, digraph=True):
    """
    Parses a newick file and returns the networkx graph.
    :param filename: str; full path of the to be parsed file
    :param digraph: Bool; is the graph a digraph
    :return: nx.Graph()
    """
    tree = newick.read(filename)

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
