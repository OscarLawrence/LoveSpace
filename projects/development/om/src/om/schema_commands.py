"""Schema generation commands for Om CLI."""

import click
from pathlib import Path
import json

from .schema_generation import SchemaGenerator, TypeDocumentationGenerator, SchemaValidator
from .scoped_cli import scoped_command, validate_scope


@click.group()
def schema():
    """Type schema generation and documentation commands."""
    pass


@schema.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for schemas')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'markdown']))
@click.option('--validate', is_flag=True, help='Validate generated schemas')
@scoped_command(['docs'])
@validate_scope
def generate(source_file, output, output_format, validate):
    """Generate type schemas from Python source file."""
    generator = SchemaGenerator()
    source_path = Path(source_file)
    
    click.echo(f"schema:generating:{source_path}")
    
    # Generate schemas
    schemas = generator.generate_module_schemas(source_path)
    
    if not schemas:
        click.echo("schema:no_types_found")
        return
    
    click.echo(f"schema:found:{len(schemas)}_types")
    
    # Validate if requested
    if validate:
        validator = SchemaValidator()
        issues = validator.validate_all_schemas(schemas)
        
        if issues:
            click.echo(f"schema:validation:issues:{len(issues)}")
            for name, schema_issues in issues.items():
                for issue in schema_issues:
                    click.echo(f"schema:validation:issue:{name}:{issue}")
        else:
            click.echo("schema:validation:passed")
    
    # Generate output
    if output_format == 'markdown':
        doc_generator = TypeDocumentationGenerator()
        content = doc_generator.generate_markdown_docs(schemas, f"Types from {source_path.name}")
    else:
        content = json.dumps(schemas, indent=2)
    
    # Output results
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"schema:saved:{output}")
    else:
        click.echo(content)


@schema.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='schemas', help='Output directory for schema files')
@click.option('--patterns', '-p', multiple=True, default=['**/*.py'], help='File patterns to process')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'markdown']))
@scoped_command(['docs'])
@validate_scope
def batch(source_dir, output_dir, patterns, output_format):
    """Generate schemas for all Python files in directory."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    generator = SchemaGenerator()
    doc_generator = TypeDocumentationGenerator()
    
    # Find all Python files
    python_files = []
    for pattern in patterns:
        python_files.extend(source_path.glob(pattern))
    
    click.echo(f"schema:batch:processing:{len(python_files)}_files")
    
    total_schemas = 0
    processed_files = 0
    
    for py_file in python_files:
        try:
            schemas = generator.generate_module_schemas(py_file)
            
            if schemas:
                # Generate output filename
                relative_path = py_file.relative_to(source_path)
                output_name = str(relative_path).replace('/', '_').replace('.py', '')
                
                if output_format == 'markdown':
                    output_file = output_path / f"{output_name}_types.md"
                    content = doc_generator.generate_markdown_docs(schemas, f"Types from {py_file.name}")
                else:
                    output_file = output_path / f"{output_name}_schemas.json"
                    content = json.dumps(schemas, indent=2)
                
                with open(output_file, 'w') as f:
                    f.write(content)
                
                total_schemas += len(schemas)
                processed_files += 1
                
                click.echo(f"schema:batch:file:{py_file.name}:{len(schemas)}_schemas")
        
        except Exception as e:
            click.echo(f"schema:batch:error:{py_file.name}:{e}")
    
    click.echo(f"schema:batch:complete:files:{processed_files}:schemas:{total_schemas}")


@schema.command()
@click.argument('schema_file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation results')
@scoped_command(['docs'])
@validate_scope
def validate(schema_file, verbose):
    """Validate JSON schema file."""
    with open(schema_file) as f:
        schemas = json.load(f)
    
    validator = SchemaValidator()
    
    if isinstance(schemas, dict) and 'definitions' in schemas:
        # JSON Schema format with definitions
        schemas_to_validate = schemas['definitions']
    else:
        # Direct schema dictionary
        schemas_to_validate = schemas
    
    issues = validator.validate_all_schemas(schemas_to_validate)
    
    if not issues:
        click.echo("schema:validate:passed")
        click.echo(f"schema:validate:schemas:{len(schemas_to_validate)}")
    else:
        click.echo("schema:validate:failed")
        click.echo(f"schema:validate:issues:{sum(len(i) for i in issues.values())}")
        
        if verbose:
            for name, schema_issues in issues.items():
                click.echo(f"\nschema:validate:schema:{name}")
                for issue in schema_issues:
                    click.echo(f"  - {issue}")


@schema.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('function_name')
@click.option('--output', '-o', help='Output file for function schema')
@scoped_command(['docs'])
@validate_scope
def function(source_file, function_name, output):
    """Generate schema for specific function."""
    import ast
    
    with open(source_file, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source, filename=str(source_file))
    
    # Find the function
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            func_node = node
            break
    
    if not func_node:
        click.echo(f"schema:function:not_found:{function_name}")
        return
    
    generator = SchemaGenerator()
    schema = generator.generate_function_schema(func_node)
    
    content = json.dumps(schema, indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"schema:function:saved:{output}")
    else:
        click.echo(content)


@schema.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('class_name')
@click.option('--output', '-o', help='Output file for class schema')
@scoped_command(['docs'])
@validate_scope
def class_schema(source_file, class_name, output):
    """Generate schema for specific class."""
    import ast
    
    with open(source_file, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source, filename=str(source_file))
    
    # Find the class
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            class_node = node
            break
    
    if not class_node:
        click.echo(f"schema:class:not_found:{class_name}")
        return
    
    generator = SchemaGenerator()
    schema = generator.generate_class_schema(class_node)
    
    content = json.dumps(schema, indent=2)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"schema:class:saved:{output}")
    else:
        click.echo(content)


# Register with docs commands
def register_schema_commands(docs_group):
    """Register schema commands with docs group."""
    docs_group.add_command(schema)