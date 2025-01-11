from enum import Enum
from typing import Protocol, runtime_checkable
from abc import abstractmethod
import uuid

class SofaBase: 

    def __init__(self):
        self.id = str(uuid.uuid4())

@runtime_checkable
class Named(Protocol):

    @abstractmethod
    def get_name(self) -> str: ...

class KeyValue(Named):
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def get_name(self):
        return self.key

class Struct:
    def __init__(self, name, inheritance=[], properties={}):
        self.name = name
        self.inheritance = inheritance
        self.properties = properties
    
    def set_properties(self, dict):
        self.properties = dict
    
class Literal(SofaBase, Named):

    def __init__(self, name, value = ''):
        self.name = name
        self.value = value

    def get_name(self):
        return self.name

class Attribute(SofaBase, Named):

    def __init__(self, name, value = '', type=None, lowerBound="0", upperBound="1"):
        super().__init__()
        self.name = name
        self.value = value
        self.type = type
        self.lowerBound = lowerBound
        self.upperBound = upperBound

    def get_name(self):
        return self.name

class ArchElement(SofaBase, Named):
    def __init__(self, struct):
        super().__init__()
        self.struct = struct
    
    def get_name(self):
        return self.struct.name

    def literals(self):
        props = self.struct.properties
        return props['literals']

    def attributes(self):
        props = self.struct.properties

        if not "attributes" in props: return None
        attrs = props['attributes']

        if attrs is None: return None
        ret = []
        for i in attrs:
            if isinstance(i, str):
                ret.append(Attribute(i))
            elif isinstance(i, KeyValue):
                attr_name = i.key
                attr_value = i.value.get("value", "")
                attr_card = i.value.get("cardinality", None)
                if attr_card is not None:
                    lower,_ , upper = attr_card.partition("..")
                attr_type = i.value.get("type", None)

                ret.append(Attribute(attr_name, attr_value, attr_type, lower, upper))
            else:
                raise AssertionError("Type of attribute must be str|keyvalue")
        return ret

class ArchElementList():
    def __init__(self, elems):
        self.elems = elems

    def __iter__(self):
        return self.elems.__iter__()
    
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

class Module(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

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
    
    def is_bidirectional(self):
        return (self.type == RelationType.BI_ASSOCIATION 
            or self.type == RelationType.BI_INFO_FLOW)

    def is_association(self):
        return (self.type == RelationType.BI_ASSOCIATION 
            or self.type == RelationType.ASSOCIATION)

    def is_information_flow(self):
        return (self.type == RelationType.INFORMATION_FLOW 
            or self.type == RelationType.BI_INFO_FLOW)

class Relations(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class RelationType(Enum):
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    INFORMATION_FLOW = "information_flow"
    REALIZATION = "realization"
    BI_ASSOCIATION = "bidirectional_association"
    BI_INFO_FLOW = "bidirectional_inflow"

class Stereotype(Named): 

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class Stereotypes(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Primitive(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Primitives(ArchElementList):
    def __init__(self, elems):
        super().__init__(elems)

class Diagram(Named): 

    def __init__(self, diagram: str | KeyValue):
        self.diagram = diagram

    def get_name(self):
        if isinstance(self.diagram, str):
            return self.diagram
        else:
            return self.diagram.key

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

class Domain(ArchElement):
    def __init__(self, struct):
        super().__init__(struct)

# ----

class Visitor(Protocol):

    @abstractmethod
    def visit_root(self, context, sofa_root): raise NotImplementedError

    @abstractmethod
    def visit_diagram(self, context, diagram): raise NotImplementedError

    @abstractmethod
    def visit_stereotype(self, context, stereotype): raise NotImplementedError

    @abstractmethod
    def visit_primitive(self, context, primitive): raise NotImplementedError

    @abstractmethod
    def visit_actor(self, context, actor): raise NotImplementedError

    @abstractmethod
    def visit_component(self, context, component): raise NotImplementedError

    @abstractmethod
    def visit_relation(self, context, relation): raise NotImplementedError

    @abstractmethod
    def visit_interface(self, context, interface): raise NotImplementedError

    @abstractmethod
    def visit_class(self, context, clazz): raise NotImplementedError

    @abstractmethod
    def visit_domain(self, context, domain): raise NotImplementedError

    @abstractmethod
    def visit_capability(self, context, capability): raise NotImplementedError

    @abstractmethod
    def visit_end(self, context, sofa_root): raise NotImplementedError

# ----
class SofaRoot:
    def __init__(self, children):
        self.imports = self._find(children, Imports)
        self.diagrams = self._find(children, Diagrams)
        self.stereotypes = self._find(children, Stereotypes)
        self.primitives = self._find(children, Primitives)
        self.actors = self._find(children, Actors)
        self.components = self._find(children, Components)
        self.relations = self._find(children, Relations)
        self.interfaces = self._find(children, Interfaces)
        self.classes = self._find(children, Classes)
        self.domains = self._find(children, Domains)
        self.capabilities = self._find(children, Capabilities)

        self._index(children)

    def _index(self, children):
        self.index_id = {}
        self.index_name = {}
        for child in children:
            for elem in child.elems:
                if hasattr(elem, 'id'):
                    self.index_id[elem.id] = elem
                if isinstance(elem, Named):
                    self.index_name[elem.get_name()] = elem

    def _find(self, list, elemType):
        for i in list:
            if type(i) == elemType:
                return i
        return None
    
    def get_by_id(self, id):
        return self.index_id[id]

    def get_by_name(self, name):
        return self.index_name[name]

    def visit(self, context, visitor: Visitor):

        visitor.visit_root(context, self)

        for i in self.diagrams:
            visitor.visit_diagram(context, i)
        
        for i in self.stereotypes:
            visitor.visit_stereotype(context, i)
        
        for i in self.primitives:
            visitor.visit_primitive(context, i)
        
        for i in self.actors:
            visitor.visit_actor(context, i)
        
        for i in self.components:
            visitor.visit_component(context, i)
        
        for i in self.relations:
            visitor.visit_relation(context, i)
        
        for i in self.interfaces:
            visitor.visit_interface(context, i)
        
        for i in self.classes:
            visitor.visit_class(context, i)
        
        for i in self.domains:
            visitor.visit_domain(context, i)

        for i in self.capabilities:
            visitor.visit_capability(context, i)

        # End of the visiting
        visitor.visit_end(context, self)