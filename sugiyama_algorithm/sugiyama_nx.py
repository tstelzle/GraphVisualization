import copy
import os
import random
import logging

import matplotlib.pyplot as plt
import networkx as nx

from module_color import *


class SugiyamaNX:

    def __init__(self, filename: str, graph: nx.DiGraph):
        self.filename = os.path.join("output", "Sugiyama", filename + ".png")
        self.sifting_logname = os.path.join("output", "Sugiyama", filename + "_sifting_step.log")
        self.method_logname = os.path.join("output", "Sugiyama", filename + "_method.log")
        self.filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.filename)
        self.graph = graph
        # block_id -> block
        self.block_lookup = {}
        # block_id -> nodes
        self.n_minus = {}
        self.n_plus = {}
        self.i_minus = {}
        self.i_plus = {}
        self.pi = {}
        # logging.basicConfig(filename=self.logname, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.sifting_step_logger = self.setup_logger('sifting_step_logger', self.sifting_logname)
        self.method_logger = self.setup_logger('method_logger', self.method_logname)

    def setup_logger(self, name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def run_sugiyama(self):
        self.method_logger.info('run_sugiyama')
        self.remove_loops()
        node_order = self.greedy_cycle_removal()
        reverted_edges = self.revert_edges(node_order)
        print(reverted_edges)
        self.longest_path()
        block_list = self.add_dummy_vertices_create_blocklist()
        block_list = self.initialize_block_position(block_list)
        self.global_sifting(block_list)
        # self.assign_prelim_x()
        self.draw_graph(reverted_edges=reverted_edges)

    def update_node_x_from_blocklist(self, block_list: []):
        self.method_logger.info('update_node_x_from_blocklist')
        for node in self.graph.nodes:
            node_name = node
            if "dummy" in node:
                node_name = "_".join(node_name.split("_")[1:])
            self.graph.add_node(node, x=block_list.index(self.block_lookup[node_name]))

    def get_block_id_from_block(self, given_block: [str]):
        # self.method_logger.info('get_block_id_from_block')
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
        self.method_logger.info('add_dummy_vertices_create_blocklist')
        edges_to_add = []
        edges_to_remove = []

        # TODO there was an error with 'dictionary changed size during iteration'
        #  -> could not find it
        #  -> this is the solution
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
                        child_position = child_position_attributes[edge_to]
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

    def global_sifting(self, block_list: [], sifting_rounds: int = 1):
        self.method_logger.info('global_sifting')
        # self.initialize_adjancies()

        block_counter = sifting_rounds * len(block_list)
        counter = 0

        for p in range(sifting_rounds):
            self.sifting_step_logger.info('Sifting Round: ' + str((counter // len(block_list)) + 1))
            block_list_copy = copy.deepcopy(block_list)
            for block in block_list_copy:
                block_string = "[" + ",".join(block) + "]"
                self.sifting_step_logger.info("Iterating block " + str(counter) + " from " + str(block_counter) + ", " + block_string)
                block_list = self.sifting_step(block_list, block)
                counter += 1

        self.update_node_x_from_blocklist(block_list)

    def initialize_adjancies(self):
        self.method_logger.info('initialize_adjancies')
        for block_id in self.block_lookup.keys():

            if "dummy" in block_id:
                first_node_of_block = "1_" + block_id
                last_node_of_block = str(len(self.block_lookup[block_id])) + "_" + block_id
            else:
                first_node_of_block = block_id
                last_node_of_block = block_id

            # Keine eingehende Kante in das Segement
            self.n_minus[block_id] = list(self.graph.predecessors(first_node_of_block))

            # Keine ausgehende Kante in das Segement
            self.n_plus[block_id] = list(self.graph.successors(last_node_of_block))

            # Kindposition des Blocks zu der eingehenden Kante
            for n_minus_index in range(len(self.n_minus[block_id])):
                if block_id not in self.i_minus.keys():
                    self.i_minus[block_id] = [
                        list(self.graph.successors(self.n_minus[block_id][n_minus_index])).index(first_node_of_block)]
                else:
                    self.i_minus[block_id].append(
                        list(self.graph.successors(self.n_minus[block_id][n_minus_index])).index(first_node_of_block))

            # Elternposition des Blocks zu der ausgehenden Kante
            for n_plus_index in range(len(self.n_plus[block_id])):
                if block_id not in self.i_plus.keys():
                    self.i_plus[block_id] = [
                        list(self.graph.predecessors(self.n_plus[block_id][n_plus_index])).index(last_node_of_block)]
                else:
                    self.i_plus[block_id].append(
                        list(self.graph.predecessors(self.n_plus[block_id][n_plus_index])).index(last_node_of_block))

    def sort_adjacencies(self, block_list: []):
        self.method_logger.info('sort_adjacencies')

        # TODO p[edge] gives key error -> Initialized with default value 0
        # !!!!!!!!!!!!!!!!!! NOT ANYMORE

        p = {}

        # for edge in self.graph.edges:
        #     p[edge] = 0

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

                    try:
                        index = self.n_plus[edge_from_block_id].index(edge_to)
                        print(index)
                    except ValueError:
                        pass

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

                    try:
                        index = self.n_minus[edge_from_block_id].index(edge_to)
                        print(index)
                    except ValueError:
                        pass

                    self.n_minus[edge_to_block_id].insert(j, edge_from)

                    node_block_position = self.pi[edge_to_block_id]
                    if block_position < node_block_position:
                        p[edge] = j
                    else:
                        self.i_minus[edge_to_block_id].insert(j, p[edge])
                        self.i_plus[edge_from_block_id].insert(p[edge], j)

    def get_position_of_block(self, block_list: [], block: [str]):
        # self.method_logger.info('get_position_of_block')
        for index in range(len(block_list)):
            if len(block_list[index]) == len(block):
                result = all(map(lambda x, y: x == y, block_list[index], block))
                if result:
                    return index

        raise Exception("Position For Block Not Found.")

    def get_block_to_node(self, node: str, block_list: [str]):
        # self.method_logger.info('get_block_to_node')
        for block in block_list:
            if node in block:
                return block

        raise Exception('Block To Node Not Found')

    def upper(self, block: [str]):
        # self.method_logger.info('upper')
        if "dummy" in block[0]:
            return "1_" + block[0][2:]
        else:
            return block[0]

    def lower(self, block: [str]):
        # self.method_logger.info('lower')
        if "dummy" in block[0]:
            return str(len(block)) + "_" + block[0][2:]
        else:
            return block[0]

    def sifting_step(self, block_list: [], block: [str]):
        self.method_logger.info('sifting_step')
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
            block_list_copy, crossings_new = self.sifting_swap(self.get_block_id_from_block(block), self.get_block_id_from_block(block_list_copy[pos]), block_list_copy)
            crossings += crossings_new
            if crossings < crossings_star:
                crossings_star = crossings
                pos_star = pos

        block_list_copy.remove(block)
        block_list_copy.insert(pos_star + 1, block)

        return block_list_copy

    def get_levels_of_block(self, block_key: str):
        # self.method_logger.info('get_levels_of_block')
        levels = []
        y_attributes = nx.get_node_attributes(self.graph, 'y')
        for block in self.block_lookup[block_key]:
            levels.append(y_attributes[block])

        return levels

    def sifting_swap(self, block_key_a: str, block_key_b: str, block_list: []):
        self.method_logger.info('sifting_swap')
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
            elem_b = block_list.pop(pos_b-1)
        else:
            elem_a = block_list.pop(pos_b)
            elem_b = block_list.pop(pos_a-1)

        block_list.insert(pos_a, elem_b)
        block_list.insert(pos_b, elem_a)

        self.pi[block_key_a] += 1
        self.pi[block_key_b] -= 1

        return block_list, delta

    def uswap(self, n_d_a: [str], n_d_b: [str], block_list: [str]):
        self.method_logger.info('uswap')

        r = len(n_d_a)
        s = len(n_d_b)
        c = 0
        i = 0
        j = 0
        while i < r and j < s:
            print('while uswap: i', i, "r:", r, "j:", j, "s:", s)
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
        self.method_logger.info('update_adjacencies')

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
                        self.n_plus[z].pop(pos_b_z-1)
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
        self.method_logger.info('remove_loops')
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
        self.method_logger.info('revert_edges')
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
        self.method_logger.info('greedy_cycle_removal')
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
        self.method_logger.info('get_level_dic')
        y_attributes = nx.get_node_attributes(self.graph, 'y')
        level_dic = {}
        for node in y_attributes.keys():
            level = y_attributes[node]
            if level in level_dic:
                level_dic[level].append(node)
            else:
                level_dic[level] = [node]

        return level_dic

    def assign_prelim_x(self):
        self.method_logger('assign_prelim_x')
        level_dic = self.get_level_dic()
        node_distance = 10
        for level in level_dic.keys():
            node_position = 0
            for node in level_dic[level]:
                self.graph.add_node(node, x=node_position)
                node_position += node_distance

    def longest_path(self):
        self.method_logger.info('longest_path')
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
        self.method_logger.info('get_max_degree_difference_node')
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
        self.method_logger.info('get_sinks')
        sinks = []
        for node in graph.nodes:
            if graph.out_degree(node) == 0:
                sinks.append(node)

        return len(sinks), sinks

    def get_roots(self, graph: nx.Graph):
        self.method_logger.info('get_roots')
        roots = []
        for node in graph.nodes:
            if graph.in_degree(node) == 0:
                roots.append(node)

        return len(roots), roots

    def draw_graph(self, reverted_edges: [], scale_x=70, scale_y=15, labels=False, show_graph=False):
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
        self.method_logger.info('draw_graph')
        pos_dict = {}

        y_attributes = nx.get_node_attributes(self.graph, 'y')
        x_attributes = nx.get_node_attributes(self.graph, 'x')
        for node in self.graph.nodes:
            pos_dict[node] = (x_attributes[node], y_attributes[node])

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
        plt.savefig(self.filename, format='png', dpi=300)
        print("Figure saved in", self.filepath)
        if show_graph:
            plt.show()
        plt.clf()

    def has_cycle(self):
        self.method_logger.info('has_cycle')
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
