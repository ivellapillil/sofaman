"""
This module defines the intermediate representation (IR) of the sofa model. 
The IR is used to represent the parsed sofa model in a structured way, which is then used by the generator 
to generate the final output in the desired format (e.g., PlantUML, XMI).
"""
from enum import Enum
from pathlib import Path
from typing import Protocol, List, runtime_checkable, Tuple
from abc import abstractmethod
import uuid

class IrContext:
    """
    Context used while building the IR. It keeps track of the imported files and
    ensures that cyclic imports are avoided.
    """

    def __init__(self, ir, root_file = None):
        self.imports = []
        self.import_context = []
        self.ir = ir
        if root_file:
            resolved_file_name = self.resolve_file(root_file)
            self.imports.append(resolved_file_name)
            self.import_context.append(resolved_file_name)
    
    def start_import(self, file_name):
        """
        Start of importing a file.
        """
        self.imports.append(file_name)
        # Import context to track import nesting
        self.import_context.append(file_name)
    
    def exists_import(self, file_name):
        """
        Checks if the given file name is already imported in the context.
        """
        return file_name in self.imports

    def end_import(self):
        """
        The end of importing a file.
        """
        # Import is finished we can remove it from the context
        self.import_context.pop()
    
    def resolve_file(self, file_name) -> str:
        """
        Resolves the given file name to a valid path.
        """
        path = Path(file_name)
        if path.is_absolute():
            return str(path.resolve())
        
        # Relative path. We resolve it relative to parent file
        if len(self.import_context) > 0:
            parent_file = self.import_context[-1]
            parent_path = Path(parent_file)
            return str(parent_path.parent.joinpath(path).resolve())
        
        return str(Path(file_name).resolve())


    def build(self, file_name):
        """
        Builds the IR from the given file name.
        """
        resolved_file_name = self.resolve_file(file_name)
        if not self.exists_import(resolved_file_name):
            with open(resolved_file_name) as f:
                content = f.read()
                self.start_import(resolved_file_name)
                sofa_root = self.ir.build(self, content)
                self.end_import()
                return sofa_root

class SofaBase: 
    """
    Base class for all the elements in the sofa model.
    """

    def __init__(self):
        self.id = str(uuid.uuid4())

class PropertyContainer:
    """
    Base class for all the elements in the sofa model that can have properties.
    """

    def __init__(self, props):
        self.props = props
        self._stereotype_refs = None
        self._diags = None
        self.visibility = Visibility(props.get("visibility", Visibility.PRIVATE.value))

    def description(self):
        """
        Returns the description of the element.
        """
        props = self.props
        if not "description" in props: return None
        return props['description']
    
    def stereotypes(self):
        """
        Returns the stereotypes of the element.
        """
        if self._stereotype_refs:
            return self._stereotype_refs
        
        props = self.props
        if not "stereotypes" in props: return None
        stereos = props['stereotypes']
        self._stereotype_refs = list(map(lambda st: StereotypeReference(st), stereos))

        return self._stereotype_refs

    def diagrams(self):
        """
        Returns in which all diagrams the element is present.
        """
        if self._diags:
            return self._diags
        
        props = self.props
        if not "diagrams" in props: return None
        diags = props['diagrams']
        self._diags = list(map(lambda st: Diagram(st), diags))

        return self._diags

@runtime_checkable
class Named(Protocol):
    """
    Protocol for elements that have a name.
    """

    @abstractmethod
    def get_name(self) -> str: 
        """
        Returns the name of the element.
        """
        ...

    def get_qname(self) -> str:
        """
        Returns the fully qualified name of the element.
        """
        return self.get_name()

    def __repr__(self):
        return self.get_name()

class KeyValue(Named):
    """
    Represents a key-value pair.
    """
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def get_name(self):
        return self.key

class Struct:
    """
    Represents a structure with properties.
    """
    def __init__(self, name, inheritance=[], properties={}):
        self.name = name.strip() # TODO: Workaround. Need to strip spaces in the parser itself.
        self.inheritance = inheritance
        self.properties = properties
    
    def set_properties(self, dict):
        """
        Set the properties of the structure.
        """
        self.properties = dict
    
class Literal(SofaBase, Named):
    """
    Represents a literal element. In XMI it is represented as a literal, while in PlantUML it is represented as as class.
    """

    def __init__(self, name, value = ''):
        self.name = name
        self.value = value

    def get_name(self):
        return self.name

class Port(SofaBase, Named):
    """
    Represents a port of a component.
    """

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class Cardinality:
    """
    Represents the cardinality of an attribute or a relation.
    """

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
    """
    Represents the visibility of an element.
    """
    PRIVATE = "private"
    PUBLIC = "public"
    PROTECTED = "protected"

class Attribute(SofaBase, Named, PropertyContainer):
    """
    Represents an attribute of a class, a component, interface etc.
    """

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
    """
    Represents the direction of a parameter of an operation (whether it is passed as input or returned as value).
    """
    IN = "in"
    OUT = "out"
    INOUT = "inout"
    RETURN = "return"

class Parameter(SofaBase, Named, PropertyContainer):
    """
    Represents a parameter of an operation.
    """

    def __init__(self, name, props):
        SofaBase.__init__(self)
        PropertyContainer.__init__(self, props)
        self.name = name
        self.type = props.get("type", None)
        self.direction = ParameterDirection(props.get("direction", ParameterDirection.IN.value))

    def get_name(self):
        return self.name

class Operation(SofaBase, Named, PropertyContainer):
    """
    Represents an operation of a class, a component, interface etc.
    """

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
    """
    Common base class for all the architectural elements like class, component, interface, relation, etc.
    """

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
        """
        Returns the literals delcared by the element.
        """
        props = self.struct.properties
        if not "literals" in props: return None
        return props['literals']
    
    def package(self):
        """
        Returns which package the element belongs to.
        """
        props = self.struct.properties
        if not "package" in props: return None
        return props['package']

    def attributes(self):
        """
        Returns the attributes of the element.
        """
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
        """
        Returns the operations of the element.
        """
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
        """
        A convenience method to get a list of values of a property.
        """
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
    """
    Represents a list of architectural elements.
    """
    def __init__(self, elems):
        self.elems = elems

    def __iter__(self):
        return self.elems.__iter__()

    def __getitem__(self, key):
        return self.elems[key]
    
    def extend(self, elems: List[ArchElement]):
        """
        Extends the list of elements with the given list.
        """
        self.elems.extend(elems)
    
    def append(self, elem: ArchElement):
        """
        Appends an element to the list.
        """
        self.elems.append(elem)
    
# -----

class Import: 
    """
    Represents an import statement.
    """
    def __init__(self, file_name):
        self.file_name = file_name
    
    def resolve(self, context: IrContext, sofa_root):
        """
        Resolves the import and returns SofaRoot.
        """
        sub_sofa_root = context.build(self.file_name)
        if sub_sofa_root:
            sofa_root.merge(sub_sofa_root)

class Imports(ArchElementList): 
    """
    Represents a list of import statements.
    """
    def __init__(self, elems):
        super().__init__(elems)

class ImportStyle(Import): 
    """
    Represents an import statement that imports a style sheet.
    """
    def __init__(self, file_name):
        super().__init__(file_name)

class Module(ArchElement): 
    """
    Represents a module.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Actor(ArchElement): 
    """
    Represents an actor.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Actors(ArchElementList): 
    """
    Represents a list of actors.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Component(ArchElement): 
    """
    Represents a component.
    """
    def __init__(self, struct):
        super().__init__(struct)
    
    def ports(self):
        """
        Returns the declared ports of the component
        """
        return self.list_values("ports", Port)

class Components(ArchElementList): 
    """
    Represents a list of components.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Class(ArchElement): 
    """
    Represents a class.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Classes(ArchElementList): 
    """
    Represents a list of classes.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Interface(ArchElement): 
    """
    Represents an interface.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Interfaces(ArchElementList): 
    """
    Represents a list of interfaces.
    """
    def __init__(self, elems):
        super().__init__(elems)

class EndPoint:
    """
    Represents an end point of a relation.
    """
    def __init__(self, name, port, cardinality = None):
        self.name = name
        self.port = port
        self.cardinality = cardinality

class Relation(ArchElement): 
    """
    Represents a relation between two elements.
    """
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
        """
        Returns whether the relation is bidirectional.
        """
        return (self.type == RelationType.BI_ASSOCIATION 
            or self.type == RelationType.BI_INFO_FLOW)

    def is_association(self):
        """
        Returns whether the relation is an association.
        """
        return (self.type == RelationType.BI_ASSOCIATION 
            or self.type == RelationType.ASSOCIATION)

    def is_information_flow(self):
        """
        Returns whether the relation is an information flow
        """
        return (self.type == RelationType.INFORMATION_FLOW 
            or self.type == RelationType.BI_INFO_FLOW)

class Relations(ArchElementList): 
    """
    Represents a list of relations.
    """
    def __init__(self, elems):
        super().__init__(elems)


class RelationType(Enum):
    """
    Represents the type of a relation.
    """
    INHERITANCE = "inheritance"
    INFORMATION_FLOW = "information_flow"
    REALIZATION = "realization"
    ASSOCIATION = "association"
    BI_ASSOCIATION = "bidirectional_association"
    BI_INFO_FLOW = "bidirectional_inflow"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"

class StereotypeReference(Named): 
    """
    Represents a reference to a stereotype.
    """

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
    """
    Represents the profile of a stereotype.
    """

    def __init__(self, name, stereotypes: List[str]):
        super().__init__()
        self.name = name
        self.stereotypes = stereotypes
    
    def get_name(self):
        return self.name

class StereotypeProfiles(ArchElementList): 
    """
    Represents a list of stereotype profiles.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Primitive(ArchElement): 
    """
    Represents a primitive type.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Primitives(ArchElementList): 
    """
    Represents a list of primitive types.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Package(ArchElement): 
    """
    Represents a package.
    """
    def __init__(self, struct):
        super().__init__(struct)
    
    def get_given_name(self):
        """
        Returns the given name of the package, which may be a qualified name.
        """
        return self.struct.name

    def get_name(self):
        """
        Returns the name of the package without the parent package names.
        """
        given_name = self.get_given_name()
        return given_name.split(".")[-1]

class Packages(ArchElementList): 
    """
    Represents a list of packages.
    """
    def __init__(self, elems):
        super().__init__(elems)

class DiagramType(Enum):
    """
    Represents the type of a diagram.
    """
    # Currently only one is supported
    COMPONENT = "component"

class Diagram(Named): 
    """
    Represents a diagram.
    """

    def __init__(self, diagram: str | KeyValue):
        self.diagram = diagram

    def get_name(self):
        if isinstance(self.diagram, str):
            return self.diagram
        else:
            return self.diagram.key
    
    def get_type(self):
        """
        Returns the type of the diagram.
        """
        if isinstance(self.diagram, str):
            return DiagramType.COMPONENT # Default
        else:
            return DiagramType(self.diagram.value.get("type", DiagramType.COMPONENT))

class Diagrams(ArchElementList): 
    """
    Represents a list of diagrams.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Components(ArchElementList): 
    """
    Represents a list of components.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Capability(ArchElement): 
    """
    Represents a business or techical capability.
    """
    def __init__(self, struct):
        super().__init__(struct)

class Capabilities(ArchElementList): 
    """
    Represents a list of capabilities.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Domains(ArchElementList): 
    """
    Represents a list of domains.
    """
    def __init__(self, elems):
        super().__init__(elems)

class Domain(ArchElement):
    """
    Represents a business or technical domain.
    """

    def __init__(self, struct):
        super().__init__(struct)

    def capabilities(self):
        """
        Returns the capabilities of the domain.
        """
        return self.list_values("capabilities", str) # TODO: May be CapabilityReference instead of str.

# ----

class Visitor(Protocol):

    @abstractmethod
    def visit_root(self, context, sofa_root): 
        """
        Visit the root of the sofa model.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_diagram(self, context, diagram): 
        """
        Visit the diagram.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_package(self, context, package): 
        """
        Visit the package.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_stereotype_profile(self, context, stereotype_profile): 
        """
        Visit the stereotype profile. This is distinct from stereotype reference.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_primitive(self, context, primitive): 
        """
        Visit primitive types.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_actor(self, context, actor): 
        """
        Visit actor.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_component(self, context, component): 
        """
        Visit component.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_relation(self, context, relation): 
        """
        Visit relation.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_interface(self, context, interface): 
        """
        Visit interface.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_class(self, context, clazz): 
        """
        Visit class.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_domain(self, context, domain): 
        """
        Visit domain.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_capability(self, context, capability): 
        """
        Visit capability.
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_end(self, context, sofa_root): 
        """
        End of the visiting. Typically results in saving of the 
        generated file or other cleanup activities.
        """
        raise NotImplementedError()

# ---- 

class ValidationError(Exception): 
    """
    Represents a validation error.
    """
    ...

class Validator:
    """
    Validates that the sofa model is semantically correct and complete.
    """

    def validate(self, sofa_root):
        """
        Validates the sofa model.
        """
        self._validate_relations(sofa_root)

    def _validate_relations(self, sofa_root):
        """
        Validates the relations in the sofa model.
        """
        
        if not sofa_root.relations: return

        # Ensure name and ports are defined when used in relations.
        for rel in sofa_root.relations:
            try:
                source_def = sofa_root.get_by_qname(rel.source.name)
            except KeyError:
                raise ValidationError(f"Relation {rel} references obj {rel.source.name}, but is not defined")
            
            if not source_def: 
                raise ValidationError(f"Relation {rel} references obj {rel.source.name}, but is not defined")
            if isinstance(source_def, Component):
                source_port = rel.source.port
                if source_port and (source_def.ports() is None 
                                    or not filter(lambda p: (p.get_name()), source_def.ports())): 
                    raise ValidationError(f"Relation {rel} references source port {source_port}, but is not defined in {source_def}")

            target_def = sofa_root.get_by_qname(rel.target.name)
            if not target_def: 
                raise ValidationError(f"Relation {rel} references obj {rel.target.name}, but is not defined")
            if isinstance(target_def, Component):
                target_port = rel.target.port
                if target_port and (target_def.ports() is None
                                    or not filter(lambda p: (p.get_name()), target_def.ports())): 
                    raise ValidationError(f"Relation {rel} references target port {target_port}, but is not defined in {target_def}")


# ----
class SofaRoot:
    """
    Represents the root of the sofa model. Contains all the elements and provide some convenience methods.
    """
    def __init__(self):
        self.children = []
        self.index_id = {}
        self.index_name = {}

        # The following are for convenience
        # All the elements are already in children,
        # but arranged in the manner how Lark parsed
        # TODO: Revisit for a better design
        self.imports = Imports([])
        self.packages = Packages([])
        self.diagrams = Diagrams([])
        self.stereotype_profiles = StereotypeProfiles([])
        self.primitives = Primitives([])
        self.actors = Actors([])
        self.components = Components([])
        self.relations = Relations([])
        self.interfaces = Interfaces([])
        self.classes = Classes([])
        self.domains = Domains([])
        self.capabilities = Capabilities([])

    def add_children(self, children):
        """
        Sets the children.
        """
        self.children.extend(children)
        self._elaborate()
        self._index()
        self._link()

    def append_child(self, child, group_type):
        """
        Appends a child to the group. Triggers re-indexing.
        """
        group = self._find_group(group_type)
        group.elems.append(child)
        self._index_child(child)
    
    def merge(self, other):
        """
        Merges the other sofa root into this one.
        """
        if not isinstance(other, SofaRoot):
            raise AssertionError("Only SofaRoot types can be merged")

        # TODO: It is a bit of a mess to having to 
        # duplicate the children in another list. Revisit.
        self.imports.extend(other.imports)
        self.packages.extend(other.packages)
        self.diagrams.extend(other.diagrams)
        self.stereotype_profiles.extend(other.stereotype_profiles)
        self.primitives.extend(other.primitives)
        self.actors.extend(other.actors)
        self.components.extend(other.components)
        self.relations.extend(other.relations)
        self.interfaces.extend(other.interfaces)
        self.classes.extend(other.classes)
        self.domains.extend(other.domains)
        self.capabilities.extend(other.capabilities)

        self.add_children(other.children)

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
            if not isinstance(elem, ArchElement): continue
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
        """
        Returns all the model elements.
        """
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
        """
        Returns the element by id.
        """
        return self.index_id[id]

    def get_by_qname(self, qname):
        """
        Returns the element by fully qualified name.
        """
        return self.index_name.get(qname, None)
        
    def validate(self):
        """
        Validates the model.
        """
        Validator().validate(self)

    def visit(self, context, visitor: Visitor):
        """
        Visits all the elements in the model.
        """

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