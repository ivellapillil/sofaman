from enum import Enum
from typing import Protocol, List, runtime_checkable, Tuple
from abc import abstractmethod
import uuid

class SofaBase: 

    def __init__(self):
        self.id = str(uuid.uuid4())

class PropertyContainer:

    def __init__(self, props):
        self.props = props
        self._stereotype_refs = None
        self.visibility = Visibility(props.get("visibility", Visibility.PRIVATE.value))

    def description(self):
        props = self.props
        if not "description" in props: return None
        return props['description']
    
    def stereotypes(self):
        if self._stereotype_refs:
            return self._stereotype_refs
        
        props = self.props
        if not "stereotypes" in props: return None
        stereos = props['stereotypes']
        self._stereotype_refs = list(map(lambda st: StereotypeReference(st), stereos))

        return self._stereotype_refs

@runtime_checkable
class Named(Protocol):

    @abstractmethod
    def get_name(self) -> str: ...

    def get_qname(self) -> str:
        return self.get_name()

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
        self.name = name.strip() # TODO: Workaround. Need to strip spaces in the parser itself.
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
        elif bound:
            return int(bound)
        return -1

class Visibility(Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    PROTECTED = "protected"

class Attribute(SofaBase, Named, PropertyContainer):

    def __init__(self, name, props):
        SofaBase.__init__(self)
        PropertyContainer.__init__(self, props)
        self.name = name
        self.value = props.get("value", "")
        self.cardinality = Cardinality(props.get("cardinality", None))
        self.type = props.get("type", None)

    def get_name(self):
        return self.name

class ParameterDirection(Enum):
    IN = "in"
    OUT = "out"
    INOUT = "inout"
    RETURN = "return"

class Parameter(SofaBase, Named, PropertyContainer):

    def __init__(self, name, props):
        SofaBase.__init__(self)
        PropertyContainer.__init__(self, props)
        self.name = name
        self.type = props.get("type", None)
        self.direction = ParameterDirection(props.get("direction", ParameterDirection.IN.value))

    def get_name(self):
        return self.name

class Operation(SofaBase, Named, PropertyContainer):

    def __init__(self, name, props):
        SofaBase.__init__(self)
        PropertyContainer.__init__(self, props)
        self.name = name
        self.parameters = self._extract_parameters(props)

    def _extract_parameters(self, props):
        op_parameters = props.get("parameters", None)
        op_params_ret = []
        if op_parameters:
            if isinstance(op_parameters, list):
                op_params_ret.extend(map(lambda param_name: Parameter(param_name, {}), op_parameters))
            else: 
                for param_name in op_parameters:
                    param_dict = op_parameters[param_name]
                    op_params_ret.append(Parameter(param_name, param_dict))
        return op_params_ret

    def get_name(self):
        return self.name

class ArchElement(SofaBase, Named, PropertyContainer):
    def __init__(self, struct):
        SofaBase.__init__(self)
        PropertyContainer.__init__(self, struct.properties)
        self.struct = struct
        self.parent_package = None
    
    def get_name(self):
        return self.struct.name

    def get_qname(self):
        # If there is no parent, return original name
        names = [self.get_name()]
        parent_pkg = self.parent_package
        while parent_pkg:
            names.append(parent_pkg.get_name())
            parent_pkg = parent_pkg.parent_package
        return ".".join(reversed(names))

    def literals(self):
        props = self.struct.properties
        if not "literals" in props: return None
        return props['literals']
    
    def package(self):
        props = self.struct.properties
        if not "package" in props: return None
        return props['package']

    def attributes(self):
        props = self.struct.properties

        if not "attributes" in props: return None
        attrs = props['attributes']

        if attrs is None: return None
        ret = []
        for attr_name in attrs:
            attr_props = attrs[attr_name]
            ret.append(Attribute(attr_name, attr_props))
        return ret

    def operations(self):
        props = self.struct.properties

        if not "operations" in props: return None
        ops = props['operations']

        if ops is None: return None
        ret = []
        for op_name in ops:
            op_props = ops[op_name]
            ret.append(Operation(op_name, op_props))
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
    
    def append(self, elem: ArchElement):
        self.elems.append(elem)
    
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
    def __init__(self, name, port, cardinality = None):
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

class StereotypeReference(Named): 

    def __init__(self, qname):
        profile, _, name = qname.partition(".")
        if name == "":
            self.name = profile
            self.profile = "default"
        else:
            self.profile = profile
            self.name = name

    def get_name(self):
        return self.name

class StereoTypeProfile(SofaBase, Named):

    def __init__(self, name, stereotypes: List[str]):
        super().__init__()
        self.name = name
        self.stereotypes = stereotypes
    
    def get_name(self):
        return self.name

class StereotypeProfiles(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Primitive(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)

class Primitives(ArchElementList): 
    def __init__(self, elems=[]):
        super().__init__(elems)

class Package(ArchElement): 
    def __init__(self, struct):
        super().__init__(struct)
    
    def get_given_name(self):
        return self.struct.name

    def get_name(self):
        given_name = self.get_given_name()
        return given_name.split(".")[-1]

class Packages(ArchElementList): 
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
    def visit_package(self, context, package): raise NotImplementedError()

    @abstractmethod
    def visit_stereotype_profile(self, context, stereotype_profile): raise NotImplementedError()

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
        self.index_id = {}
        self.index_name = {}

        # The following are for convenience
        # All the elements are already in children,
        # but arranged in the manner how Lark parsed
        # TODO: Revisit for a better design
        self.imports = Imports()
        self.packages = Packages()
        self.diagrams = Diagrams()
        self.stereotype_profiles = StereotypeProfiles()
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
        self._elaborate()
        self._index()
        self._link()

    def append_child(self, child, group_type):
        group = self._find_group(group_type)
        group.elems.append(child)
        self._index_child(child)

    def _index_child(self, child):
        if hasattr(child, 'id'):
            self.index_id[child.id] = child
        if isinstance(child, Named):
            self.index_name[child.get_qname()] = child

    def _elaborate(self):
        self._create_intermediate_packages()

    def _link(self): 
        # Now link parent packages to all elems
        self._link_packages()

    def _link_packages(self):
        for elem in self.model_elements():
            pkg_name = elem.package()
            if pkg_name:
                parent_pkg = self.get_by_qname(pkg_name)
                if not parent_pkg:
                    raise AssertionError(f"Package {pkg_name} referred by {elem.get_name()} not found. Did you use qualified name?")
                elem.parent_package = parent_pkg

    def _create_intermediate_packages(self):
        pkg_name_map = {}
        for pkg in self.packages:
            pkg_name_map[pkg.get_given_name()] = pkg
            # Sort it so that even if the package defs are 
            # out of order, it works
        sorted_pkgs = dict(sorted(pkg_name_map.items()))

        for pkg_qname_str, pkg in sorted_pkgs.items():
            pkg_qnames = pkg_qname_str.split(".")
            parent_pkg = None
            for index, pkg_name in enumerate(pkg_qnames):
                corres_pkg = sorted_pkgs.get(".".join(pkg_qnames[0:index+1]), None)
                if not corres_pkg:
                    # Missing package. Create and add parent
                    corres_pkg = Package(Struct(pkg_name))
                    # Add to the package list
                    self.packages.append(corres_pkg)
                corres_pkg.parent_package = parent_pkg
                parent_pkg = corres_pkg

    # TODO: Need a better name
    def model_elements(self):
        for child in self.children:
            for elem in child.elems:
                yield elem

    def _index(self):
        for elem in self.model_elements():
            self._index_child(elem)

    def _find_group(self, group_type):
        for i in self.children:
            if type(i) == group_type:
                return i
        return None
    
    def get_by_id(self, id):
        return self.index_id[id]

    def get_by_qname(self, qname):
        return self.index_name.get(qname, None)
        
    def validate(self):
        Validator().validate(self)

    def visit(self, context, visitor: Visitor):

        visitor.visit_root(context, self)

        if self.diagrams:
            for i in self.diagrams:
                visitor.visit_diagram(context, i)
        
        if self.packages:
            for i in self.packages:
                visitor.visit_package(context, i)
        
        if self.stereotype_profiles:
            for i in self.stereotype_profiles:
                visitor.visit_stereotype_profile(context, i)

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