from sofa import Sofa
from generator.generator import BufferContext
from generator.json import JsonVisitor
from generator.uml2 import XmiVisitor, XmiContext, XmiFlavor

with open("test/resources/full_scope.sofa") as sa:
    context = BufferContext()
    #Sofa().build(sa.read(), context, JsonVisitor())
    #print(context.get_content())

with open("test/resources/full_scope.sofa") as sa:
    context = XmiContext("build/full_scope.xml", mode=XmiFlavor.SPARX_EA)
    Sofa().build(sa.read(), context, XmiVisitor())
    print(context.get_root_as_string())
