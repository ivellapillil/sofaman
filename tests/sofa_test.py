import pytest
from sofaman.sofa import Sofa
from unittest.mock import Mock
from sofaman.generator import BufferedContext

@pytest.fixture
def sofa():
    return Sofa()

def test_build(sofa):
    with open("tests/test_cases/full_all.sofa") as f:
        content = f.read()
    visitor = Mock()
    
    sofa.build(content, BufferedContext(), visitor)
    
    visitor.assert_called()

