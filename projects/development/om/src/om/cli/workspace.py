"""Workspace management commands."""

import click
import tomllib
from pathlib import Path


@click.group()
def workspace():
    """Workspace commands."""
    pass


@workspace.command()
def status():
    """Show workspace status."""
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        members = config["tool"]["uv"]["workspace"]["members"]
        
        statuses = []
        for member in members:
            path = Path(member)
            if path.exists() and (path / "pyproject.toml").exists():
                statuses.append(f"{path.name}:✓")
            else:
                statuses.append(f"{path.name}:✗")
        
        click.echo(" ".join(statuses))
    except Exception as e:
        click.echo(f"workspace:error:{e}")


@workspace.command("list")
def list_modules():
    """List modules."""
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        members = config["tool"]["uv"]["workspace"]["members"]
        
        modules = []
        for member in members:
            path = Path(member)
            if path.exists() and (path / "pyproject.toml").exists():
                with open(path / "pyproject.toml", "rb") as f:
                    mod_config = tomllib.load(f)
                name = mod_config["project"]["name"]
                desc = mod_config["project"].get("description", "")
                modules.append(f"{name}:{desc}")
        
        click.echo("\n".join(modules))
    except Exception as e:
        click.echo(f"modules:error:{e}")