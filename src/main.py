from sofa import Sofa
from generator.generator import BufferContext
from generator.json import JsonVisitor
from generator.uml2 import XmlVisitor, XmlContext

with open("test/resources/full_scope.sofa") as sa:
    context = BufferContext()
    #Sofa().build(sa.read(), context, JsonVisitor())
    #print(context.get_content())

with open("test/resources/full_scope.sofa") as sa:
    context = XmlContext(None)
    Sofa().build(sa.read(), context, XmlVisitor())
    print(context.get_root_as_string())
