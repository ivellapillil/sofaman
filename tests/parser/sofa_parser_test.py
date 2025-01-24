import pytest
import os.path
import lark
from textwrap import dedent

from sofaman.parser.sofa_parser import SofaParser

class TestSofaParser:

    @pytest.fixture
    def parser(self):
        return SofaParser()

    def test_parse_all_valid_input(self, parser):
        dir = os.path.dirname(os.path.realpath(__file__))
        full_all = os.path.join(dir, 'full_all.sofa')
        with open(full_all) as f:
            content = f.read()
        result = parser.parse(content)
        assert isinstance(result, lark.tree.Tree)

    def test_parse_invalid_input(self, parser):
        content = """
            Random
        """
        with pytest.raises(Exception):
            parser.parse(content)
    
    def test_parse_package_variations(self, parser):
        content = """
                    package A.B:
                        visibility: public
                    package C
        """
        self.assert_variation(parser, content)

    def assert_variation(self, parser, content):
        result = parser.parse(dedent(content))
        assert isinstance(result, lark.tree.Tree)

    def test_parse_diagram_variations(self, parser):
        content = """
                    diagrams:
                        - Overview
                        - "CRM Ecosystem"
                        - "Technical Architecture":
                            type: component
                    diagrams: [A, B, C]
        """
        self.assert_variation(parser, content)

    def test_parse_stereotype_variations(self, parser):
        content = """
                    stereotype Abc: [A123, B234]
                    stereotype Def: [D123]
                    component A:
                        stereotypes: [Abc.B234]
                    class B:
                        stereotypes: [Def.D123]
                    interface C:
                        stereotypes: [Abc.A123, Def.D123]

        """
        self.assert_variation(parser, content)

    def test_parse_actor_variations(self, parser):
        content = """
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
        """
        self.assert_variation(parser, content)

    def test_parse_actor_variations(self, parser):
        content = """
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
        """
        self.assert_variation(parser, content)

    def test_parse_component_variations(self, parser):
        content = """
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
        """
        self.assert_variation(parser, content)

    def test_parse_relation_variations(self, parser):
        content = """
                    relation A composes B
                    relation A associates B
                    relation A aggregates B
                    relation A@12 flow B@R01:
                        name: Flow to B
                        protocol: HTTPS
                        payload: C, D
                        "Sync/Async": sync
        """
        self.assert_variation(parser, content)

    def test_parse_primitives_variations(self, parser):
        content = """
                    primitives: [String, Boolean]
        """
        self.assert_variation(parser, content)

    def test_parse_class_variations(self, parser):
        content = """
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
        """
        self.assert_variation(parser, content)

    def test_parse_interface_variations(self, parser):
        content = """
                    interface A:
                        attributes:
                            a: 
                                cardinality: 1
                    interface B
        """
        self.assert_variation(parser, content)

    def test_parse_domain_variations(self, parser):
        content = """
                    domain A:
                        name: "A domain"
                        capabilities:
                            - A
                            - "B C"
                            - "D/,E"
                    domain B
        """
        self.assert_variation(parser, content)


    def test_parse_capability_variations(self, parser):
        content = """
                    capability A:
                        name: "A capability"
                    capability B
        """
        self.assert_variation(parser, content)


