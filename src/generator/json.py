
from generator.generator import FileContext, Visitor
from jsonpickle import encode

class JsonContext(FileContext):

    def __init__(self, out_file):
        super().__init__(out_file)

class JsonVisitor(Visitor):

    def visit_diagram(self, context, diagram):
        context.write(encode(diagram))

    def visit_stereotype(self, context, stereotype): ...
    
    def visit_actor(self, context, actor): ...

    
    def visit_component(self, context, component): ...

    
    def visit_relation(self, context, relation): ...

    
    def visit_interface(self, context, interface): ...

    
    def visit_class(self, context, clazz): ...

    
    def visit_domain(self, context, domain): ...

    
    def visit_capability(self, context, capability): ...
