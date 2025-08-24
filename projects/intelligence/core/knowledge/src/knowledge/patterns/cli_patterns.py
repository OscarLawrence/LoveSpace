"""CLI and command processing patterns."""

from typing import List
from ..db_manager import Pattern


def get_cli_patterns() -> List[Pattern]:
    """Get CLI-related patterns."""
    return [
        Pattern(
            name="cli_argument_parser",
            language="python",
            pattern_type="cli",
            code_snippet="""
@click.command()
@click.argument('name')
@click.option('--count', default=1, help='Number of greetings')
def hello(name, count):
    for i in range(count):
        click.echo(f'Hello {name}!')
""",
            usage_context="Command line interface with Click - argument and option parsing",
            dependencies=["click"],
            success_count=25
        ),
        Pattern(
            name="cli_group_commands",
            language="python", 
            pattern_type="cli",
            code_snippet="""
@click.group()
def cli():
    pass

@cli.command()
def init():
    click.echo('Initializing...')

@cli.command()
def deploy():
    click.echo('Deploying...')
""",
            usage_context="CLI command groups for organizing related commands",
            dependencies=["click"],
            success_count=20
        ),
        Pattern(
            name="cli_validation",
            language="python",
            pattern_type="cli",
            code_snippet="""
def validate_path(ctx, param, value):
    if value and not Path(value).exists():
        raise click.BadParameter(f'Path {value} does not exist')
    return value

@click.command()
@click.option('--path', callback=validate_path)
def process(path):
    click.echo(f'Processing {path}')
""",
            usage_context="Input validation for CLI parameters",
            dependencies=["click", "pathlib"],
            success_count=15
        ),
        Pattern(
            name="cli_progress_bars",
            language="python",
            pattern_type="cli",
            code_snippet="""
import click

def process_items(items):
    with click.progressbar(items, label='Processing') as bar:
        for item in bar:
            # Process item
            time.sleep(0.1)
""",
            usage_context="Progress indication for long-running CLI operations",
            dependencies=["click"],
            success_count=12
        ),
        Pattern(
            name="cli_config_management",
            language="python",
            pattern_type="cli",
            code_snippet="""
@click.command()
@click.option('--config', type=click.Path(), default='config.json')
@click.pass_context
def cmd(ctx, config):
    if Path(config).exists():
        with open(config) as f:
            ctx.obj = json.load(f)
""",
            usage_context="Configuration file management in CLI applications",
            dependencies=["click", "json", "pathlib"],
            success_count=18
        ),
        Pattern(
            name="cli_output_formatting",
            language="python",
            pattern_type="cli",
            code_snippet="""
def format_output(data, format_type='table'):
    if format_type == 'json':
        return json.dumps(data, indent=2)
    elif format_type == 'csv':
        return '\\n'.join(','.join(row) for row in data)
    else:
        return tabulate(data, headers='firstrow', tablefmt='grid')
""",
            usage_context="Multiple output formats for CLI tools",
            dependencies=["json", "tabulate"],
            success_count=22
        ),
        Pattern(
            name="cli_error_handling",
            language="python",
            pattern_type="cli",
            code_snippet="""
def safe_cli_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            click.echo('\\nOperation cancelled by user', err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f'Error: {e}', err=True)
            sys.exit(1)
    return wrapper
""",
            usage_context="Robust error handling for CLI applications",
            dependencies=["click", "sys"],
            success_count=30
        ),
        Pattern(
            name="cli_environment_detection",
            language="python",
            pattern_type="cli",
            code_snippet="""
def detect_environment():
    env_vars = {
        'CI': os.getenv('CI'),
        'GITHUB_ACTIONS': os.getenv('GITHUB_ACTIONS'),
        'JENKINS_URL': os.getenv('JENKINS_URL'),
        'DOCKER': Path('/.dockerenv').exists()
    }
    
    if env_vars['GITHUB_ACTIONS']:
        return 'github_actions'
    elif env_vars['JENKINS_URL']:
        return 'jenkins'
    elif env_vars['DOCKER']:
        return 'docker'
    elif env_vars['CI']:
        return 'ci'
    else:
        return 'local'
""",
            usage_context="Environment detection for adaptive CLI behavior",
            dependencies=["os", "pathlib"],
            success_count=14
        )
    ]