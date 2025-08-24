"""Scoped CLI Integration.

Integrates agent scoping system with Click CLI for reduced cognitive load.
"""

import click
from typing import List, Optional
from pathlib import Path
import sys

from .agent_scoping import ScopeManager, ScopeContext, create_scope_context


class ScopedCLI:
    """CLI wrapper that provides scoped command filtering."""
    
    def __init__(self):
        self.scope_manager = ScopeManager()
        self.auto_scope_enabled = True
        self.verbose_scope_info = False
    
    def process_command(self, ctx: click.Context, command_parts: List[str], 
                       task_description: str = "", explicit_scopes: Optional[List[str]] = None) -> bool:
        """Process command with scope filtering."""
        if not command_parts:
            return True
        
        command = " ".join(command_parts)
        
        # LOGICAL COHERENCE VALIDATION HOOK
        try:
            from projects.core.validation.om_integration import OMIntegration
            om_integration = OMIntegration()
            coherence_result = om_integration.validate_before_execution(command, locals())
            if om_integration.should_halt_execution(coherence_result):
                click.echo(f"🛑 EXECUTION HALTED: {coherence_result.contradictions or coherence_result.impossibilities}")
                return False
        except ImportError:
            pass  # Validation module not available
        
        # Create scope context
        scope_context = create_scope_context(
            command=command,
            args=command_parts[1:] if len(command_parts) > 1 else [],
            task=task_description,
            history=self._get_recent_commands()
        )
        
        # Update scope
        if explicit_scopes:
            scope_result = self.scope_manager.update_scope(scope_context, explicit_scopes)
        elif self.auto_scope_enabled:
            scope_result = self.scope_manager.update_scope(scope_context)
        else:
            # No scoping - allow all commands
            return True
        
        # Check if command is in scope
        if not self.scope_manager.is_command_in_scope(command):
            suggested_scope = self.scope_manager.suggest_scope_for_command(command)
            
            if suggested_scope:
                click.echo(f"scope_error:command_not_in_scope:{command}:suggested_scope:{suggested_scope}")
                click.echo(f"hint:use --scope {suggested_scope} or --auto-scope")
            else:
                click.echo(f"scope_error:unknown_command:{command}")
            
            return False
        
        # Show scope info if verbose
        if self.verbose_scope_info:
            click.echo(f"scope_info:active:{':'.join(scope_result.scopes)}:confidence:{scope_result.confidence:.2f}")
        
        return True
    
    def show_scoped_help(self, scopes: Optional[List[str]] = None):
        """Show help filtered by current or specified scopes."""
        target_scopes = scopes or self.scope_manager.current_scopes
        available_commands = self.scope_manager.tool_provider.filter_commands(target_scopes)
        
        if target_scopes:
            click.echo(f"Available commands for scopes [{':'.join(target_scopes)}]:")
        else:
            click.echo("Available commands (all scopes):")
        
        # Group commands by scope
        scope_groups = {}
        for cmd in available_commands:
            scope = self.scope_manager.tool_provider.get_scope_for_command(cmd)
            if scope not in scope_groups:
                scope_groups[scope] = []
            scope_groups[scope].append(cmd)
        
        for scope, commands in scope_groups.items():
            click.echo(f"\n{scope.upper()}:")
            for cmd in sorted(commands):
                click.echo(f"  om {cmd}")
    
    def _get_recent_commands(self) -> List[str]:
        """Get recent command history for scope context."""
        # This could be enhanced to read from shell history or session file
        return []


# Global scoped CLI instance
scoped_cli = ScopedCLI()


def scope_option(f):
    """Decorator to add scope options to commands."""
    f = click.option('--scope', multiple=True, help='Explicit scope selection (docs, memory, analysis, code, parsing)')(f)
    f = click.option('--auto-scope', is_flag=True, help='Enable automatic scope determination')(f)
    f = click.option('--no-scope', is_flag=True, help='Disable scope filtering')(f)
    f = click.option('--scope-info', is_flag=True, help='Show scope information')(f)
    return f


def apply_scoping(ctx: click.Context, scope: tuple, auto_scope: bool, no_scope: bool, scope_info: bool):
    """Apply scoping configuration from command options."""
    if no_scope:
        scoped_cli.auto_scope_enabled = False
        return True
    
    if scope_info:
        scoped_cli.verbose_scope_info = True
    
    # Get command parts from context
    command_parts = []
    if ctx.info_name:
        command_parts.append(ctx.info_name)
    if ctx.parent and ctx.parent.info_name:
        command_parts.insert(0, ctx.parent.info_name)
    
    explicit_scopes = list(scope) if scope else None
    
    return scoped_cli.process_command(
        ctx, 
        command_parts, 
        explicit_scopes=explicit_scopes
    )


# New scoped commands
@click.group()
def scope():
    """Scope management commands."""
    pass


@scope.command()
@click.option('--task', '-t', help='Task description for scope determination')
@click.option('--module', '-m', help='Current module context')
@click.option('--history', help='Command history (comma-separated)')
def auto(task, module, history):
    """Automatically determine and set scope based on context."""
    history_list = history.split(',') if history else []
    
    context = create_scope_context(
        command="",
        task=task or "",
        module=module,
        history=history_list
    )
    
    result = scoped_cli.scope_manager.update_scope(context)
    
    click.echo(f"scope:auto_determined:{':'.join(result.scopes)}:confidence:{result.confidence:.2f}")
    click.echo(f"reasoning:{result.reasoning}")
    click.echo(f"available_commands:{len(result.filtered_commands)}")


@scope.command()
@click.argument('scopes', nargs=-1, required=True)
def set(scopes):
    """Explicitly set active scopes."""
    valid_scopes = ["docs", "memory", "analysis", "code", "parsing"]
    invalid = [s for s in scopes if s not in valid_scopes]
    
    if invalid:
        click.echo(f"error:invalid_scopes:{':'.join(invalid)}")
        click.echo(f"valid_scopes:{':'.join(valid_scopes)}")
        return
    
    context = create_scope_context(command="")
    result = scoped_cli.scope_manager.update_scope(context, list(scopes))
    
    click.echo(f"scope:set:{':'.join(result.scopes)}")
    click.echo(f"available_commands:{len(result.filtered_commands)}")


@scope.command()
def show():
    """Show current scope status."""
    stats = scoped_cli.scope_manager.get_scope_stats()
    available = scoped_cli.scope_manager.get_available_commands()
    
    click.echo(f"scope:current:{':'.join(stats['current_scopes'])}")
    click.echo(f"scope:stats:changes:{stats['total_changes']}:confidence:{stats['avg_confidence']:.2f}")
    click.echo(f"scope:most_used:{':'.join(stats['most_used_scopes'])}")
    click.echo(f"scope:available_commands:{len(available)}")


@scope.command()
@click.option('--scopes', help='Show help for specific scopes (comma-separated)')
def help(scopes):
    """Show scoped help - commands available in current or specified scopes."""
    target_scopes = scopes.split(',') if scopes else None
    scoped_cli.show_scoped_help(target_scopes)


@scope.command()
def clear():
    """Clear current scope (allow all commands)."""
    scoped_cli.scope_manager.current_scopes = []
    scoped_cli.scope_manager._save_session()
    click.echo("scope:cleared:all_commands_available")


@scope.command()
@click.argument('command')
def check(command):
    """Check if command is available in current scope."""
    if scoped_cli.scope_manager.is_command_in_scope(command):
        click.echo(f"scope:command_available:{command}")
    else:
        suggested = scoped_cli.scope_manager.suggest_scope_for_command(command)
        click.echo(f"scope:command_not_available:{command}")
        if suggested:
            click.echo(f"scope:suggestion:add_scope:{suggested}")


@scope.command()
def stats():
    """Show detailed scope usage statistics."""
    stats = scoped_cli.scope_manager.get_scope_stats()
    
    click.echo(f"scope_stats:total_changes:{stats['total_changes']}")
    click.echo(f"scope_stats:avg_confidence:{stats['avg_confidence']:.3f}")
    click.echo(f"scope_stats:current_scopes:{':'.join(stats['current_scopes'])}")
    click.echo(f"scope_stats:most_used:{':'.join(stats['most_used_scopes'])}")
    
    # Show recent scope history
    recent_history = scoped_cli.scope_manager.scope_history[-5:]
    for i, (timestamp, scopes, confidence) in enumerate(recent_history):
        click.echo(f"scope_history:{i}:{timestamp}:{':'.join(scopes)}:{confidence:.2f}")


# Integration function for main CLI
def integrate_scoping_with_main_cli(main_group):
    """Integrate scoping system with main CLI group."""
    # Add scope subcommand
    main_group.add_command(scope)
    
    # Add global scope options to main group
    main_group = scope_option(main_group)
    
    return main_group


def scoped_command(scopes: List[str]):
    """Decorator to mark commands as belonging to specific scopes."""
    def decorator(f):
        if not hasattr(f, '_om_scopes'):
            f._om_scopes = []
        f._om_scopes.extend(scopes)
        return f
    return decorator


# Scope validation decorator
def validate_scope(f):
    """Decorator to validate command is in current scope before execution."""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        command_name = ctx.info_name
        
        if hasattr(f, '_om_scopes'):
            required_scopes = f._om_scopes
            current_scopes = scoped_cli.scope_manager.current_scopes
            
            if current_scopes and not any(scope in current_scopes for scope in required_scopes):
                click.echo(f"scope_error:command_requires_scope:{command_name}:required:{':'.join(required_scopes)}")
                return
        
        return f(*args, **kwargs)
    
    return wrapper