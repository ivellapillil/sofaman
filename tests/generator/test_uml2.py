import pytest
from textwrap import dedent
import lxml.etree as etree

from sofaman.generator.generator import Generator
from sofaman.generator.uml2 import NS_MAP, NS_UML, XmiContext, XmiFlavor, XmiVisitor, XMI, UML
import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from sofaman.ir.model import RelationType, Visibility, DiagramType
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

class TestUml2:

    @pytest.fixture
    def setup(self):
        sofa_parser = parser.SofaParser()
        sofa_ir = SofaIR()
        return _Setup(sofa_parser, sofa_ir)
    
    def _generate(self, setup : _Setup, sofa_lang_fn):
        tree = setup.sofa_parser.parse(sofa_lang_fn())
        sofa_root = setup.sofa_ir._build(tree)
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
        lov.get("value") == "1"
        lov.get("type") == "uml:LiteralInteger"
        upv = attr[0].find(f"./{UML}upperValue")
        upv.get("value") == "-1"
        upv.get("type") == "uml:LiteralInteger"
        attr[0].find(f"./{UML}type").get(f"{XMI}idref") == self._get_packaged_element_by_name(root, "String").get(f"{XMI}id")

        oper = elem2.findall(f"./{UML}ownedOperation")
        assert len(oper) == 2
        assert oper[0].get("name") == "b"
        p1 = oper[0].find(f"./{UML}ownedParameter[@name='one']")
        p1.get("direction") == "in"
        p1.get("type") == "String"
        p2 = oper[0].find(f"./{UML}ownedParameter[@name='two']")
        p2.get("direction") == "in"
        p2.get("type") == "String"
        p3 = oper[0].find(f"./{UML}ownedParameter[@name='three']")
        p3.get("direction") == "return"
        p3.get("type") == "String"

        assert oper[1].get("name") == "c"
        p1 = oper[1].find(f"./{UML}ownedParameter[@name='d']")
        p1.get("direction") == "in"
        p1.get("type") == "String"
        p2 = oper[1].find(f"./{UML}ownedParameter[@name='e']")
        p2.get("direction") == "in"
        p2.get("type") == "String"
        p3 = oper[1].find(f"./{UML}ownedParameter[@name='f']")
        p3.get("direction") == "in"
        p3.get("type") == "String"

        elem3 = self._get_packaged_element_by_name(root, "C")
        assert elem3.get(f"{XMI}type") == "uml:Class"

    def test_uml_relation(self, setup):
        root = self._generate(setup, test_variations.relation_variations)
        self._print_element(root)

        cls_a = self._get_packaged_element_by_name(root, "A")
        cls_b = self._get_packaged_element_by_name(root, "B")

        inh = cls_a.find(f"./{UML}generalization[@{XMI}type='uml:Generalization']", namespaces=NS_MAP)
        assert inh.get("general") == cls_b.get(f"{XMI}id")

        relz = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:Realization']", namespaces=NS_MAP)
        assert len(relz) == 1
        relz[0].get("client") == cls_a.get(f"{XMI}id")
        relz[0].get("supplier") == cls_b.get(f"{XMI}id")

        inflow = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:InformationFlow']", namespaces=NS_MAP)
        assert len(inflow) == 2
        inflow[0].get("informationSource") == cls_a.get(f"{XMI}id")
        inflow[0].get("informationTarget") == cls_b.get(f"{XMI}id")
        inflow[1].get("informationSource") == cls_b.get(f"{XMI}id")
        inflow[1].get("informationTarget") == cls_a.get(f"{XMI}id")

        assocs = root.getroottree().findall(f".//{UML}packagedElement[@{XMI}type='uml:Association']", namespaces=NS_MAP)
        assert len(assocs) == 4
        # TODO: Add more tests for associations

    def test_uml_primitive(self, setup):
        sofa_root = self._get_root(setup, test_variations.primitives_variations)
        primitives = sofa_root.primitives
        assert primitives.elems[0].get_name() == "String"
        assert primitives.elems[1].get_name() == "Boolean"

    def test_uml_interface(self, setup):
        sofa_root = self._get_root(setup, test_variations.interface_variations)
        interfaces = sofa_root.interfaces
        assert interfaces.elems[0].get_name() == "A"
        assert interfaces.elems[1].get_name() == "B"

        assert interfaces.elems[0].attributes()[0].cardinality.to_numeric() == (1, -1)
        assert interfaces.elems[0].attributes()[1].cardinality.to_numeric() == (-1, 1)

    def test_uml_domain(self, setup):
        sofa_root = self._get_root(setup, test_variations.domain_variations)
        domains = sofa_root.domains
        assert domains.elems[0].get_name() == "A"
        assert domains.elems[1].get_name() == "B"

        assert domains.elems[0].capabilities()[0] == "A"
        assert domains.elems[0].capabilities()[1] == "B C"
        assert domains.elems[0].capabilities()[2] == "D/,E"

    def test_uml_capability(self, setup):
        sofa_root = self._get_root(setup, test_variations.capability_variations)
        capabilities = sofa_root.capabilities
        assert capabilities.elems[0].get_name() == "A"
        assert capabilities.elems[1].get_name() == "B"

        assert capabilities.elems[0].get_name() == "A"
