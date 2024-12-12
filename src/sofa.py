import parser.sofa_parser as sofa

with open("test/resources/full_scope.sofa") as sa:
    print(sofa.parse(sa.read()).pretty())

with open("test/resources/simple.sofa") as sa:
    print(sofa.parse(sa.read()).pretty())

