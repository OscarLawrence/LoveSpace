"""Memory and session management commands."""

import click
from .utils import _check_memory


@click.group()
def memory():
    """Memory and session management commands."""
    pass


@memory.command()
def context():
    """Show current context."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.memory_integration import MemoryIntegration
        memory = MemoryIntegration()
        context = memory.get_current_context()
        memory.close()
        
        click.echo(f"context:active_modules:{len(context.get('modules', []))} "
                  f"session_id:{context.get('session_id', 'none')} "
                  f"scope:{context.get('scope', 'global')}")
        
    except Exception as e:
        click.echo(f"error:context_failed:{e}")


@memory.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Limit results')
@click.option('--format', '-f', type=click.Choice(['dense', 'json', 'yaml']), default='dense', help='Output format')
@click.option('--context', '-c', help='Context filter')
@click.option('--include-patterns', '-p', multiple=True, help='Include patterns')
def inject(query, limit, format, context, include_patterns):
    """Inject context based on query."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.memory_integration import MemoryIntegration
        memory = MemoryIntegration()
        
        results = memory.inject_context(
            query=query,
            limit=limit,
            format=format,
            context_filter=context,
            include_patterns=list(include_patterns)
        )
        
        memory.close()
        
        if format == 'dense':
            for result in results:
                click.echo(f"{result['type']}:{result['name']}:{result['relevance']:.2f}")
        else:
            import json
            click.echo(json.dumps(results, indent=2))
        
    except Exception as e:
        click.echo(f"error:inject_failed:{e}")


@memory.command()
@click.argument('queries', nargs=-1)
@click.option('--limit', '-l', default=10, help='Limit results per query')
@click.option('--format', '-f', type=click.Choice(['dense', 'json']), default='dense', help='Output format')
@click.option('--context', '-c', help='Context filter')
@click.option('--include-patterns', '-p', multiple=True, help='Include patterns')
@click.option('--dedupe', '-d', is_flag=True, help='Remove duplicates across queries')
def batch_inject(queries, limit, format, context, include_patterns, dedupe):
    """Batch inject context for multiple queries."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.memory_integration import MemoryIntegration
        memory = MemoryIntegration()
        
        all_results = []
        for query in queries:
            results = memory.inject_context(
                query=query,
                limit=limit,
                format=format,
                context_filter=context,
                include_patterns=list(include_patterns)
            )
            all_results.extend(results)
        
        if dedupe:
            seen = set()
            deduped = []
            for result in all_results:
                key = f"{result['type']}:{result['name']}"
                if key not in seen:
                    seen.add(key)
                    deduped.append(result)
            all_results = deduped
        
        memory.close()
        
        if format == 'dense':
            for result in all_results:
                click.echo(f"{result['type']}:{result['name']}:{result['relevance']:.2f}")
        else:
            import json
            click.echo(json.dumps(all_results, indent=2))
        
    except Exception as e:
        click.echo(f"error:batch_inject_failed:{e}")


@memory.command()
@click.option('--force', '-f', is_flag=True, help='Force repopulation')
@click.option('--enhanced', '-e', is_flag=True, help='Use enhanced pattern detection')
def populate_patterns(force, enhanced):
    """Populate pattern database."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.memory_integration import MemoryIntegration
        memory = MemoryIntegration()
        
        result = memory.populate_patterns(force=force, enhanced=enhanced)
        memory.close()
        
        click.echo(f"patterns_populated:{result['count']} "
                  f"time:{result['time']:.2f}s "
                  f"enhanced:{result['enhanced']}")
        
    except Exception as e:
        click.echo(f"error:populate_failed:{e}")