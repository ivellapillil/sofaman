from textwrap import dedent

def package_variations():
    return dedent("""
                package A.B:
                    visibility: public
                package C
    """)

def diagram_variations():
    return dedent("""
                diagrams:
                    - Overview
                    - "CRM Ecosystem"
                    - "Technical Architecture":
                        type: component
                diagrams: [A, B, C]
    """)

def stereotype_variations():
    return dedent("""
                stereotype Abc: [A123, B234]
                stereotype Def: [D123]
                component A:
                    stereotypes: [Abc.B234]
                class B:
                    stereotypes: [Def.D123]
                interface C:
                    stereotypes: [Abc.A123, Def.D123]

    """)
    
def actor_variations():
    return dedent("""
                actor A
                actor B:
                    name: B actor
                    description:|
                        Represents a b actor
                    stereotypes: [Efg.E123]
                    package: R
                    diagrams:
                        N_diagram: 
                            style: dark
    """)

def actor_variations():
    return dedent("""
                actor A
                actor B:
                    name: B actor
                    description:|
                        Represents a b actor
                    stereotypes: [Efg.E123]
                    diagrams:
                        N_diagram: 
                            style: dark
    """)

def component_variations():
    return dedent("""
                component A
                component B:
                    name: A B component
                    description:|
                        Represents a B component
                    stereotypes: [Abc.123]
                    package: R
                    diagrams:
                        N_diagram: 
                            style: dark
    """)

def relation_variations():
    return dedent("""
                relation A composes B
                relation A associates B
                relation A aggregates B
                relation A@12 flow B@R01:
                    name: Flow to B
                    protocol: HTTPS
                    payload: C, D
                    "Sync/Async": sync
    """)

def primitives_variations():
    return dedent("""
                primitives: [String, Boolean]
    """)

def class_variations():
    return dedent("""
                class A
                class B:
                    literals:
                        - C
                        - D
                    attributes:
                        a: 
                            cardinality: 1
                            type: String
                            visibility: public
                    operations:
                        b:
                            visibility: public
                            parameters:
                                one:
                                    type: String
                                two:
                                    type: String
                                three:
                                    type: String
                                    direction: return
                        c:
                            parameters: [d, e, f]
                class C:
                    literals: [C, D]
    """)

def interface_variations():
    return dedent("""
                interface A:
                    attributes:
                        a: 
                            cardinality: 1
                interface B
    """)
    
def domain_variations():
    return dedent("""
                domain A:
                    name: "A domain"
                    capabilities:
                        - A
                        - "B C"
                        - "D/,E"
                domain B
    """)
    
def capability_variations():
    return dedent("""
                capability A:
                    name: "A capability"
                capability B
    """)


