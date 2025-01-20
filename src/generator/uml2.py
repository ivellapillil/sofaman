
import uuid
from generator.generator import FileContext, Visitor
import lxml.etree as etree
from lxml.etree import Element, SubElement
from ir.model import Attribute, ArchElement, Module, Operation, Parameter, Struct, RelationType, PropertyContainer
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

    def is_sparx_ea(self):
        return self.mode == XmiFlavor.SPARX_EA

    def get_content(self):
        return str(etree.tostring(self.root, pretty_print=True), encoding="UTF8")

    def flush(self):
        self.write(self.get_content())

class XmiVisitor(Visitor):

    class RelationEndPoint:
        def __init__(self, relation, relation_elem, endpoint_obj, endpoint_elem):
            self.relation = relation
            self.relation_elem = relation_elem
            self.endpoint_obj = endpoint_obj
            self.endpoint_elem = endpoint_elem

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

    def _common_aspects(self, context, parent_elem, obj: ArchElement|str):
        self._owned_comment(parent_elem, obj)
        self._stereotypes(context, parent_elem, obj)

    def _owned_comment(self, parent, obj: ArchElement|str):
        if isinstance(obj, str):
            return
        if not obj.documentation():
            return
        
        elem = SubElement(parent, UML + "ownedComment", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:Comment")
        self._id_attr(elem) # Random ID
        elem.set("body", obj.documentation())
        self._annotated_element(elem, obj)
        # No need to register.
        return elem

    def _annotated_element(self, parent, obj: ArchElement|str):
        elem = SubElement(parent, UML + "annotatedElement", nsmap=NS_MAP)
        elem.set(XMI+"idref", obj.id)
        # No need to register.
        return elem

    def _stereotypes(self, context, parent, obj: ArchElement|str):
        if not isinstance(obj, PropertyContainer) or not obj.stereotypes():
            return
        
        for stereo in obj.stereotypes():
            elem = SubElement(context.root, "{%s}" % stereo.profile + stereo.name, nsmap=NS_MAP)
            elem.set("base_" + obj.__class__.__name__, obj.id)
            self._id_attr(elem) # Random ID

        # No need to register.
        return elem

    def _packaged_element(self, context, parent, obj: ArchElement|str, uml_name, is_abstract=False):
        elem = SubElement(parent, UML + "packagedElement", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:"+uml_name)
        self._id_attr(elem, obj.id)
        elem.set("name", obj.struct.name)
        elem.set("isAbstract", str(is_abstract).lower())
        self._register(obj, elem)
        self._common_aspects(context, elem, obj)
        return elem
    
    def _realization(self, relation_elem, src_ep: RelationEndPoint, tgt_ep: RelationEndPoint):
        relation_elem.set("client", src_ep.endpoint_obj.id)
        relation_elem.set("supplier", tgt_ep.endpoint_obj.id)

    def _inheritance(self, relation, src_ep: RelationEndPoint, tgt_ep: RelationEndPoint):
        elem = SubElement(src_ep.endpoint_elem, UML + "generalization", nsmap=NS_MAP)
        elem.set(XMI + "type", "uml:Generalization")
        if relation.struct and relation.struct.name: elem.set("name", relation.struct.name)
        elem.set("general", tgt_ep.endpoint_obj.id)
        elem.set("isSubstitutable", "true") # TODO: May be need to be exposed in sofa
        self._id_attr(elem) # Generated ID

    def _info_flow(self, relation_elem, src_ep: RelationEndPoint, tgt_ep: RelationEndPoint):
        relation_elem.set("informationSource", src_ep.endpoint_obj.id)
        relation_elem.set("informationTarget", tgt_ep.endpoint_obj.id)

    def _get_owned_end_elem(self, relation_elem):
        return relation_elem.find(UML + "ownedEnd")

    def _owned_literal(self, parent, obj, name):
        elem = SubElement(parent, UML + "ownedLiteral", nsmap=NS_MAP)
        elem.set("name", name)
        self._id_attr(elem, obj.id)
        self._register(obj, elem)
        self._common_aspects(elem, obj)
        return elem

    def _owned_attribute(self, context, parent, attr):
        elem = SubElement(parent, UML + "ownedAttribute", nsmap=NS_MAP)
        self._id_attr(elem, attr.id)
        if isinstance(attr, str):
            elem.set("name", attr)
        elif isinstance(attr, Attribute):
            elem.set("name", attr.name)
            elem.set("value", attr.value)
            elem.set(XMI + "type", "uml:Property")
            self._cardinality(elem, attr.cardinality)
            if attr.type is not None:
                arch_elem = self.sofa_root.get_by_name(attr.type)
                if arch_elem is not None: 
                    self._type(elem, arch_elem.id)
                else:
                    raise AssertionError(f"Type {attr.type} not defined. Please define it in your sofa file.")
        else:
            raise AssertionError("Attributes must be str|dict")
        self._register(attr, elem)
        self._common_aspects(context, elem, attr)
        return elem

    def _owned_operation(self, context, parent, op: Operation):
        elem = SubElement(parent, UML + "ownedOperation", nsmap=NS_MAP)
        self._id_attr(elem, op.id)
        if isinstance(op, str):
            elem.set("name", op)
        elif isinstance(op, Operation):
            elem.set("name", op.name)
            elem.set("visibility", op.visibility.value)
            if op.parameters:
                for param in op.parameters:
                    self._owned_parameter(context, elem, param)
        else:
            raise AssertionError("Operations must be of type str|dict")
        self._common_aspects(context, elem, op)
        return elem

    def _owned_parameter(self, context, parent, parameter):
        elem = SubElement(parent, UML + "ownedParameter", nsmap=NS_MAP)
        self._id_attr(elem, parameter.id)
        if isinstance(parameter, str):
            elem.set("name", parameter)
        elif isinstance(parameter, Parameter):
            elem.set("name", parameter.name)
            elem.set("direction", parameter.direction.value)
            if parameter.type:
                elem.set("type", parameter.type)
        else:
            raise AssertionError("Parameter must be of type str|dict")
        self._common_aspects(context, elem, parameter)
        return elem

    def _cardinality(self, elem, cardinality):
        if not cardinality: return
        lower, upper = cardinality.to_numeric()
        self._lower_value(elem, lower)
        self._upper_value(elem, upper)

    def _owned_association_attribute(self, parent, obj, relation):
        elem = SubElement(parent, UML + "ownedAttribute", nsmap=NS_MAP)
        self._id_attr(elem)
        elem.set("association", relation.id)
        self._type(elem, obj.id)
        self._cardinality(elem, relation.source.cardinality)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _lower_value(self, parent, value):
        elem = SubElement(parent, UML + "lowerValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralInteger")
        elem.set("value", str(value))
        self._id_attr(elem)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _upper_value(self, parent, value):
        elem = SubElement(parent, UML + "upperValue", nsmap=NS_MAP)
        elem.set(XMI+"type", "uml:LiteralUnlimitedNatural")
        elem.set("value", str(value))
        self._id_attr(elem)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _type(self, parent, refid):
        elem = SubElement(parent, UML + "type", nsmap=NS_MAP)
        elem.set(XMI+"idref", refid)
        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _owned_end(self, parent, relation, obj_refid):
        elem = SubElement(parent, UML + "ownedEnd", nsmap=NS_MAP)
        self._id_attr(elem)

        elem.set(XMI+"association", relation.id)

        type = SubElement(elem, UML + "type", nsmap=NS_MAP)
        type.set(XMI+"idref", obj_refid)

        self._cardinality(elem, relation.target.cardinality)

        # No registration as it is an attribute that is specific to XMI structure
        return elem

    def _member_end(self, parent, owned_end_refid):
        elem = SubElement(parent, UML + "memberEnd", nsmap=NS_MAP)
        elem.set(XMI+"idref", owned_end_refid)
        # No registration as it is an attribute that is specific to XMI structure
        return elem
    
    def visit_root(self, context, sofa_root):

        NS_MAP = {
            None: NS_UML, # Sparx EA doesn't like namespace in some elements (may be a defect)
            "xmi": NS_XMI,
            "uml": NS_UML
        }

        # Add a namespace for each profile.
        for prof in sofa_root.stereotype_profiles:
            NS_MAP[prof.name.lower()] = prof.name

        context.root = Element(XMI + "XMI", nsmap=NS_MAP)

        if context.is_sparx_ea():
            # The following elements are necessary in order for EA to recognize the types 
            # referenced in attributes. 
            doc = SubElement(context.root, XMI + "Documentation", nsmap=NS_MAP)
            doc.set(XMI + "exporter", "Enterprise Architect")
            doc.set(XMI + "exporterVersion", "6.5")
            doc.set(XMI + "exporterId", "1")

            # For some reason Sparx XMI Importer expects "uml:" namespace only on "Model" element.
            spx_nsmap = NS_MAP.copy()
            spx_nsmap.pop(None)
            context.umlModel = SubElement(context.root, UML + "Model", nsmap=spx_nsmap)
        else:
            context.umlModel = SubElement(context.root, UML + "Model", nsmap=NS_MAP)

        context.umlModel.set(XMI + "type", "uml:Model")
        context.contentRoot = context.umlModel

        self.sofa_root = sofa_root
        if context.is_sparx_ea():
            # Need an outer package for EA.
            # TODO: Revisit after implementing modules.
            elem = self._packaged_element(context, context.contentRoot, Module(Struct(context.name())), "Package")
            context.contentRoot = elem

    def visit_diagram(self, context, diagram): ...

    def visit_stereotype_profile(self, context, stereotype_profile): ... # Not used for UML (see visit_root)

    def visit_primitive(self, context, primitive): 
        self._packaged_element(context, context.contentRoot, primitive, "PrimitiveType")
    
    def visit_actor(self, context, actor): 
        _ = self._packaged_element(context, context.contentRoot, actor, "Actor")

    def visit_component(self, context, component):
        elem = self._packaged_element(context, context.contentRoot, component, "Component")
        self._attributes_operations(context, component, elem)
    
    def _get_rel_type(self, relation):
        if relation.is_association():
            return "Association"
        elif relation.is_information_flow():
            return "InformationFlow"
        elif relation.type == RelationType.REALIZATION:
            return "Realization"
        elif relation.type == RelationType.INHERITANCE:
            return "Inheritance"
        elif relation.type == RelationType.AGGREGATION:
            return "Association"
        elif relation.type == RelationType.COMPOSITION:
            return "Association"
        else:
            return "Unknown"

    def visit_relation(self, context, relation): 
        rel_elem = self._packaged_element(context, context.contentRoot, relation, self._get_rel_type(relation))

        src_obj = self.sofa_root.get_by_name(relation.source.name)
        tgt_obj = self.sofa_root.get_by_name(relation.target.name)

        src_endpoint = XmiVisitor.RelationEndPoint(relation, rel_elem, src_obj, self._lookup(src_obj))
        tgt_endpoint = XmiVisitor.RelationEndPoint(relation, rel_elem, tgt_obj, self._lookup(tgt_obj))
        
        match relation.type:
            case RelationType.REALIZATION:
                self._realization(rel_elem, src_endpoint, tgt_endpoint)
            case RelationType.INHERITANCE:
                self._inheritance(relation, src_endpoint, tgt_endpoint)
            case RelationType.INFORMATION_FLOW:
                self._info_flow(rel_elem, src_endpoint, tgt_endpoint)
            case _:
                self._connection_relationship_ends(relation, rel_elem, src_endpoint, tgt_endpoint)

        self._common_aspects(context, rel_elem, relation)

    def _connection_relationship_ends(self, relation, rel_elem, src_endpoint: RelationEndPoint, tgt_endpoint: RelationEndPoint):
        # Target endpoint has an ownedAttribute that refers to the source obj
        src_owned_attr_pointing_to_tgt = self._owned_association_attribute(src_endpoint.endpoint_elem, tgt_endpoint.endpoint_obj, relation)
        # Relation now needs to point to that attribute on one end
        self._member_end(rel_elem, src_owned_attr_pointing_to_tgt.attrib[f"{XMI}id"])
        
        match relation.type:
            case RelationType.AGGREGATION:
                src_owned_attr_pointing_to_tgt.set("aggregation", "shared")
            case RelationType.COMPOSITION:
                src_owned_attr_pointing_to_tgt.set("aggregation", "composite")
            case _:
                src_owned_attr_pointing_to_tgt.set("aggregation", "none")

        if relation.is_bidirectional():
            tgt_owned_attr_pointing_to_tgt = self._owned_association_attribute(tgt_endpoint.endpoint_elem, src_endpoint.endpoint_obj, relation)
            self._member_end(rel_elem, tgt_owned_attr_pointing_to_tgt.attrib[f"{XMI}id"])
        else:
            # Additional member points to ownedElem of the relation itself.
            rel_owned_end_elem = self._owned_end(rel_elem, relation, src_endpoint.endpoint_obj.id)
            self._member_end(rel_elem, rel_owned_end_elem.attrib[f"{XMI}id"])

    def visit_interface(self, context, interface): 
        elem = self._packaged_element(context, context.contentRoot, interface, "Interface", True)
        self._attributes_operations(context, interface, elem)

    def visit_class(self, context, clazz):
        # Need to move away from contentRoot and use packages.
        elem = self._packaged_element(context, context.contentRoot, clazz, "Class")
        self._attributes_operations(context, clazz, elem)

    def _attributes_operations(self, context, obj, elem):
        lits = obj.literals()
        if lits:
            for i in lits:
                if type(i) is not str: raise AssertionError("Literals must be strings")
                self._owned_literal(elem, obj, i)
    
        attrs = obj.attributes()
        if attrs:
            for i in attrs:
                self._owned_attribute(context, elem, i)
        
        ops = obj.operations()
        if ops:
            for i in ops:
                self._owned_operation(context, elem, i)

    def visit_domain(self, context, domain): ...
    
    def visit_capability(self, context, capability): ...

    def visit_end(self, context, sofa_root): 
        # Write to the file. 
        # TODO: Should it be here? Probably not.
        context.flush()
