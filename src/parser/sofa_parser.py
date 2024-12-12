import pathlib

from lark import Lark, Transformer
from lark.indenter import Indenter, PythonIndenter


class SofaIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = [] #['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = [] #['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

class SofaParser():

    def __init__(self):
        grammar_file = pathlib.Path(__file__).parent / "grammar/sofa.lark"
        with open(grammar_file) as f:
            self.parser = Lark(f.read(), parser='lalr', transformer=Transformer(), postlex=SofaIndenter())

    def parse(self, content):
        return self.parser.parse(content)

_sofa_parser = SofaParser()        

def parse(file):
    return _sofa_parser.parse(file)

