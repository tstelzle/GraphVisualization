class Node:

    def __init__(self, name):
        self.name = name
        self.edges_to = {}
        self.edges_from = {}
        self.mod = 0
        self.thread = None
        self.ancestors = [self]
        self.root = False
        self.prelim = 0
        self.ancestor = None
        self.change = 0
        self.shift = 0
        self.number = 0
        self.x = 0
        self.y = 0

    def get_siblings(self):
        if self.edges_from:
            parent = self.edges_from[0]
            return parent.edges_to

        return {}

    def get_left_sibling(self):
        siblings = self.get_siblings()
        for position, node_name in siblings.items():
            if node_name is self.name:
                if position == 0:
                    return None
                else:
                    return siblings[position - 1]

        return None
