#!/usr/bin/env python3
"""AI-first monorepo management CLI - main entry point."""

import click
from .workspace import workspace
from .docs import docs, python
from .code import code
from .find import find
from .scaffold import scaffold
from .memory import memory
from .isolate import isolate
from .session import session
from .preferences import preferences
from .deploy import deploy
from .coherence import coherence


@click.group()
@click.option('--scope', help='Scope to specific modules/directories')
@click.option('--auto-scope', is_flag=True, help='Auto-detect scope from git changes')
@click.option('--no-scope', is_flag=True, help='Disable all scoping')
@click.option('--scope-info', is_flag=True, help='Show current scope and exit')
@click.pass_context
def main(ctx, scope, auto_scope, no_scope, scope_info):
    """AI-first monorepo management CLI."""
    ctx.ensure_object(dict)
    ctx.obj['scope'] = scope
    ctx.obj['auto_scope'] = auto_scope
    ctx.obj['no_scope'] = no_scope
    ctx.obj['scope_info'] = scope_info


# Register command groups
main.add_command(workspace)
main.add_command(docs)
main.add_command(code)
main.add_command(find)
main.add_command(scaffold)
main.add_command(memory)
main.add_command(isolate)
main.add_command(session)
main.add_command(preferences)
main.add_command(deploy)
main.add_command(coherence)


if __name__ == '__main__':
    main()