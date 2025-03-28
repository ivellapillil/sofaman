import pytest
import lxml.etree as etree

from sofaman.generator.generator import Generator
from sofaman.generator.uml2 import NS_MAP, XmiVisitor, XMI, UML
from sofaman.ir.model import IrContext
import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR
import tests.test_cases.test_variations as test_variations

class _Setup:
    def __init__(self, sofa_parser, sofa_ir):
        self.sofa_parser = sofa_parser
        self.sofa_ir = sofa_ir
        self.sofa_root = None

class _XMLContext:
    # TODO: May be the design of XMLContext need to be rethought
    
    def __init__(self):
        self.root = None

    def name(self):
        return "Test"

    def is_sparx_ea(self):
        return True
    
    def flush(self): ... # Do nothing. 

class TestUml2Generator:

    @pytest.fixture
    def setup(self):
        sofa_parser = parser.SofaParser()
        sofa_ir = SofaIR()
        return _Setup(sofa_parser, sofa_ir)
    
    def _generate(self, setup : _Setup, sofa_lang_fn):
        tree = setup.sofa_parser.parse(sofa_lang_fn())
        sofa_root = setup.sofa_ir._build(IrContext(setup.sofa_ir), tree)
        setup.sofa_root = sofa_root
        context = _XMLContext()
        visitor = XmiVisitor()
        Generator().generate(sofa_root, context, visitor)
        return self._get_root(context.root)

    def _get_root(self, element):
        return element.getroottree().getroot()

    def _print_element(self, element):
        print(str(etree.tostring(element, pretty_print=True), encoding="UTF8"), flush=True)

    def _get_packaged_element_by_name(self, root, name):
        elem = root.getroottree().find(f".//{UML}packagedElement[@name='{name}']", namespaces=NS_MAP)
        return elem

    def test_uml_root(self, setup):
        root = self._generate(setup, test_variations.package_variations)
        assert root.tag == XMI + "XMI"

    def test_uml_package(self, setup):
        root = self._generate(setup, test_variations.package_variations)

        elem = self._get_packaged_element_by_name(root, "A")
        assert elem.get("visibility") == "private"
        assert elem.get(f"{XMI}type") == "uml:Package"

        elem2 = self._get_packaged_element_by_name(root, "B")
        assert elem2.get("visibility") == "public"
        assert elem2.get(f"{XMI}type") == "uml:Package"
        assert elem2.getparent().get("name") == "A"

        assert elem.find("./*[2]").get("name") == "Z"
        assert elem.find("./*[2]").get(f"{XMI}type") == "uml:Class"

        assert elem2.find("./*[1]").get("name") == "X"
        assert elem2.find("./*[1]").get(f"{XMI}type") == "uml:Class"

        elem3 = self._get_packaged_element_by_name(root, "C")
        assert elem3.get(f"{XMI}type") == "uml:Package"
        assert elem3.find("./*[1]").get("name") == "Y"
        assert elem3.find("./*[1]").get(f"{XMI}type") == "uml:Class"

    def test_uml_diagram(self, setup): ... # Not implemented yet

    def test_uml_sereotype(self, setup):
        root = self._generate(setup, test_variations.stereotype_variations)

        assert "abc" in root.nsmap and root.nsmap["abc"] == "Abc"
        assert "def" in root.nsmap and root.nsmap["def"] == "Def"

        interface_id = setup.sofa_root.interfaces.elems[0].id
        class_id = setup.sofa_root.classes[0].id
        component_id = setup.sofa_root.components[0].id

        assert root.find(f".//{{Abc}}A123[@base_Interface='{interface_id}']", namespaces=root.nsmap) is not None
        assert root.find(f".//{{Def}}D123[@base_Interface='{interface_id}']", namespaces=root.nsmap) is not None
        assert root.find(f".//{{Def}}D123[@base_Class='{class_id}']", namespaces=root.nsmap) is not None
        assert root.find(f".//{{Abc}}B234[@base_Component='{component_id}']", namespaces=root.nsmap) is not None

    def test_uml_actor(self, setup):
        root = self._generate(setup, test_variations.actor_variations)

        elem = self._get_packaged_element_by_name(root, "A")
        assert elem.get(f"{XMI}type") == "uml:Actor"

        elem2 = self._get_packaged_element_by_name(root, "B")
        assert elem2.get(f"{XMI}type") == "uml:Actor"

        # Comments are the same for all different elements. So we test
        # only one of them
        comm = elem2.find(f"./{UML}ownedComment[@{XMI}type='uml:Comment']")
        assert comm.get(f"{XMI}type") == "uml:Comment"
        assert comm.get("body") == "Represents a b actor"
        ann = comm.find(f"./{UML}annotatedElement")
        assert ann.get(f"{XMI}idref") == elem2.get(f"{XMI}id")

        assert root.find(f".//{{Efg}}E123[@base_Actor='{elem2.get(f"{XMI}id")}']", namespaces=root.nsmap) is not None

    def test_uml_component(self, setup):
        root = self._generate(setup, test_variations.component_variations)

        elem = self._get_packaged_element_by_name(root, "A")
        assert elem.get(f"{XMI}type") == "uml:Component"

        elem2 = self._get_packaged_element_by_name(root, "B")
        assert elem2.get(f"{XMI}type") == "uml:Component"

        # TODO: Need to add test for ports once there is the support for it

    def test_uml_class(self, setup):
        root = self._generate(setup, test_variations.class_variations)

        elem = self._get_packaged_element_by_name(root, "A")
        assert elem.get(f"{XMI}type") == "uml:Class"

        elem2 = self._get_packaged_element_by_name(root, "B")
        assert elem2.get(f"{XMI}type") == "uml:Class"

        lits = elem2.findall(f"./{UML}ownedLiteral")
        assert len(lits) == 2
        assert lits[0].get("name") == "C"
        assert lits[1].get("name") == "D"

        attr = elem2.findall(f"./{UML}ownedAttribute")
        assert len(attr) == 1
        assert attr[0].get("name") == "a"
        lov = attr[0].find(f"./{UML}lowerValue")
        assert lov.get("value") == "1"
        assert lov.get(f"{XMI}type") == "uml:LiteralInteger"
        upv = attr[0].find(f"./{UML}upperValue")
        assert upv.get("value") == "-1"
        assert upv.get(f"{XMI}type") == "uml:LiteralUnlimitedNatural"
        str_id = self._get_packaged_element_by_name(root, "String").get(f"{XMI}id")
        assert str_id is not None
        assert attr[0].find(f"./{UML}type").get(f"{XMI}idref") == str_id

        oper = elem2.findall(f"./{UML}ownedOperation")
        assert len(oper) == 2
        assert oper[0].get("name") == "b"
        p1 = oper[0].find(f"./{UML}ownedParameter[@name='one']")
        assert p1.get("direction") == "in"
        assert p1.get("type") == "String"
        p2 = oper[0].find(f"./{UML}ownedParameter[@name='two']")
        assert p2.get("direction") == "in"
        assert p2.get("type") == "String"
        p3 = oper[0].find(f"./{UML}ownedParameter[@name='three']")
        assert p3.get("direction") == "return"
        assert p3.get("type") == "String"

        assert oper[1].get("name") == "c"
        p1 = oper[1].find(f"./{UML}ownedParameter[@name='d']")
        assert p1.get("direction") == "in"
        p2 = oper[1].find(f"./{UML}ownedParameter[@name='e']")
        assert p2.get("direction") == "in"
        p3 = oper[1].find(f"./{UML}ownedParameter[@name='f']")
        assert p3.get("direction") == "in"

        elem3 = self._get_packaged_element_by_name(root, "C")
        assert elem3.get(f"{XMI}type") == "uml:Class"

    def test_uml_relation(self, setup):
        root = self._generate(setup, test_variations.relation_variations)

        cls_a = self._get_packaged_element_by_name(root, "A")
        cls_a_id = cls_a.get(f"{XMI}id")
        assert cls_a_id is not None

        cls_b = self._get_packaged_element_by_name(root, "B")
        cls_b_id = cls_b.get(f"{XMI}id")
        assert cls_b_id is not None

        inh = cls_a.find(f"./{UML}generalization[@{XMI}type='uml:Generalization']", namespaces=NS_MAP)
        assert inh.get("general") == cls_b_id

        relz = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:Realization']", namespaces=NS_MAP)
        assert len(relz) == 1
        self._test_generalization(cls_a, cls_b, relz)

        inflow = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:InformationFlow']", namespaces=NS_MAP)
        assert len(inflow) == 2
        self._test_info_flow(cls_a, cls_b, inflow)

        assocs = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:Association']", namespaces=NS_MAP)
        assert len(assocs) == 4
        compos = assocs[0]
        self._test_composition(cls_a, cls_b, compos)

        assocn = assocs[1]
        self._test_association(cls_a, cls_b, assocn)

        aggr = assocs[2]
        self._test_aggregation(cls_a, aggr)

        biassocn = assocs[3]
        self._test_biassociation(cls_a, cls_b, biassocn)

        biflow = inflow[0]
        self._test_biflow(cls_a, cls_b, biflow)

    def _test_generalization(self, cls_a, cls_b, relz):
        assert relz[0].get("client") == cls_a.get(f"{XMI}id")
        assert relz[0].get("supplier") == cls_b.get(f"{XMI}id")

    def _test_info_flow(self, cls_a, cls_b, inflow):
        assert inflow[1].get("informationSource") == cls_a.get(f"{XMI}id")
        assert inflow[1].get("informationTarget") == cls_b.get(f"{XMI}id")
        # TODO: Test port and other attributes when implemented.

    def _test_biassociation(self, cls_a, cls_b, biassocn):
        a_fifth_ownedattr = cls_a.find(f'./{UML}ownedAttribute[5]')
        a_fifth_ownedattr_id = a_fifth_ownedattr.get(f'{XMI}id')
        assert a_fifth_ownedattr_id is not None
        assert biassocn.find(f"./{UML}memberEnd[1]").get(f'{XMI}idref') == a_fifth_ownedattr_id

        b_ownedattr2_id = cls_b.find(f'./{UML}ownedAttribute[2]').get(f'{XMI}id')
        assert b_ownedattr2_id is not None
        assert biassocn.find(f"./{UML}memberEnd[2]").get(f'{XMI}idref') == b_ownedattr2_id

        # TODO: Test cardinality when implemented.


    def _test_biflow(self, cls_a, cls_b, biflow):
        a_fourth_ownedattr = cls_a.find(f'./{UML}ownedAttribute[4]')
        a_fourth_ownedattr_id = a_fourth_ownedattr.get(f'{XMI}id')
        assert biflow.find(f"./{UML}memberEnd[1]").get(f'{XMI}idref') == a_fourth_ownedattr_id
        cls_b_ownedattr_2 = cls_b.find(f'./{UML}ownedAttribute[1]').get(f'{XMI}id')
        assert cls_b_ownedattr_2 is not None
        assert biflow.find(f"./{UML}memberEnd[2]").get(f'{XMI}idref') == cls_b_ownedattr_2

    def _test_aggregation(self, cls_a, aggr):
        assert aggr.find(f"./{UML}memberEnd[1]").get(f'{XMI}idref') == cls_a.find(f'./{UML}ownedAttribute[3]').get(f'{XMI}id')
        assert cls_a.find(f'./{UML}ownedAttribute[3]').get("aggregation") == "shared"
        aggr_ownedend = aggr.find(f"./{UML}ownedEnd")
        assert aggr_ownedend.get(f"{XMI}association") == aggr.get(f"{XMI}id")
        assert aggr_ownedend.find(f"./{UML}type").get(f"{XMI}idref") == cls_a.get(f"{XMI}id")
        assert aggr.find(f"./{UML}memberEnd[2]").get(f'{XMI}idref') == aggr_ownedend.get(f'{XMI}id')

    def _test_association(self, cls_a, cls_b, assocn):
        assert assocn.find(f"./{UML}memberEnd[1]").get(f'{XMI}idref') == cls_a.find(f'./{UML}ownedAttribute[2]').get(f'{XMI}id')
        assert cls_a.find(f'./{UML}ownedAttribute[2]').get("aggregation") == "none"
        assocn_ownedend = assocn.find(f"./{UML}ownedEnd")
        assert assocn_ownedend.get(f"{XMI}association") == assocn.get(f"{XMI}id")
        assert assocn_ownedend.find(f"./{UML}type").get(f"{XMI}idref") == cls_a.get(f"{XMI}id")
        assert assocn.find(f"./{UML}memberEnd[2]").get(f'{XMI}idref') == assocn_ownedend.get(f'{XMI}id')

    def _test_composition(self, cls_a, cls_b, compos):
        assert compos.find(f"./{UML}memberEnd[1]").get(f'{XMI}idref') == cls_a.find(f'./{UML}ownedAttribute[1]').get(f'{XMI}id')
        assert cls_a.find(f'./{UML}ownedAttribute[1]').get("aggregation") == "composite"
        compos_ownedend = compos.find(f"./{UML}ownedEnd")
        assert compos_ownedend.get(f"{XMI}association") == compos.get(f"{XMI}id")
        assert compos_ownedend.find(f"./{UML}type").get(f"{XMI}idref") == cls_a.get(f"{XMI}id")
        assert compos.find(f"./{UML}memberEnd[2]").get(f'{XMI}idref') == compos_ownedend.get(f'{XMI}id')

    def test_uml_primitive(self, setup):
        root = self._generate(setup, test_variations.primitives_variations)

        elem = self._get_packaged_element_by_name(root, "String")
        assert elem.get(f"{XMI}type") == "uml:PrimitiveType"

        elem2 = self._get_packaged_element_by_name(root, "Boolean")
        assert elem2.get(f"{XMI}type") == "uml:PrimitiveType"

    def test_uml_interface(self, setup):
        root = self._generate(setup, test_variations.interface_variations)

        elem = self._get_packaged_element_by_name(root, "A")
        assert elem.get(f"{XMI}type") == "uml:Interface"
        assert elem.get("isAbstract") == "true"

        elem2 = self._get_packaged_element_by_name(root, "B")
        assert elem2.get(f"{XMI}type") == "uml:Interface"
        assert elem2.get("isAbstract") == "true"

        elema_ownedattr = elem.findall(f"./{UML}ownedAttribute")
        assert len(elema_ownedattr) == 2
        assert elema_ownedattr[0].get("name") == "a"
        assert elema_ownedattr[0].get(f"{XMI}type") == "uml:Property"
        assert elema_ownedattr[1].get("name") == "b"
        assert elema_ownedattr[1].get(f"{XMI}type") == "uml:Property"

        elma_attr1_lowerval = elema_ownedattr[0].find(f"./{UML}lowerValue")
        assert elma_attr1_lowerval.get("value") == "1"
        assert elma_attr1_lowerval.get(f"{XMI}type") == "uml:LiteralInteger"

        elma_attr1_upperval = elema_ownedattr[0].find(f"./{UML}upperValue")
        assert elma_attr1_upperval.get("value") == "-1"
        assert elma_attr1_upperval.get(f"{XMI}type") == "uml:LiteralUnlimitedNatural"

        elma_attr2_lowerval = elema_ownedattr[1].find(f"./{UML}lowerValue")
        assert elma_attr2_lowerval.get("value") == "-1"
        assert elma_attr2_lowerval.get(f"{XMI}type") == "uml:LiteralInteger"
        elma_attr2_upperval = elema_ownedattr[1].find(f"./{UML}upperValue")
        assert elma_attr2_upperval.get("value") == "1"
        assert elma_attr2_upperval.get(f"{XMI}type") == "uml:LiteralUnlimitedNatural"

    def test_uml_domain(self, setup): ... # Not implemented yet in the generator

    def test_uml_capability(self, setup): ... # Not implemented yet in the generator
