import pytest
from textwrap import dedent

from sofaman.generator.generator import BufferContext, Generator
from sofaman.generator.plantuml import PumlVisitor, PumlContext
import sofaman.parser.sofa_parser as parser
from sofaman.ir.ir import SofaIR, SofaRoot, SofaTransformer
from sofaman.ir.model import RelationType, Visibility, DiagramType
import tests.test_cases.test_variations as test_variations

class _Setup:
    def __init__(self, sofa_parser, sofa_ir):
        self.sofa_parser = sofa_parser
        self.sofa_ir = sofa_ir

class _PumlContext(BufferContext):

    def __init__(self, desc_as_notes = True):
        super().__init__()
        self.desc_as_notes = desc_as_notes

    def name(self):
        return "Test"

class TestPumlGenerator:

    @pytest.fixture
    def setup(self):
        sofa_parser = parser.SofaParser()
        sofa_ir = SofaIR()
        return _Setup(sofa_parser, sofa_ir)
    
    def _generate(self, setup : _Setup, sofa_lang_fn):
        tree = setup.sofa_parser.parse(sofa_lang_fn())
        sofa_root = setup.sofa_ir._build(tree)
        setup.sofa_root = sofa_root
        context = _PumlContext()
        visitor = PumlVisitor()
        Generator().generate(sofa_root, context, visitor)
        return context.content

    def test_puml_package(self, setup): 
        puml = self._generate(setup, test_variations.package_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                package A.B { 
                                class X  
                                }
                                package C { 
                                class Y  
                                }
                                package A { 
                                class Z  
                                }
                                @enduml
                        """)

    def test_puml_diagram(self, setup): ... # Not implemented yet

    def test_puml_stereotype(self, setup): 
        puml = self._generate(setup, test_variations.stereotype_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                interface C <<A123>><<D123>>

                                class B <<D123>>
                                component A <<B234>>
                                @enduml
                             """)

    def test_puml_actor(self, setup):
        puml = self._generate(setup, test_variations.actor_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                actor A 

                                actor B <<E123>>

                                note top of B
                                    Represents a b actor
                                end note
                                
                                
                                @enduml
                            """)

    def test_puml_component(self, setup):
        puml = self._generate(setup, test_variations.component_variations)
        assert f"\n{puml}" == dedent("""
                                    @startuml Test
                                    allowmixing

                                    component A 
                                    component B {
                                        port 8080
                                        port R80
                                    }

                                    note top of B
                                        Represents a B component
                                    end note


                                    @enduml
                            """)

    def test_puml_class(self, setup):
        puml = self._generate(setup, test_variations.class_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                class A 
                                class B {
                                    String a
                                }

                                class C 
                                class String 
                                @enduml
                            """)


    def test_puml_relation(self, setup):
        puml = self._generate(setup, test_variations.relation_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                class A 
                                class B 
                                A *--> B

                                A --> B

                                A o--> B

                                A --|> B

                                A ..|> B

                                A <..> B

                                A <--> B

                                12 ..> R01

                                @enduml
                            """)

    def test_puml_primitive(self, setup):
        puml = self._generate(setup, test_variations.primitives_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                class String 

                                class Boolean 

                                @enduml
                            """)

    def test_puml_interface(self, setup):
        puml = self._generate(setup, test_variations.interface_variations)
        assert f"\n{puml}" == dedent("""
                                @startuml Test
                                allowmixing

                                interface A 
                                {
                                    a
                                    b
                                }

                                interface B 

                                @enduml
                            """)


    def test_puml_domain(self, setup): ... # Not implemented yet

    def test_puml_capability(self, setup): ... # Not implemented yet
