class Tree:

    def __init__(self, value: str = None):
        self.left_siblings = []
        self.right_siblings = []
        self.children = []
        self.value = value

    def get_left_siblings(self):
        return self.left_siblings

    def get_right_siblings(self):
        return self.right_siblings

    def get_siblings(self):
        return self.left_siblings + self.right_siblings

    def get_value(self):
        return self.value

    def set_value(self, value: str):
        self.value = value

    def add_left_sibling(self, sibling, position: int):
        self.left_siblings.insert(position, sibling)

    def add_right_sibling(self, sibling, position: int):
        self.right_siblings.insert(position, sibling)

    def add_child(self, child):
        self.children.append(child)
