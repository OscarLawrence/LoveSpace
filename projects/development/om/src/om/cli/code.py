"""Code parsing and analysis commands."""

import click
import subprocess
import sys
from pathlib import Path
from .utils import _check_code_parser


@click.group()
def code():
    """Code parsing and analysis commands."""
    pass


@code.command()
@click.option('--full', '-f', is_flag=True, help='Full parsing with enhanced patterns')
@click.option('--enhanced', '-e', is_flag=True, help='Use enhanced pattern detection')
def parse(full, enhanced):
    """Parse codebase and populate knowledge base."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from code_parser.python_parser import PythonParser
        from knowledge.db_manager import ContextDB
        
        parser = PythonParser()
        db = ContextDB()
        
        if full or enhanced:
            from knowledge.enhanced_patterns import EnhancedPatternDetector
            detector = EnhancedPatternDetector()
            patterns = detector.detect_patterns()
            click.echo(f"patterns_detected:{len(patterns)}")
        
        # Parse all Python files
        parsed_count = 0
        for py_file in Path(".").rglob("*.py"):
            if "/.venv/" in str(py_file) or "/__pycache__/" in str(py_file):
                continue
            try:
                result = parser.parse_file(str(py_file))
                if result:
                    db.store_code_analysis(result)
                    parsed_count += 1
            except Exception:
                continue
        
        db.close()
        click.echo(f"parsing_complete:{parsed_count}_files")
        
    except Exception as e:
        click.echo(f"error:parsing_failed:{e}")


@code.command()
def stats():
    """Show code analysis statistics."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        stats = db.get_stats()
        db.close()
        
        click.echo(f"files:{stats.get('files', 0)} "
                  f"functions:{stats.get('functions', 0)} "
                  f"classes:{stats.get('classes', 0)} "
                  f"patterns:{stats.get('patterns', 0)}")
        
    except Exception as e:
        click.echo(f"error:stats_failed:{e}")


@code.command()
@click.argument('code')
@click.option('--timeout', '-t', default=30, help='Execution timeout in seconds')
def execute(code, timeout):
    """Execute Python code safely."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from code_parser.interpreter import SafeInterpreter
        interpreter = SafeInterpreter(timeout=timeout)
        result = interpreter.execute(code)
        
        if result['success']:
            if result['output']:
                click.echo(result['output'])
            else:
                click.echo("execution:success:no_output")
        else:
            click.echo(f"error:execution_failed:{result['error']}")
            
    except Exception as e:
        click.echo(f"error:interpreter_failed:{e}")


@code.command()
@click.argument('function_name')
def test(function_name):
    """Test a specific function."""
    if not _check_code_parser():
        click.echo("error:code_parser_not_available")
        return
    
    try:
        from knowledge.db_manager import ContextDB
        db = ContextDB()
        
        # Find function definition
        function_info = db.find_function(function_name)
        if not function_info:
            click.echo(f"function:{function_name}:not_found")
            return
        
        # Generate and run test
        from code_parser.interpreter import SafeInterpreter
        interpreter = SafeInterpreter()
        
        test_code = f"""
# Auto-generated test for {function_name}
try:
    result = {function_name}()
    print(f"test:{function_name}:passed:{{result}}")
except Exception as e:
    print(f"test:{function_name}:failed:{{e}}")
"""
        
        result = interpreter.execute(test_code)
        if result['output']:
            click.echo(result['output'])
        else:
            click.echo(f"test:{function_name}:no_output")
            
        db.close()
        
    except Exception as e:
        click.echo(f"error:test_failed:{e}")


@code.command()
@click.argument('command')
@click.option('--timeout', '-t', default=30, help='Command timeout in seconds')
def bash(command, timeout):
    """Execute bash command safely."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            if result.stdout:
                click.echo(result.stdout.strip())
            else:
                click.echo("bash:success:no_output")
        else:
            click.echo(f"bash:error:{result.stderr.strip()}")
            
    except subprocess.TimeoutExpired:
        click.echo(f"bash:timeout:{timeout}s")
    except Exception as e:
        click.echo(f"bash:error:{e}")