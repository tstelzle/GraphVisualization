import copy
import math
import os
import random
import logging
import time

import matplotlib.pyplot as plt
import networkx as nx

from module_color import *


def initialize_output_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, 0o777)


class SugiyamaNX:

    def __init__(self, filename: str, graph: nx.DiGraph, output_directory="output"):
        self.filename = os.path.join(output_directory, "Sugiyama", filename + ".png")
        self.logname = os.path.join(output_directory, "Sugiyama", filename + "_log.log")
        self.filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.filename)
        self.file_directory = "/".join(self.filepath.split('/')[:-1])
        self.graph = graph
        # block_id -> block
        self.block_lookup = {}
        # block_id -> nodes
        self.n_minus = {}
        self.n_plus = {}
        self.i_minus = {}
        self.i_plus = {}
        self.align = {}
        self.root = {}
        self.sink = {}
        self.shift = {}
        self.x = {}
        self.mark_segments = []
        self.delta = 1
        self.pi = {}
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.logger = logging.getLogger(self.filename).setLevel(logging.DEBUG)

    def setup_logger(self, name, level=logging.DEBUG):
        if self.logger:
            self.logger.handlers[0].close()
            self.logger.handlers = []

        handler = logging.FileHandler(self.logname, mode='w')
        handler.setFormatter(self.formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def run_sugiyama(self):
        initialize_output_directory(self.file_directory)
        self.logger = self.setup_logger(self.filename)
        self.logger.debug('run_sugiyama')
        start_time = time.time()
        self.remove_loops()
        node_order = self.greedy_cycle_removal()
        reverted_edges = self.revert_edges(node_order)
        self.longest_path()
        block_list = self.add_dummy_vertices_create_blocklist()
        block_list = self.initialize_block_position(block_list)
        block_list = self.global_sifting(block_list)
        self.brandes_koepf(block_list)
        end_time = time.time()
        self.logger.info('Duration Sugiyama: ' + str(end_time - start_time) + 's')
        start_time = time.time()
        self.draw_graph(reverted_edges=reverted_edges)
        end_time = time.time()
        self.logger.info('Duration Drawing: ' + str(end_time - start_time) + 's')

    def update_node_x_from_blocklist(self, block_list: []):
        self.logger.debug('update_node_x_from_blocklist')

        for node in self.graph.nodes:
            node_name = node
            if "dummy" in node:
                node_name = "_".join(node_name.split("_")[1:])
            self.graph.add_node(node, x=block_list.index(self.block_lookup[node_name]))

    def get_block_id_from_block(self, given_block: [str]):
        returned_id = None
        for block_id, block in self.block_lookup.items():
            if len(block) == len(given_block):
                result = all(map(lambda x, y: x == y, block, given_block))
                if result:
                    returned_id = block_id
                    break

        if returned_id is None:
            raise Exception('Block ID not found.')

        return returned_id

    def initialize_block_position(self, block_list: []):
        random.shuffle(block_list)

        for block_id, block in self.block_lookup.items():
            self.pi[block_id] = self.get_position_of_block(block_list, block)

        return block_list

    def add_dummy_vertices_create_blocklist(self):
        self.logger.debug('add_dummy_vertices_create_blocklist')

        edges_to_add = []
        edges_to_remove = []

        edges = copy.deepcopy(self.graph.edges)

        block_list = []

        for node in self.graph.nodes:
            block_list.append([node])
            self.block_lookup[node] = [node]

        for edge in edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge

            y_attributes = nx.get_node_attributes(self.graph, 'y')
            child_position_attributes = nx.get_node_attributes(self.graph, 'child_position')
            difference = y_attributes[edge_to] - y_attributes[edge_from]
            if difference != 1:
                self.graph.remove_edge(edge_from, edge_to)
                edges_to_remove.append((edge_from, edge_to))
                node_counter = 1
                current_node = edge_from
                current_block = []
                block_identifier = "dummy" + "_" + edge_from + "_" + edge_to
                while difference > 1:
                    new_node_name = str(node_counter) + "_" + block_identifier
                    if node_counter == 1:
                        try:
                            child_position = child_position_attributes[edge_to]
                        except KeyError:
                            child_position = 0
                    else:
                        child_position = 0
                    self.graph.add_node(new_node_name,
                                        y=y_attributes[edge_from] + node_counter,
                                        name=new_node_name,
                                        child_position=child_position)
                    current_block.append(new_node_name)
                    edges_to_add.append((current_node, new_node_name))
                    self.graph.add_edge(current_node, new_node_name, weight=1)
                    current_node = new_node_name
                    difference -= 1
                    node_counter += 1
                    y_attributes = nx.get_node_attributes(self.graph, 'y')
                    child_position_attributes = nx.get_node_attributes(self.graph, 'child_position')
                self.graph.add_edge(current_node, edge_to, weight=1)
                block_list.append(current_block)
                self.block_lookup[block_identifier] = current_block

        return block_list

    def global_sifting(self, block_list: [], sifting_rounds: int = 2):
        self.logger.debug('global_sifting')

        block_counter = sifting_rounds * len(block_list)
        counter = 0

        for p in range(sifting_rounds):
            self.logger.info('Sifting Round: ' + str((counter // len(block_list)) + 1))
            block_list_copy = copy.deepcopy(block_list)
            for block in block_list_copy:
                block_string = "[" + ",".join(block) + "]"
                self.logger.info(
                    "Iterating block " + str(counter) + " from " + str(block_counter) + ", " + block_string)
                block_list = self.sifting_step(block_list, block)
                counter += 1

        self.update_node_x_from_blocklist(block_list)

        return block_list

    def sort_adjacencies(self, block_list: []):
        self.logger.debug('sort_adjacencies')

        p = {}

        self.n_minus = {}
        self.i_minus = {}
        self.n_plus = {}
        self.i_plus = {}

        for block_id, block in self.block_lookup.items():
            self.n_minus[block_id] = list()
            self.n_plus[block_id] = list()
            self.i_minus[block_id] = list()
            self.i_plus[block_id] = list()
            self.pi[block_id] = self.get_position_of_block(block_list, block)

        for block in block_list:
            upper = self.upper(block)
            lower = self.lower(block)
            block_position = self.pi[self.get_block_id_from_block(block)]

            for edge in self.graph.edges:
                try:
                    edge_from, edge_to = edge
                except ValueError:
                    edge_from, edge_to, weight = edge
                if edge_to == upper:
                    edge_from_block_id = self.get_block_id_from_block(self.get_block_to_node(edge_from, block_list))
                    edge_to_block_id = self.get_block_id_from_block(self.get_block_to_node(edge_to, block_list))
                    j = len(self.n_plus[edge_from_block_id])

                    self.n_plus[edge_from_block_id].insert(j, edge_to)

                    node_block_position = self.pi[edge_from_block_id]
                    if block_position < node_block_position:
                        p[edge] = j
                    else:
                        self.i_plus[edge_from_block_id].insert(j, p[edge])
                        self.i_minus[edge_to_block_id].insert(p[edge], j)

            for edge in self.graph.edges:
                try:
                    edge_from, edge_to = edge
                except ValueError:
                    edge_from, edge_to, weight = edge
                if edge_from == lower:
                    edge_from_block_id = self.get_block_id_from_block(self.get_block_to_node(edge_from, block_list))
                    edge_to_block_id = self.get_block_id_from_block(self.get_block_to_node(edge_to, block_list))
                    j = len(self.n_minus[edge_to_block_id])

                    self.n_minus[edge_to_block_id].insert(j, edge_from)

                    node_block_position = self.pi[edge_to_block_id]
                    if block_position < node_block_position:
                        p[edge] = j
                    else:
                        self.i_minus[edge_to_block_id].insert(j, p[edge])
                        self.i_plus[edge_from_block_id].insert(p[edge], j)

    @staticmethod
    def get_position_of_block(block_list: [], block: [str]):
        for index in range(len(block_list)):
            if len(block_list[index]) == len(block):
                result = all(map(lambda x, y: x == y, block_list[index], block))
                if result:
                    return index

        raise Exception("Position For Block Not Found.")

    @staticmethod
    def get_block_to_node(node: str, block_list: [str]):
        for block in block_list:
            if node in block:
                return block

        raise Exception('Block To Node Not Found')

    @staticmethod
    def upper(block: [str]):
        if "dummy" in block[0]:
            return "1_" + block[0][2:]
        else:
            return block[0]

    @staticmethod
    def lower(block: [str]):
        if "dummy" in block[0]:
            return str(len(block)) + "_" + block[0][2:]
        else:
            return block[0]

    def sifting_step(self, block_list: [], block: [str]):
        self.logger.debug('sifting_step')

        # New ordering of B' with A put to front
        block_list_copy = copy.deepcopy(block_list)
        block_list_copy.remove(block)
        block_list_copy.insert(0, block)
        self.pi[self.get_block_id_from_block(block)] = 0

        # Sort-Adjacencies
        self.sort_adjacencies(block_list_copy)

        # Current And Best Number Of Crossing
        crossings = 0
        crossings_star = 0

        # Best Block Position
        pos_star = 0

        for pos in range(1, len(block_list_copy) - 1):
            block_list_copy, crossings_new = self.sifting_swap(self.get_block_id_from_block(block),
                                                               self.get_block_id_from_block(block_list_copy[pos]),
                                                               block_list_copy)
            crossings += crossings_new
            if crossings < crossings_star:
                crossings_star = crossings
                pos_star = pos

        block_list_copy.remove(block)
        block_list_copy.insert(pos_star + 1, block)

        return block_list_copy

    def get_levels_of_block(self, block_key: str):
        # self.logger.debug('get_levels_of_block')
        levels = []
        y_attributes = nx.get_node_attributes(self.graph, 'y')
        for block in self.block_lookup[block_key]:
            levels.append(y_attributes[block])

        return levels

    def sifting_swap(self, block_key_a: str, block_key_b: str, block_list: []):
        self.logger.debug('sifting_swap')

        l_list = []
        delta = 0
        y_attributes = nx.get_node_attributes(self.graph, 'y')

        y_up_a = y_attributes[self.upper(self.block_lookup[block_key_a])]
        y_low_a = y_attributes[self.lower(self.block_lookup[block_key_a])]
        y_up_b = y_attributes[self.upper(self.block_lookup[block_key_b])]
        y_low_b = y_attributes[self.lower(self.block_lookup[block_key_b])]

        level_a = self.get_levels_of_block(block_key_a)
        level_b = self.get_levels_of_block(block_key_b)

        if y_up_a in level_b:
            l_list.append((y_up_a, '-'))
        if y_low_a in level_b:
            l_list.append((y_low_a, '+'))
        if y_up_b in level_a:
            l_list.append((y_up_b, '-'))
        if y_low_b in level_a:
            l_list.append((y_low_b, '+'))

        for (l, d) in l_list:
            a_node = None
            for block in self.block_lookup[block_key_a]:
                if y_attributes[block] == l:
                    a_node = block
            b_node = None
            for block in self.block_lookup[block_key_b]:
                if y_attributes[block] == l:
                    b_node = block

            if a_node is None or b_node is None:
                raise Exception('Node with that level not found.')

            if d == '+':
                delta += self.uswap(self.n_plus[block_key_a], self.n_plus[block_key_b], block_list)
                self.update_adjacencies(a_node, b_node, d, block_list)
            if d == '-':
                delta += self.uswap(self.n_minus[block_key_a], self.n_minus[block_key_b], block_list)
                self.update_adjacencies(a_node, b_node, d, block_list)

        pos_a = self.get_position_of_block(block_list, self.block_lookup[block_key_a])
        pos_b = self.get_position_of_block(block_list, self.block_lookup[block_key_b])

        if pos_a < pos_b:
            elem_a = block_list.pop(pos_a)
            elem_b = block_list.pop(pos_b - 1)
        else:
            elem_a = block_list.pop(pos_b)
            elem_b = block_list.pop(pos_a - 1)

        block_list.insert(pos_a, elem_b)
        block_list.insert(pos_b, elem_a)

        self.pi[block_key_a] += 1
        self.pi[block_key_b] -= 1

        return block_list, delta

    def uswap(self, n_d_a: [str], n_d_b: [str], block_list: [str]):
        self.logger.debug('uswap')

        r = len(n_d_a)
        s = len(n_d_b)
        c = 0
        i = 0
        j = 0
        while i < r and j < s:
            pos_a = self.pi[self.get_block_id_from_block(self.get_block_to_node(n_d_a[i], block_list))]
            pos_b = self.pi[self.get_block_id_from_block(self.get_block_to_node(n_d_b[j], block_list))]
            if pos_a < pos_b:
                c += (s - j)
                i += 1
            elif pos_a > pos_b:
                c -= (r - i)
                j += 1
            else:
                c += (s - j) - (r - i)
                i += 1
                j += 1

        return c

    def update_adjacencies(self, a_node: str, b_node: str, d, block_list: [str]):
        self.logger.debug('update_adjacencies')

        a_block = self.get_block_to_node(a_node, block_list)
        b_block = self.get_block_to_node(b_node, block_list)
        a_block_id = self.get_block_id_from_block(a_block)
        b_block_id = self.get_block_id_from_block(b_block)

        if d == '+':
            r = len(self.n_plus[a_block_id])
            s = len(self.n_plus[b_block_id])
            i = 0
            j = 0

            while i < r and j < s:
                x_i = self.get_block_id_from_block(self.get_block_to_node(self.n_plus[a_block_id][i], block_list))
                y_i = self.get_block_id_from_block(self.get_block_to_node(self.n_plus[b_block_id][j], block_list))
                pos_a = self.pi[x_i]
                pos_b = self.pi[y_i]
                if pos_a < pos_b:
                    i += 1
                elif pos_a > pos_b:
                    j += 1
                else:
                    z = x_i

                    if x_i != y_i:
                        raise Exception('Z not equal to Y')

                    pos_a_z = self.n_minus[z].index(self.lower(a_block))
                    pos_b_z = self.n_minus[z].index(self.lower(b_block))

                    if pos_a_z < pos_b_z:
                        self.n_minus[z].pop(pos_a_z)
                        self.n_minus[z].pop(pos_b_z - 1)
                        elem_a = self.i_minus[z].pop(pos_a_z)
                        elem_b = self.i_minus[z].pop(pos_b_z - 1)
                    else:
                        self.n_minus[z].pop(pos_b_z)
                        self.n_minus[z].pop(pos_a_z - 1)
                        elem_a = self.i_minus[z].pop(pos_b_z)
                        elem_b = self.i_minus[z].pop(pos_a_z - 1)

                    self.n_minus[z].insert(pos_a_z, self.lower(b_block))
                    self.n_minus[z].insert(pos_b_z, self.lower(a_block))

                    self.i_minus[z].insert(pos_a_z, elem_b)
                    self.i_minus[z].insert(pos_b_z, elem_a)

                    self.i_plus[a_block_id][i] += 1
                    self.i_plus[b_block_id][j] -= 1

                    i += 1
                    j += 1

        else:
            r = len(self.n_minus[a_block_id])
            s = len(self.n_minus[b_block_id])
            i = 0
            j = 0

            while i < r and j < s:
                x_i = self.get_block_id_from_block(self.get_block_to_node(self.n_minus[a_block_id][i], block_list))
                y_i = self.get_block_id_from_block(self.get_block_to_node(self.n_minus[b_block_id][j], block_list))
                pos_a = self.pi[x_i]
                pos_b = self.pi[y_i]
                if pos_a < pos_b:
                    i += 1
                elif pos_a > pos_b:
                    j += 1
                else:
                    z = x_i

                    if x_i != y_i:
                        raise Exception('Z not equal to Y')

                    pos_a_z = self.n_plus[z].index(self.upper(a_block))
                    pos_b_z = self.n_plus[z].index(self.upper(b_block))

                    if pos_a_z < pos_b_z:
                        self.n_plus[z].pop(pos_a_z)
                        self.n_plus[z].pop(pos_b_z - 1)
                        elem_a = self.i_plus[z].pop(pos_a_z)
                        elem_b = self.i_plus[z].pop(pos_b_z - 1)
                    else:
                        self.n_plus[z].pop(pos_b_z)
                        self.n_plus[z].pop(pos_a_z - 1)
                        elem_a = self.i_plus[z].pop(pos_b_z)
                        elem_b = self.i_plus[z].pop(pos_a_z - 1)

                    self.n_plus[z].insert(pos_a_z, self.upper(b_block))
                    self.n_plus[z].insert(pos_b_z, self.upper(a_block))

                    self.i_plus[z].insert(pos_a_z, elem_b)
                    self.i_plus[z].insert(pos_b_z, elem_a)

                    self.i_minus[a_block_id][i] += 1
                    self.i_minus[b_block_id][j] -= 1

                    i += 1
                    j += 1

    def remove_loops(self):
        self.logger.debug('remove_loops')

        edges_to_remove = []

        for edge in self.graph.edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            if edge_from == edge_to:
                edges_to_remove.append(edge_from)

        for edge in edges_to_remove:
            self.graph.remove_edge(edge, edge)

    def revert_edges(self, node_order: [str]):
        self.logger.debug('revert_edges')
        reverting_edges = []
        reverted_edges = []
        weight = 1

        for edge in self.graph.edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            if node_order.index(edge_from) < node_order.index(edge_to):
                reverting_edges.append(edge)

        for edge in reverting_edges:
            try:
                edge_from, edge_to, weight = edge
            except ValueError:
                edge_from, edge_to = edge
            self.graph.remove_edge(edge_from, edge_to)
            self.graph.add_edge(edge_to, edge_from, weight=weight)
            reverted_edges.append((edge_to, edge_from))

        return reverted_edges

    def greedy_cycle_removal(self):
        self.logger.debug('greedy_cycle_removal')

        copy_graph = copy.deepcopy(self.graph)
        s_1 = []
        s_2 = []
        while len(copy_graph.nodes) != 0:
            sink_counter, sinks = self.get_sinks(copy_graph)
            while sink_counter != 0:
                sink = sinks.pop(0)
                sink_counter -= 1
                s_2.insert(0, sink)
                copy_graph.remove_node(sink)
                sink_counter, sinks = self.get_sinks(copy_graph)

            root_counter, roots = self.get_roots(copy_graph)
            while root_counter != 0:
                root = roots.pop(0)
                root_counter -= 1
                s_1.append(root)
                copy_graph.remove_node(root)
                root_counter, roots = self.get_roots(copy_graph)

            if len(copy_graph.nodes) != 0:
                max_node, max_difference = self.get_max_degree_difference_node(copy_graph)
                s_1.append(max_node)
                copy_graph.remove_node(max_node)

        return s_1 + s_2

    def get_level_dic(self):
        self.logger.debug('get_level_dic')

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        level_dic = {}
        for node in y_attributes.keys():
            level = y_attributes[node]
            if level in level_dic:
                level_dic[level].append(node)
            else:
                level_dic[level] = [node]

        return level_dic

    def longest_path(self):
        self.logger.debug('longest_path')

        node_amount = len(self.graph.nodes)
        sink_counter, sinks = self.get_sinks(self.graph)
        for sink in sinks:
            self.graph.add_node(sink, y=node_amount)

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        non_y_attributes = [node for node in self.graph.nodes if node not in y_attributes.keys()]
        while len(non_y_attributes) != 0:
            for node in non_y_attributes:
                adjacent_successors = list(self.graph.successors(node))
                if all(elem in y_attributes.keys() for elem in adjacent_successors):
                    min_y = node_amount
                    for suc in adjacent_successors:
                        if y_attributes[suc] < min_y:
                            min_y = y_attributes[suc]
                    y_attributes[node] = min_y - 1
                    non_y_attributes = [node for node in self.graph.nodes if node not in y_attributes.keys()]
                    break
        nx.set_node_attributes(self.graph, y_attributes, "y")

    def get_max_degree_difference_node(self, graph: nx.Graph):
        self.logger.debug('get_max_degree_difference_node')

        max_difference = -1
        max_node = None
        for node in graph.nodes:
            max_in = graph.in_degree(node)
            max_out = graph.out_degree(node)
            difference = abs(max_in - max_out)
            if difference > max_difference:
                max_difference = difference
                max_node = node

        return max_node, max_difference

    def get_sinks(self, graph: nx.DiGraph):
        self.logger.debug('get_sinks')
        sinks = []
        for node in graph.nodes:
            if graph.out_degree(node) == 0:
                sinks.append(node)

        return len(sinks), sinks

    def get_roots(self, graph: nx.Graph):
        self.logger.debug('get_roots')
        roots = []
        for node in graph.nodes:
            if graph.in_degree(node) == 0:
                roots.append(node)

        return len(roots), roots

    def draw_graph(self, reverted_edges: [], scale_x=200, scale_y=30, labels=False, show_graph=False):
        """
        Draws the current graph from top to bottom. The image is then shown and
        also saved in the output directory with the specified filename.
        The scale parameters define the size of the image.
        :param reverted_edges: [], edges which have been reverted in the graph
        :param labels: bool, print labels if True
        :param scale_x: int
        :param scale_y: int
        :param show_graph: bool, if matplotlib should directly show the graph
        :return: None
        """
        self.logger.debug('draw_graph')

        pos_dict = {}

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        x_attributes = nx.get_node_attributes(self.graph, 'x')
        for node in self.graph.nodes:
            pos_dict[node] = (x_attributes[node] * 10, y_attributes[node] * 5)

        node_color = []
        for node in self.graph.nodes:
            if "dummy" in node:
                node_color.append("red")
            else:
                node_color.append("blue")

        edge_color = []
        for edge in self.graph.edges:
            if edge in reverted_edges:
                edge_color.append("green")
            else:
                edge_color.append("black")

        plt.figure(1, figsize=(scale_x, scale_y))
        nx.draw(self.graph, pos=pos_dict, node_color=node_color, edge_color=edge_color, with_labels=labels)
        plt.gca().invert_yaxis()
        plt.savefig(self.filename, format='png')
        print("Figure saved in", self.filepath)
        if show_graph:
            plt.show()
        plt.clf()

    def has_cycle(self):
        self.logger.debug('has_cycle')

        reachability = {}
        for node in self.graph.nodes:
            reachable_nodes = []
            active_nodes = []
            active_nodes += list(self.graph.successors(node))
            while active_nodes:
                current_node = active_nodes[0]
                if current_node not in reachable_nodes:
                    reachable_nodes.append(current_node)
                    active_nodes += list(self.graph.successors(current_node))

                del active_nodes[0]

            reachability[node] = reachable_nodes

        has_cycle = False
        cycle_amount = 0
        for key, value in reachability.items():
            if key in value:
                cycle_amount += 1
                print(Color.YELLOW, "CYCLE: ", key, ": ", value, Color.END)
                has_cycle = True

        print(Color.RED, "Cycles: ", cycle_amount, Color.END)

        return has_cycle

    ### Brandes & Köpf ###

    def brandes_koepf(self, blocklist: [str]):
        self.logger.debug('brandes_koepf')

        self.bk_horizontal_coordinate_assignment(blocklist)

    def bk_preprocessing(self, blocklist: []) -> None:
        self.logger.debug('bk_preprocessing')

        levels = self.get_level_dic()
        level_keys = sorted(levels.keys())

        x_sorted = self.__get_sorted_levels(levels)

        # Ignore Root and Sink Level
        for level in range(1, len(levels) - 1):
            k_0 = 0
            l = 1
            for l_1 in range(0, len(x_sorted[level_keys[level + 1]])):
                v_l1_i1 = x_sorted[level_keys[level + 1]][l_1]
                block_id = self.get_block_id_from_block(self.get_block_to_node(v_l1_i1, blocklist))
                incident_to_inner_segment = False
                for node in self.n_minus[block_id]:
                    if "dummy" in node:
                        incident_to_inner_segment = True
                if l_1 == len(x_sorted[level_keys[level]]) or incident_to_inner_segment:
                    k_1 = len(x_sorted[level_keys[level]])
                    if incident_to_inner_segment:
                        # Can only be one as we are in a block
                        upper_neighbor = self.n_minus[block_id][0]
                        k_1 = x_sorted[level_keys[level]].index(upper_neighbor)
                    while l <= l_1:
                        predecessors = self.__get_upper(v_l1_i1, blocklist)
                        for neighbor in predecessors:
                            k = x_sorted[level_keys[level]].index(neighbor)
                            if k < k_0 or k > k_1:
                                self.mark_segments.append((neighbor, v_l1_i1))
                        l += 1
                    k_0 = k_1

    def bk_vertical_alignment(self, blocklist: [str], vertical_direction: str, horizontal_direction: str) -> None:
        # root self.upper von Knoten
        # align ist der nächst folgende Knoten im Block, wobei nach self.lower wieder self.upper kommt
        # Brandes & Köpf bezeichen upper (N-) und lower (N+) als die Knoten in der oben bwz. unten liegenden Ebene, gleich zu N+ und N-
        self.logger.debug('bk_vertical_alignment')

        self.__initialice_align()
        self.__initialice_root()

        levels = self.get_level_dic()
        level_keys = sorted(levels.keys())

        x_sorted = self.__get_sorted_levels(levels)

        if vertical_direction == 'up':
            level_range = range(0, len(levels) - 1)
        else:
            level_range = range(len(levels) - 1, 0, -1)

        for i in level_range:
            r = 0

            if horizontal_direction == 'right':
                node_range = range(len(x_sorted[level_keys[i]]) - 1)
            else:
                node_range = range(len(x_sorted[level_keys[i]]) - 1, 0, -1)

            for k in node_range:
                v_k_i = x_sorted[level_keys[i]][k]
                # TODO Reversed successors?
                if vertical_direction == 'up':
                    pre_suc_cessors = self.__get_upper(v_k_i, blocklist)
                else:
                    pre_suc_cessors = self.__get_lower(v_k_i, blocklist)

                d = len(pre_suc_cessors)
                if d > 0:
                    # TODO Probably -1, as to adjust to the list index
                    for m in range(math.floor((d + 1) / 2)-1, math.ceil((d + 1) / 2)-1):
                        if self.align[v_k_i] == v_k_i:
                            u_m = pre_suc_cessors[m]
                            # Cannot go out of bounds, as this is only executed, when there are predecessors
                            if vertical_direction == 'up':
                                pos_u_m = x_sorted[level_keys[i - 1]].index(u_m)
                            else:
                                pos_u_m = x_sorted[level_keys[i + 1]].index(u_m)
                            # TODO Reversed r > pos_u_m ?
                            if vertical_direction == 'up':
                                if (u_m, v_k_i) not in self.mark_segments and r < pos_u_m:
                                    self.align[u_m] = v_k_i
                                    self.root[v_k_i] = self.root[u_m]
                                    self.align[v_k_i] = self.root[v_k_i]
                                    r = pos_u_m
                            else:
                                if (v_k_i, u_m) not in self.mark_segments and r > pos_u_m:
                                    self.align[u_m] = v_k_i
                                    self.root[v_k_i] = self.root[u_m]
                                    self.align[v_k_i] = self.root[v_k_i]
                                    r = pos_u_m

    def bk_horizontal_compaction(self, blocklist: [str], vertical_direction: str, horizontal_direction: str):
        self.logger.debug('bk_horizontal_compaction')

        # TODO reverse Direction -> not necessary?

        self.__initialice_sink()
        self.__initialice_shift()
        self.__initialice_x()

        for node in self.graph.nodes:
            if self.root[node] == node:
                self.__place_block(node, blocklist)

        for node in self.graph.nodes:
            self.x[node] = self.x[self.root[node]]
            if self.shift[self.sink[self.root[node]]] < math.inf:
                self.x[node] += self.shift[self.sink[self.root[node]]]

    def bk_horizontal_coordinate_assignment(self, blocklist: [str]):
        self.logger.debug('bk_horizontal_coordinate_assignment')

        layouts = []

        self.bk_preprocessing(blocklist)
        for vertical_direction in ['up', 'down']:
            for horizontal_direction in ['left', 'right']:
                self.bk_vertical_alignment(blocklist, vertical_direction=vertical_direction,
                                           horizontal_direction=horizontal_direction)
                self.bk_horizontal_compaction(blocklist, vertical_direction=horizontal_direction,
                                              horizontal_direction=horizontal_direction)
                layouts.append(copy.deepcopy(self.x))

        print('test')

        for node in self.graph.nodes:
            pi = 0
            for layout in layouts:
                pi += layout[node]
            pi = pi / len(layouts)
            self.graph.add_node(node, x=pi)

    def __place_block(self, v: str, blocklist: [str]) -> None:
        self.logger.debug('__place_block')

        levels = self.get_level_dic()
        x_sorted = self.__get_sorted_levels(levels)

        v_level = None

        for level, level_nodes in levels.items():
            if v in level_nodes:
                v_level = level

        if v_level is None:
            raise Exception('Level To Node V Not Found')

        if self.x[v] is None:
            self.x[v] = 0
            w = v
            while w != v:
                w_level = None
                for level, level_nodes in levels.items():
                    if w in level_nodes:
                        w_level = level

                if w_level is None:
                    raise Exception('Level To Node W Not Found')

                w_pos = x_sorted[w_level].index(w)
                # TODO Weird Check, as the node always has a position -> Maybe 1
                if w_pos > 0:
                    # TODO Maybe Change to successor for different direction?
                    predecessor = self.n_minus[self.get_block_id_from_block(self.get_block_to_node(w, blocklist))]
                    u = self.root[predecessor]
                    self.__place_block(u, blocklist)
                    if self.sink[v] == v:
                        self.sink[v] = self.sink[u]
                    if self.sink[v] != self.sink[u]:
                        self.shift[self.sink[u]] = min(self.shift[self.sink[u]], self.x[v] - self.x[u] - self.delta)
                    else:
                        self.x[v] = max(self.x[v], self.x[u] + self.delta)
                w = self.align[w]

    def __get_sorted_levels(self, levels: dict) -> dict:
        x_sorted = {}
        for level_val, level_nodes in levels.items():
            x_sorted[level_val] = self.__sort_nodes_by_x_value(level_nodes)

        return x_sorted

    def __initialice_x(self):
        for node in self.graph.nodes:
            self.x[node] = None

    def __initialice_sink(self):
        for node in self.graph.nodes:
            self.sink[node] = node

    def __initialice_shift(self):
        for node in self.graph.nodes:
            self.shift[node] = math.inf

    def __initialice_root(self) -> None:
        for node in self.graph.nodes:
            self.root[node] = node

    def __initialice_align(self) -> None:
        for node in self.graph.nodes:
            self.align[node] = node

    # TODO Not Used Anymore -> Align was wrongly initialized
    def __get_next_align(self, node: str, blocklist: [str]) -> str:
        block = self.get_block_to_node(node, blocklist)
        if "dummy" in node:
            node_number = int(node.split("_")[0])
            node_name = "_".join(node.split("_")[1:])
            successor = str(node_number + 1) + "_" + node_name
            if successor not in block:
                return self.upper(block)
        else:
            return node

    def __get_upper(self, node: str, blocklist: []) -> [str]:
        block_id = self.get_block_id_from_block(self.get_block_to_node(node, blocklist))
        if "dummy" in node and "1_dummy" not in node:
            node_number = int(node.split("_")[0])
            node_name = "_".join(node.split("_")[1:])
            predecessors = [str(node_number - 1) + "_" + node_name]
        else:
            predecessors = self.n_minus[block_id]

        return predecessors

    def __get_lower(self, node: str, blocklist: [str]) -> [str]:
        block = self.get_block_to_node(node, blocklist)
        block_id = self.get_block_id_from_block(block)
        if "dummy" in node and "1_dummy" not in node:
            node_number = int(node.split("_")[0])
            node_name = "_".join(node.split("_")[1:])
            successor = str(node_number + 1) + "_" + node_name
            if successor not in block:
                successors = self.n_plus[block_id]
            else:
                successors = [successor]
        else:
            successors = self.n_plus[block_id]

        return successors

    def __sort_nodes_by_x_value(self, nodes: []):
        x_attributes = nx.get_node_attributes(self.graph, 'x')
        sorted_by_x = []
        for node in nodes:
            position = 0
            x_node = x_attributes[node]
            for pos in range(len(sorted_by_x)):
                if x_node < x_attributes[sorted_by_x[pos]]:
                    position = pos
                    break
            sorted_by_x.insert(position, node)

        return sorted_by_x
