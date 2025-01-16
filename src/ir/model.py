from enum import Enum
from typing import Protocol, List, runtime_checkable, Tuple
from abc import abstractmethod
import uuid

class SofaBase: 

    def __init__(self):
        self.id = str(uuid.uuid4())

@runtime_checkable
class Named(Protocol):

    @abstractmethod
    def get_name(self) -> str: ...

    def __repr__(self):
        return self.get_name()

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

class Port(SofaBase, Named):

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class Cardinality:

    def __init__(self, card_str: str = "0..1"):
        self.lowerBound,_ , self.upperBound = card_str.partition("..")

    def to_numeric(self) -> Tuple[int, int]:
        # Need a better name
        return (self._as_int(self.lowerBound), self._as_int(self.upperBound))
    
    def _as_int(self, bound) -> int:
        if bound.strip() == "*":
            return -1
        else:
            return int(bound)

class Attribute(SofaBase, Named):

    def __init__(self, name, value = '', type=None, cardinality: Cardinality = Cardinality()):
        super().__init__()
        self.name = name
        self.value = value
        self.type = type
        self.cardinality = cardinality

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
        if not "attributes" in props: return None
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
                attr_type = i.value.get("type", None)

                ret.append(Attribute(attr_name, attr_value, attr_type, Cardinality(attr_card)))
            else:
                raise AssertionError("Type of attribute must be str|keyvalue")
        return ret

    def list_values(self, prop_name, value_class):
        props = self.struct.properties

        if not prop_name in props: return None
        values = props[prop_name]

        if values is None: return None
        ret = []
        for i in values:
            if isinstance(i, str):
                ret.append(value_class(i))
            else:
                raise AssertionError("Type of value must be str")
        return ret


class ArchElementList():
    def __init__(self, elems):
        self.elems = elems

    def __iter__(self):
        return self.elems.__iter__()
    
    def extend(self, elems: List[ArchElement]):
        self.elems.extend(elems)
    
# -----

class Import: 
    def __init__(self, file_name):
        self.file_name = file_name

class Imports(ArchElementList): 
    def __init__(self, elems=[]):
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
    def __init__(self, elems=[]):
        super().__init__(elems)


class Component(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)
    
    def ports(self):
        return self.list_values("ports", Port)

class Components(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)


class Class(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Classes(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)


class Interface(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Interfaces(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class EndPoint:
    def __init__(self, name, port, cardinality = Cardinality()):
        self.name = name
        self.port = port
        self.cardinality = cardinality

class Relation(ArchElement): 
    def __init__(self, type, source, source_port, target, target_port, struct):
        super().__init__(struct)
        self.type = type
        self.source = EndPoint(source, source_port)
        self.target = EndPoint(target, target_port)

        self._init_props()
    
    def _init_props(self):
        props = self.struct.properties
        source_item = props.get("source", None)
        if source_item:
            self.source.cardinality = Cardinality(source_item.get("cardinality", None))
        target_item = props.get("target", None)
        if target_item:
            self.target.cardinality = Cardinality(target_item.get("cardinality", None))


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
    def __init__(self, elems=[]):
        super().__init__(elems)


class RelationType(Enum):
    INHERITANCE = "inheritance"
    INFORMATION_FLOW = "information_flow"
    REALIZATION = "realization"
    ASSOCIATION = "association"
    BI_ASSOCIATION = "bidirectional_association"
    BI_INFO_FLOW = "bidirectional_inflow"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"

class Stereotype(Named): 

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class Stereotypes(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Primitive(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Primitives(ArchElementList): 
    def __init__(self, elems=[]):
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
    def __init__(self, elems=[]):
        super().__init__(elems)

class Components(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Capability(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Capabilities(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Domains(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Domain(ArchElement):
    def __init__(self, struct):
        super().__init__(struct)

# ----

class Visitor(Protocol):

    @abstractmethod
    def visit_root(self, context, sofa_root): raise NotImplementedError()

    @abstractmethod
    def visit_diagram(self, context, diagram): raise NotImplementedError()

    @abstractmethod
    def visit_stereotype(self, context, stereotype): raise NotImplementedError()

    @abstractmethod
    def visit_primitive(self, context, primitive): raise NotImplementedError()

    @abstractmethod
    def visit_actor(self, context, actor): raise NotImplementedError()

    @abstractmethod
    def visit_component(self, context, component): raise NotImplementedError()

    @abstractmethod
    def visit_relation(self, context, relation): raise NotImplementedError()

    @abstractmethod
    def visit_interface(self, context, interface): raise NotImplementedError()

    @abstractmethod
    def visit_class(self, context, clazz): raise NotImplementedError()

    @abstractmethod
    def visit_domain(self, context, domain): raise NotImplementedError()

    @abstractmethod
    def visit_capability(self, context, capability): raise NotImplementedError()

    @abstractmethod
    def visit_end(self, context, sofa_root): raise NotImplementedError()

# ---- 

class ValidationError(Exception): ...

class Validator:

    def validate(self, sofa_root):
        self.validate_relations(sofa_root)

    def validate_relations(self, sofa_root):
        
        if not sofa_root.relations: return

        # Ensure name and ports are defined when used in relations.
        for rel in sofa_root.relations:
            try:
                source_def = sofa_root.get_by_name(rel.source.name)
            except KeyError:
                raise ValidationError(f"Relation {rel} references obj {rel.source.name}, but is not defined")
            
            if not source_def: 
                raise ValidationError(f"Relation {rel} references obj {rel.source.name}, but is not defined")
            if isinstance(source_def, Component):
                source_port = rel.source.port
                if source_port and (source_def.ports() is None 
                                    or not filter(lambda p: (p.get_name()), source_def.ports())): 
                    raise ValidationError(f"Relation {rel} references source port {source_port}, but is not defined in {source_def}")

            target_def = sofa_root.get_by_name(rel.target.name)
            if not target_def: 
                raise ValidationError(f"Relation {rel} references obj {rel.target.name}, but is not defined")
            if isinstance(target_def, Component):
                target_port = rel.target.port
                if target_port and (target_def.ports() is None
                                    or not filter(lambda p: (p.get_name()), target_def.ports())): 
                    raise ValidationError(f"Relation {rel} references target port {target_port}, but is not defined in {target_def}")


# ----
class SofaRoot:
    def __init__(self):
        self.children = None

        # The following are for convenience
        # All the elements are already in children,
        # but arranged in the manner how Lark parsed
        # TODO: Revisit for a better design
        self.imports = Imports()
        self.diagrams = Diagrams()
        self.stereotypes = Stereotypes()
        self.primitives = Primitives()
        self.actors = Actors()
        self.components = Components()
        self.relations = Relations()
        self.interfaces = Interfaces()
        self.classes = Classes()
        self.domains = Domains()
        self.capabilities = Capabilities()

    def set_children(self, children):
        self.children = children
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
    
    def validate(self):
        Validator().validate(self)

    def visit(self, context, visitor: Visitor):

        visitor.visit_root(context, self)

        if self.diagrams:
            for i in self.diagrams:
                visitor.visit_diagram(context, i)
        
        if self.stereotypes:
            for i in self.stereotypes:
                visitor.visit_stereotype(context, i)

        if self.domains:
            for i in self.domains:
                visitor.visit_domain(context, i)

        if self.capabilities:
            for i in self.capabilities:
                visitor.visit_capability(context, i)
        
        if self.actors:        
            for i in self.actors:
                visitor.visit_actor(context, i)
        
        if self.primitives:
            for i in self.primitives:
                visitor.visit_primitive(context, i)

        if self.interfaces:
            for i in self.interfaces:
                visitor.visit_interface(context, i)
        
        if self.classes:
            for i in self.classes:
                visitor.visit_class(context, i)
        
        if self.components:
            for i in self.components:
                visitor.visit_component(context, i)
        
        if self.relations:
            for i in self.relations:
                visitor.visit_relation(context, i)
        
        # End of the visiting
        visitor.visit_end(context, self)