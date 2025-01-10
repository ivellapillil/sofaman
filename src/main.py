import sys

import fire

from sofa import Sofa
from generator.generator import BufferContext
from generator.json import JsonVisitor
from generator.uml2 import XmiVisitor, XmiContext, XmiFlavor
from generator.plantuml import PumlVisitor, PumlContext

class SofRun:
   
    def __init__(self, input_file, output_file, type="xmi"):
      self.input_file = input_file
      self.output_file = output_file
      self.type = type

    def build(self):
        with open(self.input_file) as sa:
            context = None
            visitor = None
            match self.type:
                case "json":
                    context = BufferContext()
                    visitor = JsonVisitor()
                case "xmi":
                    context = XmiContext(self.output_file, mode=XmiFlavor.SPARX_EA)
                    visitor = XmiVisitor()
                case "puml":
                    context = PumlContext(self.output_file)
                    visitor = PumlVisitor()
                case _:
                    raise f"Unknown type {self.type}"

            Sofa().build(sa.read(), context, visitor)
            if self.type == "xmi": print(context.get_content())

if __name__ == '__main__':
  fire.Fire(SofRun)
