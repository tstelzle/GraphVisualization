import networkx as nx
import newick
import copy


def parse_graphml_file(filename: str, digraph=True):
    """
    Parses a graphml file and return the networkx graph. Forces each node to be in the newick.Node format.
    :param filename: str; full path of the to be parsed file
    :param digraph: Bool; is the graph a digraph
    :return: nx.Graph()
    """
    graphml_graph = nx.read_graphml(filename)

    if digraph:
        graphml_graph = nx.DiGraph(graphml_graph)

    for current_node in graphml_graph.nodes:
        multiple_parents = []
        one_parent = []
        child_list = list(graphml_graph.successors(current_node))
        for child_pos in range(len(child_list)):
            child = child_list[child_pos]
            parent_list = list(graphml_graph.predecessors(child))
            if len(parent_list) > 1:
                multiple_parents.append(child)
            else:
                one_parent.append(child)

        if len(multiple_parents) == 0:
            for child_pos in range(len(child_list)):
                child = child_list[child_pos]
                graphml_graph.add_node(child, name=child, child_position=child_pos)
        else:
            # The child position can have spaces.
            # This is intended, hence the code can not iterate over the keys in edges_to.
            # This cannot be fixed, as a two child could need the same child_position -> Error
            child_position_attributes = nx.get_node_attributes(graphml_graph, 'child_position')
            fixed_positions = {}
            for child in child_list:
                try:
                    child_position = child_position_attributes[child]
                    fixed_positions[child_position] = child
                except KeyError:
                    continue

            for child_pos in range(len(multiple_parents)):
                child = multiple_parents[child_pos]
                if child_pos in fixed_positions.keys():
                    child_pos += 1
                    continue
                if child in fixed_positions.values():
                    continue
                graphml_graph.add_node(child, name=child, child_position=child_pos)

            for child_pos in range(len(multiple_parents) + 1, len(one_parent) + len(multiple_parents)):
                child = one_parent[child_pos - len(multiple_parents)]
                if child_pos - len(multiple_parents) in fixed_positions.keys():
                    child_pos += 1
                    continue
                if child in fixed_positions.values():
                    continue
                graphml_graph.add_node(child, name=child, child_position=child_pos)

    for node in graphml_graph.nodes:
        position_attributes = nx.get_node_attributes(graphml_graph, 'child_position')
        try:
            position_attributes[node]
        except KeyError:
            graphml_graph.add_node(node, name=node, child_position=0)

    return graphml_graph


def parse_newick_file_by_name(filename: str, digraph=True):
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
    if tree[0].name is None:
        graph_newick.add_node("None_1", child_position=0)
        none_counter += 1
    else:
        graph_newick.add_node(tree[0].name, child_position=0)

    while tree:
        tree_node = tree[0]
        tree_node, none_counter = rename_none_node(tree_node, none_counter)
        graph_newick, descendants, none_counter = add_newick_node_and_edge_by_name(graph_newick, tree_node, none_counter)
        tree += descendants
        tree.remove(tree_node)

    return graph_newick


def add_newick_node_and_edge_by_name(nx_graph: nx.Graph, current_node, none_counter: int):
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
        nx_graph.add_node(descendants[child_pos].name, child_position=child_pos)
        nx_graph.add_edge(current_node.name, descendants[child_pos].name)

    return nx_graph, descendants, none_counter



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
