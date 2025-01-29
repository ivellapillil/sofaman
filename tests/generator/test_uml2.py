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
        comm = elem2.find(f"./{UML}ownedComment[@{XMI}type='uml:Comment']")
        assert comm.get(f"{XMI}type") == "uml:Comment"
        assert comm.get("body") == "Represents a b actor"
        ann = comm.find(f"./{UML}annotatedElement")
        assert ann.get(f"{XMI}idref") == elem2.get(f"{XMI}id")

        assert root.find(f".//{{Efg}}E123[@base_Actor='{elem2.get(f"{XMI}id")}']", namespaces=root.nsmap) is not None

        self._print_element(root)

    def test_uml_component(self, setup):
        sofa_root = self._get_root(setup, test_variations.component_variations)
        components = sofa_root.components
        assert components[0].get_name() == "A"
        assert components[1].get_name() == "B"
        assert components[1].description() == "Represents a B component"
        assert components[1].ports()[0].get_name() == "8080"
        assert components[1].ports()[1].get_name() == "R80"
        # the other tests are same as archelement tests; see test_uml_class

    def test_uml_class(self, setup):
        sofa_root = self._get_root(setup, test_variations.class_variations)
        clss = sofa_root.classes
        assert clss[0].get_name() == "A"
        assert clss[1].get_name() == "B"
        assert clss[2].get_name() == "C"

        # The following belongs to ArchElement, so
        # testing in class is enough
        lits = clss[1].literals()
        assert lits == ["C", "D"]
        attrs = clss[1].attributes()
        assert len(attrs) == 1
        assert attrs[0].cardinality.to_numeric()[0]== 1 and attrs[0].cardinality.to_numeric()[1] == -1
        assert attrs[0].visibility == Visibility.PUBLIC
        assert attrs[0].type == "String"
        ops = clss[1].operations()
        assert ops[0].parameters[1].name == "two"

    def test_uml_relation(self, setup):
        sofa_root = self._get_root(setup, test_variations.relation_variations)
        relations = sofa_root.relations
        assert relations[0].source.name == "A"
        assert relations[0].target.name == "B"
        assert relations[0].source.port == None
        assert relations[0].target.port == None
        assert relations[0].type == RelationType.COMPOSITION
        assert relations[1].type == RelationType.ASSOCIATION
        assert relations[2].type == RelationType.AGGREGATION
        assert relations[3].type == RelationType.INHERITANCE
        assert relations[4].type == RelationType.REALIZATION
        assert relations[5].type == RelationType.BI_INFO_FLOW

        assert relations[6].type == RelationType.BI_ASSOCIATION
        assert relations[6].source.cardinality.lowerBound == "0"
        assert relations[6].source.cardinality.upperBound == "1"
        assert relations[6].target.cardinality.to_numeric() == (1, -1)

        assert relations[7].source.name == "A"
        assert relations[7].target.name == "B"
        assert relations[7].source.port.get_name() == "12"
        assert relations[7].target.port.get_name() == "R01"

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
