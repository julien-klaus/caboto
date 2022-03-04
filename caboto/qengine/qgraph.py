

from enum import Enum

from graphviz import Digraph

class Type(Enum):
    AND = 1
    OR = 2
    PROPERTY = 3


class QGraph:
    def __init__(self, root):
        self.root = root

    def draw(self):
        g = Digraph("Property Graph")
        nodes = [self.root]
        node_to_index = {}
        index = 1
        while nodes:
            node = nodes.pop()
            g.node(str(index), str(node))
            node_to_index[node] = index
            index += 1
            for child in node.get_children():
                nodes.append(child)
        for node in node_to_index.keys():
            for child in node.get_children():
                g.edge(str(node_to_index[node]), str(node_to_index[child]))
        g.render("property_graph.pdf")


class LogicNode:
    def __init__(self, label, left, right):
        self.label = label
        if self.label == "and":
            self.type = Type.AND
        elif self.label == "or":
            self.type = Type.PROPERTY
        else:
            self.type = Type.PROPERTY
        self.left = left
        self.right = right
    
    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.right = right

    def get_children(self):
        return [self.left, self.right]

    def __str__(self):
        return self.label


class PropertyNode:
    def __init__(self, property):
        self.property = property
        self.children = {}

    def get_children(self):
        return self.children.keys()

    def add_child(child, label):
        self.children[child] = label
    
    def __str__(self):
        return str(self.property)







