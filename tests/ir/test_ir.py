import pytest

import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
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
        sofa_root = setup.sofa_ir.build(tree)
        assert sofa_root.actors["name"] == "A"

