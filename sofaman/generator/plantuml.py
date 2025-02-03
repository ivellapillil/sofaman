
from textwrap import dedent
from sofaman.generator.generator import FileContext, Visitor
from sofaman.ir.model import RelationType, Attribute, Port

class PumlContext(FileContext):

    def __init__(self, out_file, desc_as_notes = False):
        super().__init__(out_file)
        self.desc_as_notes = desc_as_notes

class PumlVisitor(Visitor):

    INDENT = " " * 4

    # In general the rendering puts newline in at first instead of later,
    # this is because PlantUML is a bit finicky on braces on a new line.
    # Putting newline in front avoids some conditional checks.

    def visit_root(self, context, sofa_root): 
        context.write_ln(f"@startuml {context.name()}\nallowmixing")
    
    def visit_package(self, context, package): 
        ... # Packages are rendered only when they are referenced by other objects

    def _wrap_inside_package(self, context, obj, content):
        if obj.package() is None: return content
        return f"\npackage {obj.package()} {{ {content} \n}}"
    
    def _sterotype(self, context, obj):
        if obj.stereotypes() is None: return ""
        stereotypes = ""
        for s in obj.stereotypes():
            stereotypes += f"<<{s}>>"
        return stereotypes

    def _description(self, context, obj):
        if not context.desc_as_notes or obj.description() is None: return ""
        context.write_ln(dedent(f"""
            note top of {obj.get_name()}
                {obj.description()}
            end note
        """))

    def visit_primitive(self, context, primitive): 
        context.write_ln(self._wrap_inside_package(context, primitive, f"\nclass {primitive.get_name()} {self._sterotype(context, primitive)}"))
        self._description(context, primitive)

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype_profile(self, context, stereotype): ...
    
    def visit_actor(self, context, actor): 
        context.write_ln(self._wrap_inside_package(context, actor, f"\nactor {actor.get_name()} {self._sterotype(context, actor)}"))
        self._description(context, actor)

    def visit_component(self, context, component):
        context.write(self._wrap_inside_package(context, component, f"\ncomponent {component.get_name()} {self._sterotype(context, component)}"))
        self._gen_ports(context, component)
        self._description(context, component)

    def _gen_ports(self, context, obj):
        ports = obj.list_values("ports", Port)

        if not ports: return

        context.write_ln("{")

        for port in ports:
            context.write(self.INDENT)
            context.write_ln(f"port {port.get_name()}")

        context.write_ln("}")

    def visit_relation(self, context, relation): 
        context.write_ln(f"\n{self._determine_source(context, relation)} {self._as_arrow(context, relation)} {self._determine_target(context, relation)}")
    
    def _determine_source(self, context, relation):
        return relation.source.port.get_name() if relation.source.port else relation.source.name
    
    def _determine_target(self, context, relation):
        return relation.target.port.get_name() if relation.target.port else relation.target.name
    
    def _as_arrow(self, context, relation):
        match relation.type:
            case RelationType.COMPOSITION:
                return "*-->"
            case RelationType.AGGREGATION:
                return "o-->"
            case RelationType.INHERITANCE:
                return "--|>"
            case RelationType.REALIZATION:
                return "..|>"
            case RelationType.BI_INFO_FLOW:
                return "<..>"
            case RelationType.ASSOCIATION:
                return "-->"
            case RelationType.INFORMATION_FLOW:
                return "..>"
            case RelationType.BI_ASSOCIATION:
                return "<-->"
            case _:
                return "--"
    
    def visit_interface(self, context, interface): 
        context.write_ln(self._wrap_inside_package(context, interface, f"\ninterface {interface.get_name()} {self._sterotype(context, interface)}"))
        self._gen_attributes(context, interface)
        self._description(context, interface)

    def visit_class(self, context, clazz): 
        context.write(self._wrap_inside_package(context, clazz, f"\nclass {clazz.get_name()} {self._sterotype(context, clazz)}"))
        self._gen_attributes(context, clazz)
        self._description(context, clazz)
        
    def _gen_attributes(self, context, obj):
        attrs = obj.attributes()

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
        context.write_ln("\n@enduml")
