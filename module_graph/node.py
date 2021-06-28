class Node:

    def __init__(self, name):
        self.name = name
        self.edges_to = {}
        self.edges_from = {}
        self.parent = None
        self.mod = 0
        self.thread = None
        self.root = False
        self.prelim = 0
        self.ancestor = self
        self.change = 0
        self.shift = 0
        self.number = 0
        self.x = -1
        self.y = -1

    def get_x_or_y(self, position):
        """
        Returns the coordinate from the node, specified by the position
        :param position: str, x or y
        :return: int
        """
        if position == 'x':
            return self.x
        elif position == 'y':
            return self.y

    def get_siblings(self):
        """
        Returns the dictionary of all siblings from the current node.
        :return: dict
        """
        if self.parent:
            return self.parent.edges_to

        return {}

    def get_left_most_sibling(self):
        """
        Returns the left most sibling of the current node. If the left most is the node self None is returned.
        :return: ?Node
        """
        if self.parent:
            left_most_node = self.parent.edges_to[min(self.parent.edges_to.keys())]
            if left_most_node is not self:
                return left_most_node

        return None

    def get_right_most_sibling(self):
        if self.parent:
            right_most_node = self.parent.edges_to[max(self.parent.edges_to.keys())]
            if right_most_node is not self:
                return right_most_node

        return None

    def get_position(self):
        if self.parent:
            for position, node in self.parent.edges_to.items():
                if node is self:
                    return position
        return -1

    def update_position(self, number: int):
        start = number + 1
        last_key = max(self.edges_to.keys())
        for child_counter in range(start, last_key):
            try:
                self.edges_to[number] = self.edges_to[child_counter]
            except KeyError:
                child_counter += 1

    def get_left_sibling(self):
        """
        Returns the left sibling of the node. If the node has no left sibling None is returned
        :return: ?Node
        """
        node_position = self.get_position()
        if node_position == 0 or node_position == -1:
            return None
        position_keys = sorted(self.get_siblings().keys())
        position_to_look_for = position_keys[position_keys.index(node_position)-1]

        return self.get_siblings()[position_to_look_for]

    def get_right_sibling(self):
        node_position = self.get_position()
        position_keys = sorted(self.get_siblings().keys())
        position_to_look_for = position_keys[position_keys.index(node_position)+1]
        if position_to_look_for > max(position_keys):
            return None
        else:
            return self.get_siblings()[position_to_look_for]

    def get_child_at_key_position(self, current_position: int):
        position = sorted(self.edges_to.keys())[current_position]
        return self.edges_to[position]

    def get_last_child(self):
        maximum = max(self.edges_to.keys())
        return self.edges_to[maximum]

    def get_first_child(self):
        minimum = min(self.edges_to.keys())
        return self.edges_to[minimum]

    def neighbours_have_y(self, maximum_value):
        minimum = maximum_value
        for position, node in self.edges_to.items():
            if node is None:
                return False, -1
            elif node.y == -1:
                return False, -1
            else:
                if node.y < minimum:
                    minimum = node.y
        return True, minimum
