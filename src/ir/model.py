from enum import Enum

class SofaBase: ...

class KeyValue(SofaBase):
    def __init__(self, key, value):
        self.key = key
        self.value = value

class Struct:
    def __init__(self, name, parents, properties):
        self.name = name
        self.parents = parents
        self.properties = properties
    
    def set_properties(self, dict):
        self.properties = dict

class ArchElement(SofaBase):
    def __init__(self, struct):
        self.struct = struct

class ArchElementList():
    def __init__(self, elems):
        self.elems = elems

class SofaRoot:
    def __init__(self, children):
        self.children = children

# -----

class Import: 
    def __init__(self, file_name):
        self.file_name = file_name

class Imports(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class ImportStyle(Import): 
    def __init__(self, file_name):
        super().__init__(file_name)

class Actor(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Actors(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Component(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Components(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Class(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Classes(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Interface(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Interfaces(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Relation(ArchElement): 
    def __init__(self, type, source, target, struct):
        super().__init__(struct)
        self.type = type
        self.source = source
        self.target = target

class Relations(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class RelationType(Enum):
    ASSOCIATION = "association"
    BIDIRECTIONAL = "bidirectional"
    INHERITANCE = "inheritance"
    INFORMATION_FLOW = "information_flow"
    REALIZATION = "realization"

class Stereotype(ArchElement): 
    def __init__(self, stereotype: str):
        self.stereotype = stereotype

class Stereotypes(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Diagram(ArchElement): 
    def __init__(self, diagram: str | KeyValue):
        self.diagram = diagram

class Diagrams(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Components(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Capability(ArchElement): 

    def __init__(self, struct):
        super().__init__(struct)

class Capabilities(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Domains(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Domain(ArchElement): ...
