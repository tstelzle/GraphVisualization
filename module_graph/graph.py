class Graph:
    """
    Implements a representation of a graph.
    """

    def __init__(self):
        self.node_list = []
        self.edge_list = []

    def get_node_list(self):
        """
        Returns the list of nodes of the current graph.
        :return: [str]
        """
        return self.node_list

    def get_edge_list(self):
        """
        Returns the list of dictionaries, which represent edges within the current graph.
        :return: [{'from', 'to'}]
        """
        return self.edge_list

    def read_graph_from_file_list(self, filename: str, digraph=True, multi_graph=False):
        """
        Reads the graph from a file. The graph should be wrote in a list format.
        Each line is a node. After a colon a list of reachable nodes is listed. This list is separated by commas.
        :param filename: filename of the graph file
        :param digraph: Is the graph a digraph?; default True
        :param multi_graph: Is the graph a multi-graph?; default False
        :return: None
        """
        file = open(filename)

        for line in file:
            line = line.replace("\n", '')
            from_vertex, to_vertices = line.split(':')
            self.node_list.append(from_vertex)
            if not to_vertices:
                continue
            to_vertices_list = to_vertices.split(',')
            for v in to_vertices_list:
                one_way_dic = {'from': from_vertex, 'to': v}
                self.edge_list.append(one_way_dic)

                if digraph is False and v is not from_vertex:
                    return_dic = {'from': v, 'to': from_vertex}
                    self.edge_list.append(return_dic)

        if multi_graph is False:
            self.edge_list = remove_duplicate_dictionaries(self.edge_list)

    def print_edges(self):
        """
        Prints the list of edges from the current graph in the format 'from' -> 'to'.
        :return: None
        """
        for edge in self.edge_list:
            print(edge['from'] + " -> " + edge['to'])

    def print_nodes(self):
        """
        Prints the nodes of the current graph as a list.
        :return: None
        """
        print(", ".join(self.node_list))

    def count_edges(self):
        """
        Returns the amount of nodes in the current graph.
        :return: int
        """
        return len(self.edge_list)

    def count_nodes(self):
        """
        Returns the amount of edges in the current graph.
        :return: int
        """
        return len(self.node_list)


def remove_duplicate_dictionaries(input_list: list):
    """
    Removes duplicate dictionaries from a list of dictionaries.
    :param input_list: [{}]
    :return: [{}]
    """
    return [k for j, k in enumerate(input_list) if k not in input_list[:j]]
