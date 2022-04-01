

from enum import Enum

from graphviz import Digraph

class Type(Enum):
    AND = 1
    OR = 2


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
    
    def execute(self, graph, context):
        valid, context = self.root.execute(graph, context)
        return valid

class LogicNode:
    def __init__(self, label):
        self.label = label
        if self.label == "and":
            self.type = Type.AND
        if self.label == "or":
            self.type = Type.OR
        self.children = []

    def execute(self, graph, context):
        valid = True
        change = True
        contex_tmp = context
        while change:
            change = False
            for node in self.children:
                valid_temp, context_tmp = node.execute(graph, context)
                if context_tmp != context:
                    breakpoint()
                    change = True
                context = context_tmp
                if self.label == "and":
                    valid = valid and valid_temp
                else:
                    valid = valid or valid_temp
        return valid, context
    
    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def __str__(self):
        return self.label