
from generator.generator import FileContext, Visitor
from ir.model import RelationType, Attribute

class PumlContext(FileContext):

    def __init__(self, out_file):
        super().__init__(out_file)
        # Not nice. Hack for the moment to ensure old data is removed.
        with open(self.out_file, "w"): ...

class PumlVisitor(Visitor):

    INDENT = " " * 4

    def visit_root(self, context, sofa_root): 
        context.write_ln("@startuml\nallowmixing")

    def visit_primitive(self, context, primitive): 
        context.write_ln(f"class {primitive.get_name()}")

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype(self, context, stereotype): ...
    
    def visit_actor(self, context, actor): 
        context.write_ln(f"actor {actor.get_name()}")

    def visit_component(self, context, component):
        context.write_ln(f"component {component.get_name()}")
    
    def visit_relation(self, context, relation): 
        context.write_ln(f"{relation.source} {self._as_arrow(context, relation)} {relation.target}")
    
    def _as_arrow(self, context, relation):
        match relation.type:
            case RelationType.BI_ASSOCIATION:
                return "<-->"
            case RelationType.BI_INFO_FLOW:
                return "<..>"
            case RelationType.ASSOCIATION:
                return "-->"
            case RelationType.INFORMATION_FLOW:
                return "..>"
            case _:
                return "--"
    
    def visit_interface(self, context, interface): 
        context.write_ln(f"interface {interface.get_name()}")
    
    def visit_class(self, context, clazz): 
        context.write_ln(f"class {clazz.get_name()}")
        attrs = clazz.attributes()
        self._gen_attributes(context, attrs)
        
    def _gen_attributes(self, context, attrs):

        if not attrs: return

        context.write_ln("{")

        for attr in attrs:
            context.write(self.INDENT)
            if isinstance(attr, str):
                context.write_ln(f"{attr.name}")
            elif isinstance(attr, Attribute):
                if attr.type is not None: context.write(f"{attr.type} ")
                context.write_ln(f"{attr.name}")
            else:
                raise AssertionError("Attributes must be str|dict")

        context.write_ln("}")

    def visit_domain(self, context, domain): ...
    
    def visit_capability(self, context, capability): ...

    def visit_end(self, context, sofa_root): 
        context.write_ln("@enduml")
