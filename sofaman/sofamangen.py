"""
CLI for generating architectural diagram/model files from a given Sofa model file.
"""

import json
import sys

import click

from sofaman.sofa import Sofa
from sofaman.generator.uml2 import XmiVisitor, XmiContext, XmiFlavor
from sofaman.generator.plantuml import PumlVisitor, PumlContext
from sofaman.tools.export.id_export import IdExporter

class SofaException(Exception): 
    """
    Represents class of exceptions that SofaMan can raise.
    """
    ...

@click.group()
def main():
    """
    Provides various commands to generate XMI, PlantUML, and JSON files from a given Sofa model file. 
    Additionally, you can export IDs from a given XMI file and use it to generate XMI files with the IDs.
    """
    ...

@main.command()
@click.option('--type', default="xmi", help='The type of the output file (possible values: xmi, puml)')
@click.option('--ids_file', help='The id file to use')
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def generate(input, output, type, ids_file=None):
    """
    Generates architectural diagram/model files from a given Sofa model file. Supports XMI and PlantUML.

    \b
    Arguments:
        input    The input Sofa model file.
        output   The output file to be generated.
    """
    try: 
        _build(input, output, type, ids_file)
    except SofaException as e:
        print(f"Error: {e}")
        sys.exit(1)

def _build(input, output, type, ids_file=None):
    """
    Builds the architectural diagram/model files from a given Sofa model file.
    """
    context = None
    visitor = None
    match type:
        case "xmi":
            context = XmiContext(output, mode=XmiFlavor.SPARX_EA)
            visitor = XmiVisitor()
        case "puml":
            context = PumlContext(output)
            visitor = PumlVisitor()
        case _:
            raise SofaException(f"Unknown type {type}")
    
    if ids_file:
        with open(ids_file, 'r') as f:
            context.ids = json.load(f)

    Sofa().build(input, context, visitor)

@main.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def export(input, output):
    """
    Extracts IDs from the given XMI file, mapped to fully qualified names of XMI elements.

    \b
    Arguments:
        input    The input XMI file.
        output   The output JSON file.
    """
    try: 
        _export(input, output)
    except SofaException as e:
        print(f"Error: {e}")
        sys.exit(1)

def _export(input, output):
    """
    Exports the XMI IDs from a given XMI file, mapped to fully qualified names of XMI elements.
    """
    id_exporter = IdExporter(input)
    id_exporter.export(output)

if __name__ == '__main__':
    main()