from parser.sofa_parser import SofaParser
from ir.model import (SofaRoot, KeyValue, Struct, 
                    Capability, Domain, Interface, Component, 
                    Class, Import, ImportStyle, Diagram, Actor, 
                    Relation, RelationType, Capabilities, 
                    Domains, Interfaces, Components, Classes, 
                    Stereotype, Primitive, 
                    Imports, Diagrams, Actors, Relations, Stereotypes, Primitives)
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
        return args

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
        return Capabilities(self._as_arch_elements(args, Capability))
    
    def capability(self, args):
        return args[0]
    
    def domains(self, args):
        return Domains(self._as_arch_elements(args, Domain))

    def domain(self, args):
        return args[0]
    
    def interfaces(self, args):
        return Interfaces(self._as_arch_elements(args, Interface))

    def interface(self, args):
        return args[0]
    
    def classes(self, args):
        return Classes(self._as_arch_elements(args, Component))

    def clazz(self, args):
        return args[0]
    
    def components(self, args):
        return Components(self._as_arch_elements(args, Class))

    def component(self, args):
        return args[0]
    
    def actors(self, args):
        return Actors(self._as_arch_elements(args, Actor))

    def actor(self, args):
        return args[0]
    
    def _as_arch_elements(self, args, clazz):
        elems = []
        for arg in args:
            if isinstance(arg, str):
                # All arch elements have struct. 
                # If it is a plain string, then it is name.
                elems.append(clazz(Struct(arg)))
            else:
                elems.append(clazz(arg))
        return elems

    def imports(self, args):
        imps = []
        for i in args:
            imp = i.children
            if len(imp) > 1:
                imps.append(ImportStyle(imp[1]))
            else:
                imps.append(Import(imp[0]))
        return Imports(imps)

    def diagrams(self, args):
        diags = []
        for i in args[0].children[0]:
            diags.append(Diagram(i))
        return Diagrams(diags)

    def stereotypes(self, args):
        sts = []
        for i in args[0].children[0]:
            sts.append(Stereotype(i))
        return Stereotypes(sts)

    def primitives(self, args):
        prims = []
        for i in args[0].children[0]:
            prims.append(Primitive(Struct(i)))
        return Primitives(prims)

    def relation_type(self, args):
        return RelationType(args[0].data.value)

    def relation(self, args):
        source_name = args[0].children[0]
        target_name = args[2].children[0]
        type = args[1]
        name = f"{source_name}_{type.name}_{target_name}"
        props = {}
        if len(args) > 3:
            props = args[3]
        return Relation(type, source_name, target_name, Struct(name=name, properties=props))

    def relations(self, args):
        return Relations(args)
    
    def sofa(self, args):
        return SofaRoot(args)

class SofaIR:

    def __init__(self):
        self.parser = SofaParser()
    
    def build(self, content: str) -> SofaRoot:
        ast = self.parser.parse(content)
        return self._build(ast)
    
    def _build(self, root: Tree) -> SofaRoot: 
        return SofaTransformer().transform(root)
