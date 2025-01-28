import pytest
import os.path
import lark
import tests.test_cases.test_variations as test_variations

from sofaman.parser.sofa_parser import SofaParser

class TestSofaParser:

    @pytest.fixture
    def parser(self):
        return SofaParser()

    def test_parse_all_valid_input(self, parser):
        dir = os.path.dirname(os.path.realpath(__file__))
        full_all = os.path.join(dir, '../test_cases/full_all.sofa')
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
        self.assert_variation(parser, test_variations.package_variations())

    def assert_variation(self, parser, content):
        result = parser.parse(content)
        assert isinstance(result, lark.tree.Tree)

    def test_parse_diagram_variations(self, parser):
        self.assert_variation(parser, test_variations.diagram_variations())

    def test_parse_stereotype_variations(self, parser):
        self.assert_variation(parser, test_variations.stereotype_variations())

    def test_parse_actor_variations(self, parser):
        self.assert_variation(parser, test_variations.actor_variations())

    def test_parse_component_variations(self, parser):
        self.assert_variation(parser, test_variations.component_variations())

    def test_parse_relation_variations(self, parser):
        self.assert_variation(parser, test_variations.relation_variations())

    def test_parse_primitives_variations(self, parser):
        self.assert_variation(parser, test_variations.primitives_variations())

    def test_parse_class_variations(self, parser):
        self.assert_variation(parser, test_variations.class_variations())

    def test_parse_interface_variations(self, parser):
        self.assert_variation(parser, test_variations.interface_variations())

    def test_parse_domain_variations(self, parser):
        self.assert_variation(parser, test_variations.domain_variations())


    def test_parse_capability_variations(self, parser):
        self.assert_variation(parser, test_variations.capability_variations())

