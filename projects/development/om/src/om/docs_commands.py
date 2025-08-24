"""Documentation generation commands for Om CLI.

Integrates Sphinx auto-generation with CLI interface.
"""

import click
from pathlib import Path
from typing import Optional, List
import json

from .sphinx_auto import DocumentationBuilder, CodeAnalyzer, SphinxGenerator
from .scoped_cli import scoped_command, validate_scope


@click.group()
def docs():
    """Documentation generation and management commands."""
    pass


@docs.command()
@click.option('--source', '-s', default='src', help='Source directory to analyze')
@click.option('--output', '-o', default='docs', help='Output directory for documentation')
@click.option('--patterns', '-p', multiple=True, default=['**/*.py'], help='File patterns to include')
@click.option('--build-html', is_flag=True, help='Build HTML documentation after generation')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@scoped_command(['docs'])
@validate_scope
def generate(source, output, patterns, build_html, verbose):
    """Auto-generate Sphinx documentation from source code."""
    source_dir = Path(source)
    output_dir = Path(output)
    
    if not source_dir.exists():
        click.echo(f"error:source_not_found:{source_dir}")
        return
    
    click.echo(f"docs:generating:source:{source_dir}:output:{output_dir}")
    
    # Build documentation
    builder = DocumentationBuilder(source_dir, output_dir)
    result = builder.build_documentation(list(patterns))
    
    # Report results
    stats = result['analysis_stats']
    click.echo(f"docs:analysis:files:{stats['files_processed']}:elements:{stats['elements_found']}")
    
    if stats['errors'] and verbose:
        for error in stats['errors']:
            click.echo(f"docs:error:{error}")
    
    click.echo(f"docs:generated:files:{len(result['generated_files'])}")
    
    if verbose:
        for name, path in result['generated_files'].items():
            click.echo(f"docs:file:{name}:{path}")
    
    # Build HTML if requested
    if build_html:
        click.echo("docs:building_html")
        if builder.build_html():
            click.echo("docs:html_build:success")
        else:
            click.echo("docs:html_build:failed")


@docs.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for analysis results')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'text']))
@scoped_command(['docs'])
@validate_scope
def analyze(source_dir, output, output_format):
    """Analyze source code and extract documentation elements."""
    analyzer = CodeAnalyzer()
    source_path = Path(source_dir)
    
    all_elements = []
    for py_file in source_path.glob('**/*.py'):
        elements = analyzer.analyze_file(py_file)
        all_elements.extend(elements)
    
    if output_format == 'json':
        # Convert elements to JSON-serializable format
        elements_data = []
        for element in all_elements:
            elements_data.append({
                'name': element.name,
                'type': element.type,
                'signature': element.signature,
                'source_file': str(element.source_file),
                'line_number': element.line_number,
                'docstring': element.docstring,
                'annotations': element.annotations,
                'complexity': element.complexity,
                'dependencies': element.dependencies,
                'examples': element.examples
            })
        
        result = {
            'total_elements': len(elements_data),
            'elements': elements_data,
            'analysis_timestamp': click.DateTime().convert(None, None, None)
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"docs:analysis:saved:{output}")
        else:
            click.echo(json.dumps(result, indent=2))
    
    else:  # text format
        output_lines = [f"Documentation Analysis Results ({len(all_elements)} elements)"]
        output_lines.append("=" * 50)
        
        by_type = {}
        for element in all_elements:
            if element.type not in by_type:
                by_type[element.type] = []
            by_type[element.type].append(element)
        
        for element_type, elements in by_type.items():
            output_lines.append(f"\n{element_type.upper()} ({len(elements)}):")
            for element in elements:
                output_lines.append(f"  {element.name} - {element.signature}")
        
        result_text = '\n'.join(output_lines)
        
        if output:
            with open(output, 'w') as f:
                f.write(result_text)
            click.echo(f"docs:analysis:saved:{output}")
        else:
            click.echo(result_text)


@docs.command()
@click.argument('docs_dir', type=click.Path(exists=True))
@click.option('--format', 'output_format', default='html', type=click.Choice(['html', 'pdf', 'epub']))
@click.option('--clean', is_flag=True, help='Clean build directory first')
@scoped_command(['docs'])
@validate_scope
def build(docs_dir, output_format, clean):
    """Build documentation in specified format."""
    docs_path = Path(docs_dir)
    
    if clean:
        import subprocess
        try:
            subprocess.run(['make', 'clean'], cwd=docs_path, check=True)
            click.echo("docs:build:cleaned")
        except subprocess.CalledProcessError:
            click.echo("docs:build:clean_failed")
    
    # Build documentation
    try:
        import subprocess
        result = subprocess.run(
            ['make', output_format], 
            cwd=docs_path, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            click.echo(f"docs:build:success:{output_format}")
            build_dir = docs_path / '_build' / output_format
            if build_dir.exists():
                click.echo(f"docs:build:output:{build_dir}")
        else:
            click.echo(f"docs:build:failed:{output_format}")
            if result.stderr:
                click.echo(f"docs:build:error:{result.stderr}")
    
    except Exception as e:
        click.echo(f"docs:build:exception:{e}")


@docs.command()
@click.argument('docs_dir', type=click.Path(exists=True))
@click.option('--host', default='localhost', help='Host to serve on')
@click.option('--port', default=8000, help='Port to serve on')
@scoped_command(['docs'])
@validate_scope
def serve(docs_dir, host, port):
    """Serve documentation with live reload."""
    docs_path = Path(docs_dir)
    build_dir = docs_path / '_build' / 'html'
    
    if not build_dir.exists():
        click.echo("docs:serve:no_build_found:building")
        try:
            import subprocess
            subprocess.run(['make', 'html'], cwd=docs_path, check=True)
        except subprocess.CalledProcessError:
            click.echo("docs:serve:build_failed")
            return
    
    try:
        import http.server
        import socketserver
        import os
        
        os.chdir(build_dir)
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer((host, port), handler) as httpd:
            click.echo(f"docs:serve:started:http://{host}:{port}")
            click.echo("docs:serve:ctrl_c_to_stop")
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        click.echo("docs:serve:stopped")
    except Exception as e:
        click.echo(f"docs:serve:error:{e}")


@docs.command()
@click.argument('docs_dir', type=click.Path(exists=True))
@scoped_command(['docs'])
@validate_scope
def validate(docs_dir):
    """Validate documentation build and check for issues."""
    docs_path = Path(docs_dir)
    
    issues = []
    
    # Check required files
    required_files = ['conf.py', 'index.rst', 'Makefile']
    for req_file in required_files:
        if not (docs_path / req_file).exists():
            issues.append(f"missing_file:{req_file}")
    
    # Check build directory
    build_dir = docs_path / '_build'
    if not build_dir.exists():
        issues.append("no_build_directory")
    
    # Try test build
    try:
        import subprocess
        result = subprocess.run(
            ['make', 'html'], 
            cwd=docs_path, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            issues.append(f"build_failed:{result.stderr}")
    except Exception as e:
        issues.append(f"build_exception:{e}")
    
    # Report results
    if issues:
        click.echo(f"docs:validate:issues:{len(issues)}")
        for issue in issues:
            click.echo(f"docs:validate:issue:{issue}")
    else:
        click.echo("docs:validate:success")


# Register with main CLI
def register_docs_commands(main_cli):
    """Register documentation commands with main CLI."""
    # Register coverage commands
    try:
        from .coverage_commands import register_coverage_commands
        register_coverage_commands(docs)
    except ImportError:
        pass
    
    # Register schema commands
    try:
        from .schema_commands import register_schema_commands
        register_schema_commands(docs)
    except ImportError:
        pass
    
    main_cli.add_command(docs)