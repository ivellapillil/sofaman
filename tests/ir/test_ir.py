import pytest
from textwrap import dedent

import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from sofaman.ir.model import RelationType, Visibility, DiagramType
import tests.test_cases.test_variations as test_variations

class _Setup:
    def __init__(self, sofa_parser, sofa_ir):
        self.sofa_parser = sofa_parser
        self.sofa_ir = sofa_ir

class TestSofaIR:

    @pytest.fixture
    def setup(self):
        sofa_parser = parser.SofaParser()
        sofa_ir = SofaIR()
        return _Setup(sofa_parser, sofa_ir)
    
    def _get_root(self, setup : _Setup, sofa_lang_fn):
        tree = setup.sofa_parser.parse(sofa_lang_fn())
        return setup.sofa_ir._build(tree)

    def test_ir_package(self, setup):
        sofa_root = self._get_root(setup, test_variations.package_variations)
        pks = sofa_root.packages
        assert pks[0].get_name() == "B"
        assert pks[1].get_name() == "C"
        assert pks[2].get_name() == "A"
        assert pks[0].get_qname() == "A.B"
        assert pks[1].get_name() == "C"
        assert pks[2].get_name() == "A"
        if pks[1].get_name() == "B":
            assert pks[1].visibility == Visibility.PUBLIC
        clss = sofa_root.classes
        assert clss[0].parent_package == pks[0]       
        assert clss[1].parent_package == pks[1]       
        assert clss[2].parent_package == pks[2]       

    def test_ir_package_missing(self, setup):
        content = dedent("""
                    class Y:
                        package: C
        """)
        with pytest.raises(Exception): # TODO: Make it custom exception
            tree = setup.sofa_parser.parse(content)
            return setup.sofa_ir._build(tree)

    def test_ir_diagram(self, setup):
        sofa_root = self._get_root(setup, test_variations.diagram_variations)
        diagrams = sofa_root.diagrams
        assert diagrams.elems[0].get_name() == "X"
        assert diagrams.elems[1].get_name() == "X and Y"
        assert diagrams.elems[2].get_type() == DiagramType.COMPONENT

        components = sofa_root.components
        assert components[0].get_name() == "A"
        assert components[0].diagrams()[0].get_name() == "N_diagram"
        assert components[0].diagrams()[0].get_type() == DiagramType.COMPONENT

    def test_ir_sereotype(self, setup):
        sofa_root = self._get_root(setup, test_variations.stereotype_variations)
        stereotypes = sofa_root.stereotype_profiles
        assert stereotypes.elems[0].get_name() == "Abc"
        assert stereotypes.elems[1].get_name() == "Def"
        assert stereotypes.elems[0].stereotypes == ["A123", "B234"]
        assert stereotypes.elems[1].stereotypes == ["D123"]

        components = sofa_root.components
        assert components[0].stereotypes()[0].get_name() == "B234"

        classes = sofa_root.classes
        assert classes[0].stereotypes()[0].get_name() == "D123"

        interfaces = sofa_root.interfaces
        assert interfaces[0].stereotypes()[0].get_name() == "A123"
        assert interfaces[0].stereotypes()[1].get_name() == "D123"

    def test_ir_actor(self, setup):
        sofa_root = self._get_root(setup, test_variations.actor_variations)
        actors = sofa_root.actors
        assert actors[0].get_name() == "A"
        assert actors[1].get_name() == "B"
        assert actors[1].description() == "Represents a b actor"

    def test_ir_component(self, setup):
        sofa_root = self._get_root(setup, test_variations.component_variations)
        components = sofa_root.components
        assert components[0].get_name() == "A"
        assert components[1].get_name() == "B"
        assert components[1].description() == "Represents a B component"
        assert components[1].ports()[0].get_name() == "8080"
        assert components[1].ports()[1].get_name() == "R80"
        # the other tests are same as archelement tests; see test_ir_class

    def test_ir_class(self, setup):
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

    def test_ir_relation(self, setup):
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

    def test_ir_primitive(self, setup):
        sofa_root = self._get_root(setup, test_variations.primitives_variations)
        primitives = sofa_root.primitives
        assert primitives.elems[0].get_name() == "String"
        assert primitives.elems[1].get_name() == "Boolean"

    def test_ir_interface(self, setup):
        sofa_root = self._get_root(setup, test_variations.interface_variations)
        interfaces = sofa_root.interfaces
        assert interfaces.elems[0].get_name() == "A"
        assert interfaces.elems[1].get_name() == "B"

        assert interfaces.elems[0].attributes()[0].cardinality.to_numeric() == (1, -1)
        assert interfaces.elems[0].attributes()[1].cardinality.to_numeric() == (-1, 1)

    def test_ir_domain(self, setup):
        sofa_root = self._get_root(setup, test_variations.domain_variations)
        domains = sofa_root.domains
        assert domains.elems[0].get_name() == "A"
        assert domains.elems[1].get_name() == "B"

        assert domains.elems[0].capabilities()[0] == "A"
        assert domains.elems[0].capabilities()[1] == "B C"
        assert domains.elems[0].capabilities()[2] == "D/,E"

    def test_ir_capability(self, setup):
        sofa_root = self._get_root(setup, test_variations.capability_variations)
        capabilities = sofa_root.capabilities
        assert capabilities.elems[0].get_name() == "A"
        assert capabilities.elems[1].get_name() == "B"

        assert capabilities.elems[0].get_name() == "A"
