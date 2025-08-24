"""CLI interface for documentation parser."""

import click
from .python_stdlib import PythonStdlibParser


@click.group()
def docs():
    """Documentation parsing commands."""
    pass


@docs.group()
def python():
    """Python documentation commands."""
    pass


@python.command()
@click.argument('function_spec')
def parse(function_spec: str):
    """Parse Python function documentation.
    
    Function spec format: module.function (e.g., ast.parse)
    """
    if '.' not in function_spec:
        click.echo(f"error:invalid_spec:{function_spec}")
        return
    
    module_name, function_name = function_spec.rsplit('.', 1)
    
    parser = PythonStdlibParser()
    result = parser.get_function_docs(module_name, function_name)
    
    if result:
        click.echo(result)
    else:
        click.echo(f"docs:{function_spec}:not_found")


if __name__ == '__main__':
    docs()