import pytest
from unittest.mock import Mock

from sofaman.sofa import Sofa
from sofaman.ir.model import Visitor
from sofaman.generator.generator import BufferContext

@pytest.fixture
def sofa():
    return Sofa()

def test_build(sofa):
    with open("tests/test_cases/full_all.sofa") as f:
        content = f.read()
    visitor = Mock(Visitor)
    
    sofa.build(content, BufferContext(), visitor)
    
    visitor.visit_root.assert_called()
    visitor.visit_diagram.assert_called()
    visitor.visit_package.assert_called()
    visitor.visit_stereotype_profile.assert_called()
    visitor.visit_primitive.assert_called()
    visitor.visit_actor.assert_called()
    visitor.visit_component.assert_called()
    visitor.visit_relation.assert_called()
    visitor.visit_interface.assert_called()
    visitor.visit_class.assert_called()
    visitor.visit_domain.assert_called()
    visitor.visit_capability.assert_called()
    visitor.visit_end.assert_called()

