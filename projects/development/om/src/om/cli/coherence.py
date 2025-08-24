"""Coherence CLI commands."""

import click
import json
from pathlib import Path
from ..coherent_api import CoherentUpdateEngine, CoherentFileManager, get_api_key


@click.group()
def coherence():
    """Coherence-first operations."""
    pass


@coherence.command()
@click.argument('files', nargs=-1)
@click.argument('request')
def update(files, request):
    """Update files coherently."""
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not found")
        return
    
    engine = CoherentUpdateEngine(api_key)
    manager = CoherentFileManager(engine)
    
    result = manager.update_files(list(files), request)
    
    if result.get("success"):
        click.echo(f"✓ Updated {len(result['files'])} files (coherence: {result['coherence_score']:.2f})")
    else:
        click.echo(f"✗ Failed: {result.get('error')}")
        if result.get('issues'):
            for issue in result['issues']:
                click.echo(f"  - {issue}")


@coherence.command()
@click.argument('request')
def validate(request):
    """Validate request coherence."""
    from ..coherent_api import LogicalCoherenceValidator
    
    validator = LogicalCoherenceValidator()
    issues = validator.validate_request(request)
    
    if not issues:
        click.echo("✓ Request is logically coherent")
    else:
        click.echo(f"✗ Found {len(issues)} coherence issues:")
        for issue in issues:
            click.echo(f"  - {issue.description} ({issue.severity.name})")


@coherence.command()
def setup():
    """Setup coherence system."""
    api_key = click.prompt("Anthropic API key", hide_input=True)
    
    config_dir = Path.home() / '.om'
    config_dir.mkdir(exist_ok=True)
    
    config_path = config_dir / 'config.json'
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    
    config['anthropic_api_key'] = api_key
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo("✓ Coherence system configured")