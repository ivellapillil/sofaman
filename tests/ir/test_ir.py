import pytest
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from lark import Tree

class TestSofaIR:

    @pytest.fixture
    def sofa_ir(self):
        return SofaIR()

    def test_build(self, sofa_ir):
        ...

    def test_build_with_empty_content(self, sofa_ir):
        ...