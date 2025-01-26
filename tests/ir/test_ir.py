import pytest

import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from sofaman.ir.model import Visibility
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

    def test_ir_actor(self, setup):
        tree = setup.sofa_parser.parse(test_variations.actor_variations())
        sofa_root = setup.sofa_ir._build(tree)
        for actor in sofa_root.actors:
            assert actor.get_name() in ["A", "B"]
            if actor.get_name() == "B":
                assert actor.description() == "Represents a b actor"

    def test_ir_class(self, setup):
        tree = setup.sofa_parser.parse(test_variations.class_variations())
        sofa_root = setup.sofa_ir._build(tree)
        for clazz in sofa_root.classes:
            assert clazz.get_name() in ["A", "B", "C"]
            if clazz.get_name() == "B":
                lits = clazz.literals()
                assert lits == ["C", "D"]
                attrs = clazz.attributes()
                assert len(attrs) == 1
                assert attrs[0].cardinality.to_numeric()[0]== 1 and attrs[0].cardinality.to_numeric()[1] == -1
                assert attrs[0].visibility == Visibility.PUBLIC
                ops = clazz.operations()
                assert ops[0].parameters[1].name == "two"
