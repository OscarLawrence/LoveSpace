"""Documentation commands."""

import click
import re
from pathlib import Path
from .utils import _check_docs_parser


@click.group()
def docs():
    """Documentation commands."""
    pass


@click.group()
def python():
    """Python documentation commands."""
    pass


@docs.command()
@click.argument('query')
def search(query):
    """Search code for patterns."""
    results = []
    for py_file in Path("modules").rglob("*.py"):
        try:
            content = py_file.read_text()
            if re.search(query, content, re.IGNORECASE):
                matches = re.findall(rf'(?:class|def)\s+(\w*{re.escape(query)}\w*)', content, re.IGNORECASE)
                for match in matches[:3]:
                    results.append(f"{py_file.stem}:{match}")
        except:
            continue
    
    click.echo(" ".join(results[:10]) if results else f"search:{query}:no_results")


@docs.command()
@click.argument('path')
def dense(path):
    """Show dense documentation."""
    dense_file = Path(f"dense/{path}.dense")
    if dense_file.exists():
        click.echo(dense_file.read_text().strip())
    else:
        # Try to find it
        for found in Path("dense").rglob(f"*{path}*.dense"):
            click.echo(found.read_text().strip())
            return
        click.echo(f"dense:{path}:not_found")


@python.command()
@click.argument('function_spec')
def parse(function_spec: str):
    """Parse Python function documentation.
    
    Function spec format: module.function (e.g., ast.parse)
    """
    if not _check_docs_parser():
        click.echo("error:docs_parser_not_available")
        return
        
    if '.' not in function_spec:
        click.echo(f"error:invalid_spec:{function_spec}")
        return
    
    module_name, function_name = function_spec.rsplit('.', 1)
    
    from docs_parser.python_stdlib import PythonStdlibParser
    parser = PythonStdlibParser()
    result = parser.get_function_docs(module_name, function_name)
    
    if result:
        click.echo(result)
    else:
        click.echo(f"docs:{function_spec}:not_found")


@python.command()
def warm():
    """Pre-cache popular Python stdlib functions."""
    if not _check_docs_parser():
        click.echo("error:docs_parser_not_available")
        return
    
    try:
        from docs_parser.batch_parser import BatchParser
        from docs_parser.python_stdlib import PythonStdlibParser
        parser = PythonStdlibParser()
        batch = BatchParser(parser)
        results = batch.warm_cache()
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        click.echo(f"cache_warmed:{success_count}/{total_count}")
        
    except Exception as e:
        click.echo(f"error:cache_warm_failed:{e}")


@docs.command()
@click.argument('url')
@click.option('--function', '-f', help='Extract specific function from docs')
def url(url: str, function: str = None):
    """Parse documentation from any URL using docling."""
    if not _check_docs_parser():
        click.echo("error:docs_parser_not_available")
        return
    
    try:
        from docs_parser.universal_parser import UniversalParser
        parser = UniversalParser()
        result = parser.parse_url(url, function)
        
        if result:
            click.echo(result)
        else:
            click.echo(f"docs:url:parse_failed:{url}")
            
    except Exception as e:
        click.echo(f"error:universal_parse_failed:{e}")


@docs.command()
@click.argument('query')
@click.option('--auto-parse', '-a', is_flag=True, help='Automatically parse top results')
@click.option('--provider', '-p', type=click.Choice(['auto', 'tavily', 'serper']), default='auto', help='Search provider to use')
def search_docs(query, auto_parse, provider):
    """Search for documentation URLs using Google Serper."""
    if not _check_docs_parser():
        click.echo("error:docs_parser_not_available")
        return
    
    try:
        from docs_parser.search import DocumentationSearcher
        searcher = DocumentationSearcher(provider=provider)
        results = searcher.search_docs(query, num_results=3)
        
        if not results:
            click.echo(f"search:{query}:no_results")
            return
        
        if auto_parse:
            from docs_parser.universal_parser import UniversalParser
            parser = UniversalParser()
            for result in results[:2]:  # Parse top 2 results
                try:
                    parsed = parser.parse_url(result['url'])
                    if parsed:
                        click.echo(f"=== {result['title']} ===")
                        click.echo(parsed[:500] + "..." if len(parsed) > 500 else parsed)
                        click.echo()
                except:
                    continue
        else:
            for result in results:
                click.echo(f"{result['title']}:{result['url']}")
                
    except Exception as e:
        click.echo(f"error:search_failed:{e}")


# Add python as a subgroup to docs
docs.add_command(python)