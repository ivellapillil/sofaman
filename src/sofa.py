from parser.sofa_parser import SofaParser
from ir.ir import SofaIR

class _Cached:
    ir = SofaIR()


class Sofa:

    def __init__(self):
        pass

    def build(self, content: str):
        return _Cached.ir.build(content)