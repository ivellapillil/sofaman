from ir.model import SofaRoot, Visitor
from typing import Protocol

class Context(Protocol):
    def write(self, content): raise NotImplementedError

class BufferContext(Context):
    
    def __init__(self):
        self.content = ""
    
    def write(self, content):
        self.content += content
    
    def get_content(self):
        return self.content

class FileContext(Context):

    def __init__(self, out_file):
        self.out_file = out_file

    def write(self, content):
        # Yes, a very naive implementation for the moment
        with open(self.out_file) as o:
            o.write(content)

class Generator:

    def generate(self, sofa_root: SofaRoot, context, visitor: Visitor): 
        sofa_root.visit(context, visitor)