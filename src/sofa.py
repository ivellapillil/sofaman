from parser.sofa_parser import SofaParser
from ir.ir import SofaIR
from generator.generator import Generator

class _Cached:
    ir = SofaIR()


class Sofa:

    def __init__(self):
        pass

    def build(self, content: str, context, visitor):
        return self._generate(_Cached.ir.build(content), context, visitor)
    
    def _generate(self, sofa_root, context, visitor):
        return Generator().generate(sofa_root, context, visitor)