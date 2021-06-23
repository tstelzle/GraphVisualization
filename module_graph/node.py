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
            left_most_node = self.parent.edges_to[0]
            if left_most_node is not self:
                return left_most_node

        return None

    def get_position(self):
        if self.parent:
            for position, node in self.parent.edges_to.items():
                if node is self:
                    return position
        return -1

    def update_position(self, number: int):
        start = number + 1
        for child_counter in range(start, len(self.edges_to)):
            self.edges_to[number] = self.edges_to[child_counter]

    def get_left_sibling(self):
        """
        Returns the left sibling of the node. If the node has no left sibling None is returned
        :return: ?Node
        """
        node_position = self.get_position()

        if node_position == 0 or node_position == -1:
            return None

        siblings = self.get_siblings()
        for position, node_name in siblings.items():
            if position == node_position - 1:
                return siblings[position]

        return None

    def neighbours_have_y(self, maximum_value):
        minimum = maximum_value
        for position, node in self.edges_to.items():
            if node.y == -1:
                return False, -1
            else:
                if node.y < minimum:
                    minimum = node.y
        return True, minimum
