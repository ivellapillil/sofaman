from sofaman.ir.model import SofaRoot, Visitor
from typing import Protocol
import pathlib

class Context(Protocol):
    """
    A protocol that implements some of the support functionality needed by the visitor.
    """
    def write(self, content):
        """
        Write the content.
        """
        raise NotImplementedError()
    
    def write_ln(self, content = ""):
        """
        Write the content along with a new line.
        """
        self.write(content + "\n")

class BufferContext(Context):
    """
    Context with content stored in a buffer.
    """
    
    def __init__(self):
        self.content = ""
    
    def write(self, content):
        self.content += content
    
    def get_content(self):
        """
        Gets content from the buffer.
        """
        return self.content

class FileContext(Context):
    """
    Context with content stored in a file.
    """

    def __init__(self, out_file):
        self.out_file = out_file
        # Not nice. Hack for the moment to ensure old data is removed.
        with open(self.out_file, "w"): ...

    def write(self, content):
        # Yes, a very naive implementation for the moment
        with open(self.out_file, "a") as o:
            o.write(content)
    
    def name(self):
        """
        Name of the file.
        """
        return pathlib.PurePath(self.out_file).stem

class Generator:
    """
    Generates an output from the sofa model.
    """
    def generate(self, sofa_root: SofaRoot, context, visitor: Visitor): 
        """
        Generate using the given visitor.
        """
        sofa_root.visit(context, visitor)