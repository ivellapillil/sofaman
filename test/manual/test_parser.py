from lark import Lark, Transformer
from lark.indenter import Indenter, PythonIndenter


class SofaIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = [] #['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = [] #['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


with open("test.lark") as f:
    lark_parser = Lark(f.read(), parser='lalr', transformer=Transformer(), postlex=SofaIndenter())
    with open("test.sofa") as sa:
        print(lark_parser.parse(sa.read()).pretty())