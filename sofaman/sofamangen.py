"""
CLI for generating architectural diagram/model files from a given Sofa model file.
"""

import sys

import click

from sofaman.sofa import Sofa
from sofaman.generator.uml2 import XmiVisitor, XmiContext, XmiFlavor
from sofaman.generator.plantuml import PumlVisitor, PumlContext

@click.command()
@click.option('--type', default="xmi", help='The type of the output file (possible values: xmi, puml)')
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def generate(input, output, type):
    """
    Generates architectural diagram/model files from a given Sofa model file. Supports XMI and PlantUML.

    \b
    Arguments:
        input    The input Sofa model file.
        output   The output file to be generated.
    """
    try: 
        _build(input, output, type)
    except SofaException as e:
        print(f"Error: {e}")
        sys.exit(1)

def _build(input, output, type):
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

    Sofa().build(input, context, visitor)

class SofaException(Exception): 
    """
    Represents class of exceptions that SofaMan can raise.
    """
    ...

if __name__ == '__main__':
    generate()