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
        result = parser.parse(dedent(content))
        assert isinstance(result, lark.tree.Tree)
