import pytest
import os.path
import lark
import tests.test_cases.test_variations as test_variations

from sofaman.tools.export.id_export import IdExporter

class TestExport:

    @pytest.fixture
    def exporter(self, tmp_path):
        return IdExporter("tests/test_cases/full_all.xmi")

    def test_plain_id(self, exporter):
        """
        Test the plain ID extraction from the XMI file.
        """
        ids = exporter.ids
        assert ids["full_all"] == "17ff2979-398e-4b16-a62a-4a52387b3b01"

    def test_nested_id(self, exporter):
        """
        Test the plain ID extraction from the XMI file.
        """
        ids = exporter.ids
        assert ids["full_all.Retail.CRM.CustomerDB"] == "6ff575dd-e7ef-4df0-9956-f502a40835de"
