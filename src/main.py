from sofa import Sofa

with open("test/resources/full_scope.sofa") as sa:
    print(Sofa().build(sa.read()))

with open("test/resources/simple.sofa") as sa:
    print(Sofa().build(sa.read()))

