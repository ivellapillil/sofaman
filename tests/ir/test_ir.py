import pytest
from textwrap import dedent

import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from sofaman.ir.model import Visibility, DiagramType
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
        sofa_root = self._get_root(setup, self._package_variations_with_usage)
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
    
    def _package_variations_with_usage(self):
        return test_variations.package_variations() + dedent("""
            class X:
                package: A.B
            class Y:
                package: C
            class Z:
                package: A
        """)

    def test_ir_diagram(self, setup):
        sofa_root = self._get_root(setup, test_variations.diagram_variations)
        diagrams = sofa_root.diagrams
        assert diagrams.elems[0].get_name() == "X"
        assert diagrams.elems[1].get_name() == "X and Y"
        assert diagrams.elems[2].get_type() == DiagramType.COMPONENT

    def test_ir_actor(self, setup):
        sofa_root = self._get_root(setup, test_variations.actor_variations)
        actors = sofa_root.actors
        assert actors[0].get_name() == "A"
        assert actors[1].get_name() == "B"
        assert actors[1].description() == "Represents a b actor"

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

