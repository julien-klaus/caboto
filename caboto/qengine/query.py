from string import ascii_lowercase, ascii_uppercase

import networkx as nx

from .qgraph import LogicNode, QGraph

alpha = list(ascii_lowercase) + list((ascii_uppercase))
number = list(range(9))

class Query:
    def __init__(self, query, graph):
        self.parser = Parser(query)
        self.graph = graph # Kubernetes Graph

    def execute(self):
        if self.parser.query_type == "nodes":
            nodes = []
            context = {self.parser.identifier: None}
            for node, _ in self.graph.nodes.items():
                # set context 
                context[self.parser.identifier] = node
                if self.parser.property_graph.execute(self.graph, context):
                    nodes.append(node)
                # reset context
                context = {self.parser.identifier: None}
            return nodes
        elif self.parser.query_type == "edges":
            edges = []
            context = {(self.parser.identifier[0], self.parser.identifier[1]): None}
            for (source, target), _ in self.graph.edges.items():
                # set context
                context[(self.parser.identifier[0], self.parser.identifier[1])] = (source, target)
                context[self.parser.identifier[0]] = source
                context[self.parser.identifier[1]] = target
                if self.parser.property_graph.execute(self.graph, context):
                    edges.append((source, target))    
                # reset context
                context = {self.parser.identifier[0]: None, self.parser.identifier[1]: None}
            return edges
        else:
            raise Exception("Currently we can only get nodes or edges.")
    

KEYWORDS = ["get", "where", "nodes", "edges", "and", "or", "type", "label", "name"]
SYMBOLS = {
    ".": "dot",
    "(": "lbracket",
    ")": "rbracket",
    ",": "comma",
    "=": "equal"
}


class Property:
    def __init__(self):
        self.ident = None
        self.property = None
        self.target = None

    def get_children(self):
        return []

    def execute(self, graph, context):
        # check if there is a an ident
        # breakpoint()
        if self.ident and self.ident in context:
            attributes = nx.get_node_attributes(graph, self.property)
            if context[self.ident] in attributes and attributes[context[self.ident]] == self.target:
                # breakpoint()
                return True, context
        else:
            # check if the ident is in some tuple
            for key in context:
                if isinstance(key, tuple):
                    (source, target) = key
                    if self.ident == source:
                        breakpoint()
                        attributes = nx.get_edge_attributes(graph, self.property)
                        # check if there is a successor
                        for target in graph.successors(source):
                            if attributes[(source, target)] == self.target:
                                return True, contex
                    elif self.ident == target:
                        breakpoint()
                        attributes = nx.get_edge_attributes(graph, self.property)
                        # check if there is a predecessor
                        for source in graph.predecessors(target):
                            if attributes[(source, target)] == self.target:
                                return True, context
                        pass
        return False, context

    def __str__(self):
        if not self.target:
            return ""
        property = f"{self.ident}." if self.ident else ""
        property += f"{self.property}={self.target}"
        return property

    def __repr__(self):
        return str(self)


class Parser:
    """
    Parser for network queries.

    query = "GET" _variable "WITH" _property_or
    _variable = "nodes" identifier | "edges" [ "(" identifier "," identifier")" ]
    _property_or = _property_and [ "OR" propertiyAnd ]
    _property_and = _property [ "AND" _property ]
    _property = ( { identifier "." ( "type" | "label" | "name" ) "=" identifier ) | "(" _property_or ")"
    identifier = _alpha_ { _alpha_ | _number_}
    """
    def __init__(self, query):
        self.query = query
        self.scanner = Scanner(query)
        self.query_type = None
        self.identifier = None
        self.symbol = None
        self.description = None
        self.property_graph = None
        self._get_symbol()
        self._query()
        self.property_graph.draw()

    def _get_symbol(self):
        self.symbol, self.description = self.scanner.get_symbol()

    def _description_equal(self, description):
        return self.description == description

    def _symbol_equal(self, symbol):
        return self.symbol == symbol

    def _query(self):
        """ query = "GET" _variable "WITH" _property_or """
        if self._description_equal("keyword") and self._symbol_equal("get"):
            self._get_symbol()
            self._variable()
            if self._description_equal("keyword") and self._symbol_equal("where"):
                self._get_symbol()
                self.property_graph = QGraph(self._property_or())
            else:
                raise Exception("Please define properties using 'WITH'.")
        else:
            raise Exception("Queries should start with 'GET'.")

    def _variable(self):
        """ _variable = "nodes" identifier | "edges" "(" identifier "," identifier")" """
        if self._description_equal("keyword") and self._symbol_equal("nodes"):
            self.query_type = "nodes"
            self._get_symbol()
            if self._description_equal("identifier"):
                self.identifier = self.symbol
                self._get_symbol()
            else:
                raise Exception("Please define an identifier for the nodes.")
        elif self._description_equal("keyword") and self._symbol_equal("edges"):
            self.query_type = "edges"
            self._get_symbol()
            if self._description_equal("lbracket"):
                self._get_symbol()
                if self._description_equal("identifier"):
                    self.identifier = self.symbol
                    self._get_symbol()
                    if self._description_equal("comma"):
                        self._get_symbol()
                        if self._description_equal("identifier"):
                            self.identifier = (self.identifier, self.symbol)
                            self._get_symbol()
                            if self._description_equal("rbracket"):
                                self._get_symbol()
                            else:
                                raise Exception("Closing bracket expected.")
                        else:
                            raise Exception("Identifier for target expected.")
                    else:
                        raise Exception("Comma expected.")
                else:
                    raise Exception("Identifier for source expected.")
            else:
                raise Exception("Please define an identifier for the edges.")

    def _property_or(self):
        """ _property_or = _property_and [ "OR" propertiyAnd """
        node = self._property_and() 
        while self._symbol_equal("or"):
            self._get_symbol()
            tmp = LogicNode("or")
            tmp.add_child(node)
            tmp.add_child(self._property_or())
            node = tmp
        return node

    def _property_and(self):
        """ _property_and = _property [ "AND" _property ] """
        node = self._property()
        while self._symbol_equal("and"):
            self._get_symbol()
            tmp = LogicNode("and")
            tmp.add_child(node)
            tmp.add_child(self._property_or())
            node = tmp
        return node

    def _property(self):
        """ _property = ( { identifier "." ( "type" | "label" | "name" ) "=" identifier ) | "(" _property_or ")" """
        property = Property()
        if self._description_equal("lbracket"):
            self._get_symbol()
            
        if self._description_equal("identifier"):
            #TODO: check for tuple identifier
            property.ident = self.symbol
            self._get_symbol()
            if self._description_equal("dot"):
                self._get_symbol()
        else:
            raise Exception("Each property needs an identifier.")
        if self._description_equal("keyword"):
            if self.symbol in ['type', 'label', 'name']:
                property.property = self.symbol
                self._get_symbol()
                if self._description_equal("equal"):
                    self._get_symbol()
                    if self._description_equal("identifier"):
                        property.target = self.symbol
                        self._get_symbol()
                    else:
                        raise Exception(f"Not allowed symbol '{self.symbol}'. Identifier for property excepted.")
                else:
                    raise Exception("Equal sign expected.")
            else:
                raise Exception("Type, label or name expected")
        return property


class Scanner:
    """
    Split the query into token.
    """
    def __init__(self, query):
        self.query = query
        self.input = Input(query)
        self.next()

    def next(self):
        self.sym = self.input.next()

    def get_symbol(self):
        # skip blanks
        while self.sym == " ":
            self.next()
        symbol = ""
        description = ""
        # look for keywords and identifier
        if self.sym in alpha:
            while self.sym in alpha + number:
                symbol += self.sym
                self.next()
            if str(symbol).lower() in KEYWORDS:
                description = "keyword"
                symbol = symbol.lower()
            else:
                description = "identifier"
        # look for symbols
        elif self.sym in SYMBOLS.keys():
            symbol = self.sym
            description = SYMBOLS[self.sym]
            self.next()
        elif self.sym == "":
            description = "None"
        else:
            raise Exception(f"Character '{self.sym}' not allowed.")
        return (symbol, description)


class Input:
    """
    Split the query into characters.
    """
    def __init__(self, query: str):
        self.query = list(query)
        self.n = len(self.query)
        self.index = -1

    def next(self) -> str:
        self.index += 1
        if self.index < self.n:
            return self.query[self.index]
        else:
            return ""


if __name__ == "__main__":
    query = "GET nodes WHERE type=Pod and type=Service"
    s = Parser(query)
    print(s.properties)
    s.property_graph.draw()




