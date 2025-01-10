from ir.model import SofaRoot, Visitor
from typing import Protocol
import pathlib

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
        with open(self.out_file, "a") as o:
            o.write(content)
    
    def write_ln(self, content):
        self.write(content + "\n")

    def name(self):
        return pathlib.PurePath(self.out_file).stem

class Generator:

    def generate(self, sofa_root: SofaRoot, context, visitor: Visitor): 
        sofa_root.visit(context, visitor)