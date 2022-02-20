from string import ascii_lowercase, ascii_uppercase

"""
nodes = []
for node, labels in source_graph.nodes.items():
    if 'type' in labels:
        if labels['type'] == "Pod":
            nodes.append(node)
"""

"""
edges = []
for (source, target), labels in source_graph.edges.items():
    if "label" in labels:
        if labels["label"] == "hosts":
            edges.append((source, target))
"""

"""
IngressToContainerImage wäre eigentlich so eine query.
Das wäre dann irgendwie so:
1) hole alle Knoten vom Typ "Container"
2) filtere die die eine Verbindung (label=selects) zu einen Knoten vom Typ "Service" haben
3) filtere alle Knoten vom Typ "Service" die eine Verbindung (label=serves) zu Knoten vom Typ "Ingress" haben
4) map die route (z.B. /* für alles, oder /admin/* nur für diesen URL präfix) auf die verbleibenden Container
das ist halt eine komplexe traversierung mit einer reihe an bedingungen
das ergebnis wäre dann
[(Ingress <admin.mysite.com/admin/*>, Container <myfancy-admin>), ... ]
"""

""" Gib mir alle Knoten vom Typ "Pod", welche mit dem Knoten <NAME> vom Typ "Service" über eine Beziehung mit Label "selects" verbunden sind """


# GET nodes WHERE type=Pod
# GET nodes WHERE type=ConfigMap
# GET nodes WHERE type=Service
# GET nodes WHERE type=Ingress
# GET nodes WHERE type=Application
# GET edges WHERE label=hosts
# GET paths WITH START type=Service AND data.name=<name> END type=Pod
# GET paths WITH START label:serves and type=Pod

# GET nodes n WHERE n.type=Container AND n - selects -> m.type=Service AND m.type=Service - servers -> l.type=Ingress



alpha = list(ascii_lowercase) + list((ascii_uppercase))
number = list(range(9))

class Query:
    def __init__(self, query, graph):
        self.parser = Parser(query)
        self.graph = graph

    def execute(self):
        if self.parser.query_type == "nodes":
            nodes = []
            for node, labels in self.graph.nodes.items():
                if self.parser.properties.property in labels:
                    if labels[self.parser.properties.property] == self.parser.properties.target:
                        nodes.append(node)
            return nodes

        elif self.parser.query_type == "edges":
            pass
            #TODO: see aboce
        else:
            raise Exception("Currently we can only get nodes or edges.")


KEYWORDS = ["get", "where", "nodes", "edges", "and", "or", "type"]
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

    def __str__(self):
        if not self.target:
            return ""
        property = f"{self.ident}." if self.ident else ""
        property += f"{self.property}={self.target}"
        return property


class Parser:
    """
    Parser for network queries.

    query = "GET" _variable "WITH" _property_or
    _variable = "nodes" [ identifier ] | "edges" [ "(" identifier "," identifier")" ]
    _property_or = _property_and [ "OR" propertiyAnd ]
    _property_and = _property [ "AND" _property ]
    _property = ( { [ identifier "." ] ( "type" | "label" | "name" ) "=" identifier ) | "(" _property_or ")"
    identifier = _alpha_ { _alpha_ | _number_}
    """
    def __init__(self, query):
        self.query = query
        self.scanner = Scanner(query)
        self.query_type = None
        self.identifier = None
        self.properties = None
        self.symbol = None
        self.description = None
        self._get_symbol()
        self._query()

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
                self._property_or()
            else:
                raise Exception("Please define properties using 'WITH'.")
        else:
            raise Exception("Queries should start with 'GET'.")

    def _variable(self):
        """ _variable = "nodes" [ identifier ] | "edges" [ "(" identifier "," identifier")" ] """
        if self._description_equal("keyword") and self._symbol_equal("nodes"):
            self.query_type = "nodes"
            self._get_symbol()
            if self._description_equal("identifier"):
                self.identifier = self.symbol
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

    def _property_or(self):
        """ _property_or = _property_and [ "OR" propertiyAnd """
        self._property_and()
        # TODO

    def _property_and(self):
        """ _property_and = _property [ "AND" _property ] """
        self._property()
        # TODO

    def _property(self):
        """ _property = ( { [ identifier "." ] ( "type" | "label" | "name" ) "=" identifier ) | "(" _property_or ")" """
        property = Property()
        if self._description_equal("identifier"):
            property.ident = self.symbol
            self._get_symbol()
            if self._description_equal("dot"):
                self._get_symbol()
        if self._description_equal("keyword"):
            if self.symbol in ['type', 'label', 'name']:
                property.property = self.symbol
                self._get_symbol()
                if self._description_equal("equal"):
                    self._get_symbol()
                    if self._description_equal("identifier"):
                        property.target = self.symbol
                    else:
                        raise Exception("Identifier for _property excepted.")
                else:
                    raise Exception("Equal sign expected.")
            else:
                raise Exception("Type, label or name expected")
        self.properties = property


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
    query = "GET nodes WHERE type=Pod"
    s = Parser(query)
    print(s.properties)


