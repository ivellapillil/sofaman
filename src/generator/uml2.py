
import uuid
from generator.generator import FileContext, Visitor
import lxml.etree as etree
from lxml.etree import Element, SubElement
from ir.model import Attribute, ArchElement, Module, Struct, RelationType
from enum import Enum

NS_UML = "http://schema.omg.org/spec/UML/2.1"
NS_XMI = "http://schema.omg.org/spec/XMI/2.1"

UML = "{%s}" % NS_UML
XMI = "{%s}" % NS_XMI

NS_MAP = {
    None: NS_UML, # Sparx EA doesn't like namespace in some elements (may be a defect)
    "xmi": NS_XMI,
    "uml": NS_UML
}

class XmiFlavor:
    NORMAL = 1
    SPARX_EA = 2

class XmiContext(FileContext):

    def __init__(self, out_file, mode=XmiFlavor.NORMAL):
        super().__init__(out_file)
        self.mode = mode
        self.root = Element(XMI + "XMI", nsmap=NS_MAP)

        if self.is_sparx_ea():
            # The following elements are necessary in order for EA to recognize the types 
            # referenced in attributes. 
            self.doc = SubElement(self.root, XMI + "Documentation", nsmap=NS_MAP)
            self.doc.set(XMI + "exporter", "Enterprise Architect")
            self.doc.set(XMI + "exporterVersion", "6.5")
            self.doc.set(XMI + "exporterId", "1")

            # For some reason Sparx XMI Importer expects "uml:" namespace only on "Model" element.
            spx_nsmap = NS_MAP.copy()
            spx_nsmap.pop(None)
            self.umlModel = SubElement(self.root, UML + "Model", nsmap=spx_nsmap)
        else:
            self.umlModel = SubElement(self.root, UML + "Model", nsmap=NS_MAP)

        self.umlModel.set(XMI + "type", "uml:Model")
        self.contentRoot = self.umlModel

    def is_sparx_ea(self):
        return self.mode == XmiFlavor.SPARX_EA

    def get_content(self):
        return str(etree.tostring(self.root, pretty_print=True), encoding="UTF8")

class XmiVisitor(Visitor):

    def __init__(self):
        super().__init__()
        self.registry = {}
    
    def _register(self, obj, elem):
        self.registry[obj] = elem
    
    def _lookup(self, obj):
        return self.registry[obj]

    def _id_attr(self, elem, id=None):
        id_val = id or str(uuid.uuid4())
        elem.set(XMI + "id", id_val)
        return id_val

    def _packaged_element(self, parent, obj: ArchElement|str, uml_name):
        elem = SubElement(parent, UML + "packagedElement", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:"+uml_name)
        self._id_attr(elem, obj.id)
        elem.set("name", obj.struct.name)
        self._register(obj, elem)
        return elem

    def _owned_literal(self, parent, obj, name):
        elem = SubElement(parent, UML + "ownedLiteral", nsmap=NS_MAP)
        elem.set("name", name)
        self._id_attr(elem, obj.id)
        self._register(obj, elem)
        return elem

    def _owned_attribute(self, parent, attr):
        elem = SubElement(parent, UML + "ownedAttribute", nsmap=NS_MAP)
        self._id_attr(elem, attr.id)
        if isinstance(attr, str):
            elem.set("name", attr)
        elif isinstance(attr, Attribute):
            elem.set("name", attr.name)
            elem.set("value", attr.value)
            elem.set(XMI + "type", "uml:Property")
            self._lower_value(elem, attr.lowerBound)
            self._upper_value(elem, attr.upperBound)
            if attr.type is not None:
                arch_elem = self.sofa_root.get_by_name(attr.type)
                if arch_elem is not None: 
                    self._type(elem, arch_elem.id)
        else:
            raise AssertionError("Attributes must be str|dict")
        self._register(attr, elem)
        return elem

    def _owned_association_attribute(self, parent, obj, relation):
        elem = SubElement(parent, UML + "ownedAttribute", nsmap=NS_MAP)
        self._id_attr(elem)
        elem.set("association", relation.id)
        self._type(elem, obj.id)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _lower_value(self, parent, value):
        elem = SubElement(parent, UML + "lowerValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralInteger")
        elem.set("value", value)
        self._id_attr(elem)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _upper_value(self, parent, value):
        elem = SubElement(parent, UML + "upperValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralUnlimitedNatural")
        elem.set("value", value)
        self._id_attr(elem)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _type(self, parent, refid):
        elem = SubElement(parent, UML + "type", nsmap=NS_MAP)
        elem.set(XMI+"idref", refid)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _owned_end(self, parent, rel_refid, obj_refid):
        elem = SubElement(parent, UML + "ownedEnd", nsmap=NS_MAP)
        elem.set(XMI+"association", rel_refid)

        type = SubElement(elem, UML + "type", nsmap=NS_MAP)
        type.set(XMI+"idref", obj_refid)

        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _member_end(self, parent, owned_end_refid):
        elem = SubElement(parent, UML + "memberEnd", nsmap=NS_MAP)
        elem.set(XMI+"idref", owned_end_refid)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def visit_root(self, context, sofa_root):
        self.sofa_root = sofa_root
        if context.is_sparx_ea():
            # Need an outer package for EA.
            elem = self._packaged_element(context.contentRoot, Module(Struct(context.name())), "Package")
            context.contentRoot = elem

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype(self, context, stereotype): ...

    def visit_primitive(self, context, primitive): 
        self._packaged_element(context.contentRoot, primitive, "PrimitiveType")
    
    def visit_actor(self, context, actor): ...

    def visit_component(self, context, component):
        elem = self._packaged_element(context.contentRoot, component, "Component")
    
    def _get_rel_type(self, relation):
        if relation.is_association():
            return "Association"
        elif relation.is_information_flow():
            return "Information"
        else:
            return "Unknown"

    def visit_relation(self, context, relation): 
        elem = self._packaged_element(context.contentRoot, relation, self._get_rel_type(relation))
        src = relation.source
        tgt = relation.target

        src_obj = self.sofa_root.get_by_name(src)
        tgt_obj = self.sofa_root.get_by_name(tgt)

        src_owned_e = self._owned_end(elem, relation.id, src_obj.id)
        src_id_attr_val = self._id_attr(src_owned_e)
        self._member_end(elem, src_id_attr_val)

        corres_src_elem = self._lookup(src_obj)
        src_owned_attr = self._owned_association_attribute(corres_src_elem, tgt_obj, relation)
        self._member_end(elem, src_owned_attr.attrib[f"{XMI}id"])

        if relation.is_bidirectional():
            tgt_owned_e = self._owned_end(elem, relation.id, tgt_obj.id)
            tgt_id_attr_val = self._id_attr(tgt_owned_e)
            #self._member_end(elem, tgt_id_attr_val)

            corres_tgt_elem = self._lookup(tgt_obj)
            tgt_owned_attr = self._owned_association_attribute(corres_tgt_elem, src_obj, relation)
            self._member_end(elem, tgt_owned_attr.attrib[f"{XMI}id"])
    
    def visit_interface(self, context, interface): ...

    def visit_class(self, context, clazz):
        elem = self._packaged_element(context.contentRoot, clazz, "Class")
        lits = clazz.literals()
        for i in lits:
            if type(i) is not str: raise AssertionError("Literals must be strings")
            self._owned_literal(elem, clazz, i)
    
        attrs = clazz.attributes()
        for i in attrs:
            self._owned_attribute(elem, i)

    def visit_domain(self, context, domain): ...

    
    def visit_capability(self, context, capability): ...
