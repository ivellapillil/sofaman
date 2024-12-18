
from generator.generator import FileContext, Visitor
import lxml.etree as etree
from lxml.etree import Element, SubElement
from ir.model import Attribute, ArchElement

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

    def _packaged_element(self, parent, obj: ArchElement|str, uml_name):
        elem = SubElement(parent, UML + "packagedElement", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:"+uml_name)
        elem.set(XMI + "id", obj.id)
        elem.set("name", obj.struct.name)
        return elem

    def _owned_literal(self, parent, obj, name):
        elem = SubElement(parent, UML + "ownedLiteral", nsmap=NS_MAP)
        elem.set("name", name)
        elem.set(XMI + "id", obj.id)
        return elem

    def _owned_attribute(self, parent, attr):
        elem = SubElement(parent, UML + "ownedAttribute", nsmap=NS_MAP)
        elem.set(XMI + "id", attr.id)
        if isinstance(attr, str):
            elem.set("name", attr)
        elif isinstance(attr, Attribute):
            elem.set("name", attr.name)
            elem.set("value", attr.value)
            self._lower_value(elem, attr.lowerBound)
            self._upper_value(elem, attr.upperBound)
            if attr.type is not None:
                attr_id = self.sofa_root.get_by_name(attr.type)
                if attr_id is not None: 
                    elem.set("type", attr_id)
        else:
            raise AssertionError("Attributes must be str|dict")
        return elem

    def _lower_value(self, parent, value):
        elem = SubElement(parent, UML + "lowerValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralInteger")
        elem.set("value", value)
        return elem

    def _upper_value(self, parent, value):
        elem = SubElement(parent, UML + "upperValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralUnlimitedNatural")
        elem.set("value", value)
        return elem

    def _type(self, parent, type):
        elem = SubElement(parent, UML + "type", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralUnlimitedNatural")
        elem.set("value", value)
        return elem

    def visit_root(self, context, sofa_root):
        self.sofa_root = sofa_root

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype(self, context, stereotype): ...

    def visit_primitive(self, context, primitive): 
        self._packaged_element(context.root, primitive, "PrimitiveType")
    
    def visit_actor(self, context, actor): ...

    def visit_component(self, context, component):
        elem = self._packaged_element(context.root, component, "Component")
    
    def visit_relation(self, context, relation): ...

    
    def visit_interface(self, context, interface): ...

    
    def visit_class(self, context, clazz):
        elem = self._packaged_element(context.root, clazz, "Class")
        lits = clazz.literals()
        for i in lits:
            if type(i) is not str: raise AssertionError("Literals must be strings")
            self._owned_literal(elem, clazz, i)
    
        attrs = clazz.attributes()
        for i in attrs:
            self._owned_attribute(elem, i)

    def visit_domain(self, context, domain): ...

    
    def visit_capability(self, context, capability): ...
