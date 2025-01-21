import pytest
from sofaman.parser.sofa_parser import SofaParser

class TestSofaParser:

    @pytest.fixture
    def parser(self):
        return SofaParser()

    def test_parse_valid_input(self, parser):
        content = """
        valid input content here
        """
        result = parser.parse(content)
        assert result is not None

    def test_parse_invalid_input(self, parser):
        content = """
        invalid input content here
        """
        with pytest.raises(Exception):
            parser.parse(content)