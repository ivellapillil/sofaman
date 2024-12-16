
from generator.generator import FileContext, Visitor
import lxml.etree as etree
from lxml.etree import Element, SubElement

NS_UML = "http://www.eclipse.org/uml2/4.0.0/UML"
NS_XMI = "http://www.omg.org/spec/XMI/20110701"

UML = "{%s}" % NS_UML
XMI = "{%s}" % NS_XMI

NS_MAP = {
    "xmi": NS_XMI,
    "uml": NS_UML
}

class XmlContext(FileContext):

    def __init__(self, out_file):
        super().__init__(out_file)
        self.root = Element(UML + "Model", nsmap=NS_MAP)

    def get_root_as_string(self):
        return str(etree.tostring(self.root, pretty_print=True), encoding="UTF8")

class XmlVisitor(Visitor):

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype(self, context, stereotype): ...
    
    def visit_actor(self, context, actor): ...

    def visit_component(self, context, component):
        elem = SubElement(context.root, UML + "packagedElement", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:Component")
        elem.set("name", component.struct.name)
    
    def visit_relation(self, context, relation): ...

    
    def visit_interface(self, context, interface): ...

    
    def visit_class(self, context, clazz): ...

    
    def visit_domain(self, context, domain): ...

    
    def visit_capability(self, context, capability): ...
