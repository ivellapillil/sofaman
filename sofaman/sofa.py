"""
Main entry point to generate the final output from the input sofa model.
"""
from sofaman.ir.model import IrContext
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

    def build(self, input_file, context, visitor):
        """
        Build the final output from the input sofa model file.
        """
        with open(input_file) as f:
            content = f.read()
            return self._generate(_Cached.ir.build(IrContext(_Cached.ir, input_file), content), context, visitor)
    
    def _generate(self, sofa_root, context, visitor):
        """
        Validate the sofa model and generate the final output.
        """
        sofa_root.validate()
        return Generator().generate(sofa_root, context, visitor)