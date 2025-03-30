import json
from lxml import etree

NS_UML = "http://schema.omg.org/spec/UML/2.1"
NS_XMI = "http://schema.omg.org/spec/XMI/2.1"

UML = "{%s}" % NS_UML
XMI = "{%s}" % NS_XMI

NS_MAP = {
    "xmi": NS_XMI,
    "uml": NS_UML
}
class IdExporter:
    """
    Extracts IDs from the given XMI input file, mapped to fully qualified names of XMI elements into a given JSON output file.
    """

    def __init__(self, input):
        self.input_file = input
        self.ids = self._extract_ids(self._read().getroot(), "", {})

    def _read(self):
        """
        Reads the input file and returns a DOM.
        """
        return etree.parse(self.input_file)
        
    def _extract_ids(self, elem, parent_name, ids):
        """
        Extracts IDs from the dom.
        """
        for child in elem:
            name = child.get("name")
            if name:
                qname = name
                if parent_name:
                    qname = parent_name + "." + name

                id = child.get(XMI+"id")
                if id:
                    ids[qname] = id
            else:
                qname = parent_name

            self._extract_ids(child, qname, ids)
        return ids

    def export(self, output_file):
        """
        Exports the IDs from the XMI file.
        """
        with open(output_file, 'w') as file:
            json.dump(self.ids, file, indent=4)
