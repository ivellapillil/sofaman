from sofaman.parser.sofa_parser import SofaParser
from sofaman.ir.ir import SofaIR
from sofaman.generator.generator import Generator

class _Cached:
    """
    Caches the intermediate representation of the sofa model.
    """
    ir = SofaIR()

class Sofa:
    """
    Sofa is the main class that is used to build the final output from the input sofa model.
    """

    def __init__(self):
        pass

    def build(self, content: str, context, visitor):
        """
        Build the final output from the input sofa model.
        """
        return self._generate(_Cached.ir.build(content), context, visitor)
    
    def _generate(self, sofa_root, context, visitor):
        """
        Validate the sofa model and generate the final output.
        """
        sofa_root.validate()
        return Generator().generate(sofa_root, context, visitor)