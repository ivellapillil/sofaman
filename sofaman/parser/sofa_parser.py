"""
Supports parsing of Sofa files into an abstract syntax tree (AST). It uses Lark to parse the content of a Sofa file.
"""
import pathlib

from lark import Lark, Transformer
from lark.indenter import Indenter, PythonIndenter


class _SofaIndenter(Indenter):
    """
    Custom indenter for the Sofa language to support whitespace significance.
    """
    NL_type = '_NL'
    OPEN_PAREN_types = [] #['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = [] #['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

class SofaParser():
    """
    SofaParser is a class that parses a Sofa file into an abstract syntax tree (AST).
    """

    def __init__(self):
        grammar_file = pathlib.Path(__file__).parent / "grammar/sofa.lark"
        with open(grammar_file) as f:
            self.parser = Lark(f.read(), parser='lalr', postlex=_SofaIndenter())

    def parse(self, content):
        """
        Parse the content of a Sofa file into an AST.
        """
        return self.parser.parse(content)

