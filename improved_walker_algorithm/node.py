class Node:

    def __init__(self, name):
        self.name = name
        self.edges_to = {}
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
        self.y = 0

    def get_siblings(self):
        if self.parent:
            return self.parent.edges_to

        return {}

    def get_left_sibling(self):
        siblings = self.get_siblings()
        for position, node_name in siblings.items():
            if position == 0:
                if node_name is self.name:
                    return None
                else:
                    return siblings[position]

        return None
