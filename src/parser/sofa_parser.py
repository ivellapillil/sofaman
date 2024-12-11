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


grammar_file = pathlib.Path(__file__).parent / "grammar/sofa.lark"

with open(grammar_file) as f:
    lark_parser = Lark(f.read(), parser='lalr', transformer=Transformer(), postlex=SofaIndenter())
    with open("test/resources/full_scope.sofa") as sa:
        print(lark_parser.parse(sa.read()).pretty())

    with open("test/resources/simple.sofa") as sa:
        print(lark_parser.parse(sa.read()).pretty())