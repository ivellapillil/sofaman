from sofaman.parser.sofa_parser import SofaParser
from sofaman.ir.model import (SofaRoot, KeyValue, Struct, 
                    Capability, Domain, Interface, Component, 
                    Class, Import, ImportStyle, Diagram, Actor, 
                    Relation, RelationType, Port, Package,
                    StereoTypeProfile, Primitive)
from lark import Tree, Transformer

class SofaStructTransformer(Transformer):
    
    def STRING(self, args):
        return self._as_string(args)
    
    def SIMPLE_STRING(self, args):
        return self._as_string(args)
    
    def NUMBER(self, args):
        return self._as_string(args)

    def QUOTED_STRING(self, args):
        return self._as_string(args)
    
    def CNAME(self, args):
        return self._as_string(args)

    def scalar(self, args):
        return args[0]
    
    def name(self, args):
        return args[0].strip("\"")
    
    def multiline_scalar(self, args):
        return args[0]

    def vector_items(self, args):
        return list(map(lambda s: s.strip(), args)) # TODO: This is not nice. Need to fix it at grammar level!!

    def vector(self, args):
        return self._as_flat_list(args)

    def key_value(self, args):
        return KeyValue(args[0], args[1])

    def vector_value(self, args):
        return KeyValue(args[0], args[1])

    def multiline_value(self, args):
        return KeyValue(args[0], args[1])

    def map(self, args):
        return KeyValue(args[0], args[1])

    def properties(self, args):
        props = dict()
        for kv in args:
            props[kv.key] = kv.value
        return props

    def multiline_vector_body(self, args):
        return args

    def multiline_vector_value(self, args):
        return KeyValue(args[0], args[1])
    
    def param_list(self, args):
        return self._as_flat_list(args)

    def _as_flat_list(self, args):
        # It is array of array (flatten it)
        return args[0]

    def _as_string(self, args):
        return args.value

class SofaTransformer(SofaStructTransformer):

    # This class is NOT thread-safe, as its
    # members are mutated

    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)
        # Consolidate aggregations since Lark 
        # processes in a streaming manner
        self.sofa_root = SofaRoot()

    def struct_body(self, args):
        return args[0]

    def struct(self, args):
        arg_len = len(args)
        if len(args) > 2:
            return Struct(args[0], args[1], args[2])
        elif arg_len > 1:
            return Struct(args[0], [], args[1])
        else:
            return Struct(args[0], [], {})

    def capabilities(self, args):
        return self._extend_arch_elem_list(self.sofa_root.capabilities, self._as_arch_elements(args, Capability))
    
    def capability(self, args):
        return args[0]
    
    def domains(self, args):
        return self._extend_arch_elem_list(self.sofa_root.domains, self._as_arch_elements(args, Domain))

    def domain(self, args):
        return args[0]
    
    def packages(self, args):
        return self._extend_arch_elem_list(self.sofa_root.packages, self._as_arch_elements(args, Package))

    def package(self, args):
        return args[0]
    
    def interfaces(self, args):
        return self._extend_arch_elem_list(self.sofa_root.interfaces, self._as_arch_elements(args, Interface))

    def interface(self, args):
        return args[0]
    
    def classes(self, args):
        return self._extend_arch_elem_list(self.sofa_root.classes, self._as_arch_elements(args, Class))

    def clazz(self, args):
        return args[0]
    
    def components(self, args):
        return self._extend_arch_elem_list(self.sofa_root.components, self._as_arch_elements(args, Component))

    def component(self, args):
        return args[0]
    
    def actors(self, args):
        return self._extend_arch_elem_list(self.sofa_root.actors, self._as_arch_elements(args, Actor))

    def actor(self, args):
        return args[0]
    
    def _as_arch_elements(self, args, clazz):
        elems = []
        for arg in args:
            if isinstance(arg, str):
                # All arch elements have struct. 
                # If it is a plain string, then it is just a name.
                elems.append(clazz(Struct(arg)))
            else:
                elems.append(clazz(arg))
        return elems

    def _extend_arch_elem_list(self, arch_elem, args):
        arch_elem.extend(args)
        return arch_elem

    def imports(self, args):
        imps = []
        for i in args:
            imp = i.children
            if len(imp) > 1:
                imps.append(ImportStyle(imp[1]))
            else:
                imps.append(Import(imp[0]))
        return self._extend_arch_elem_list(self.sofa_root.imports, imps)

    def diagrams(self, args):
        diags = []
        for i in args[0].children[0]:
            diags.append(Diagram(i))
        return self._extend_arch_elem_list(self.sofa_root.diagrams, diags)

    def stereotypes(self, args):
        s_profiles = []
        for i in args:
            profile = i.children[0]
            stereotypes = i.children[1]
            s_profiles.append(StereoTypeProfile(profile, stereotypes))
        return self._extend_arch_elem_list(self.sofa_root.stereotype_profiles, s_profiles)

    def primitives(self, args):
        prims = []
        for i in args[0].children[0]:
            prims.append(Primitive(Struct(i)))
        return self._extend_arch_elem_list(self.sofa_root.primitives, prims)

    def relation_type(self, args):
        return RelationType(args[0].data.value)
    
    def port(self, args):
        return Port(args[0])

    def relation(self, args):
        source_name = args[0].children[0]
        source_port = None
        if len(args[0].children) > 1:
            source_port = args[0].children[1]

        target_name = args[2].children[0]
        target_port = None
        if len(args[2].children) > 1:
            target_port = args[2].children[1]

        type = args[1]
        name = f"{source_name}_{type.name}_{target_name}"
        props = {}
        if len(args) > 3:
            props = args[3]
        return Relation(type, source_name, source_port, target_name, target_port, Struct(name=name, properties=props))

    def relations(self, args):
        return self._extend_arch_elem_list(self.sofa_root.relations, args)
    
    def sofa(self, args):
        self.sofa_root.set_children(args)
        return self.sofa_root

class SofaIR:

    def __init__(self):
        self.parser = SofaParser()
    
    def build(self, content: str) -> SofaRoot:
        ast = self.parser.parse(content)
        return self._build(ast)
    
    def _build(self, root: Tree) -> SofaRoot: 
        return SofaTransformer().transform(root)
