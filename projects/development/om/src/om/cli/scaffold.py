"""Coordinated subsystem scaffolding commands."""

import click


@click.group()
def scaffold():
    """Coordinated subsystem scaffolding."""
    pass


# Placeholder for scaffold commands - these would be registered
# by external modules if available
@scaffold.command()
def info():
    """Show scaffold system information."""
    click.echo("scaffold:system:available")