"""User preferences management commands."""

import click
from .utils import _check_memory


@click.group()
def preferences():
    """User preferences management."""
    pass


@preferences.command()
@click.argument('category')
@click.argument('key')
@click.argument('value')
@click.option('--weight', '-w', type=float, default=1.0, help='Preference weight')
def set(category, key, value, weight):
    """Set user preference."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.preferences import PreferenceManager
        manager = PreferenceManager()
        
        result = manager.set_preference(category, key, value, weight)
        manager.close()
        
        click.echo(f"preference_set:{category}:{key}:{value}:weight:{weight}")
        
    except Exception as e:
        click.echo(f"error:set_preference_failed:{e}")


@preferences.command()
@click.argument('category', required=False)
def show(category):
    """Show user preferences."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.preferences import PreferenceManager
        manager = PreferenceManager()
        
        if category:
            prefs = manager.get_category_preferences(category)
            prefix = f"preferences:{category}"
        else:
            prefs = manager.get_all_preferences()
            prefix = "preferences:all"
        
        manager.close()
        
        if not prefs:
            click.echo(f"{prefix}:none")
            return
        
        for pref in prefs:
            click.echo(f"{prefix}:{pref['key']}:{pref['value']}:weight:{pref['weight']}")
        
    except Exception as e:
        click.echo(f"error:show_preferences_failed:{e}")


@preferences.command()
@click.argument('rating', type=int)
@click.argument('comment')
@click.option('--task', '-t', help='Task context')
@click.option('--module', '-m', help='Module context')
def feedback(rating, comment, task, module):
    """Provide feedback for preference learning."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.preferences import PreferenceManager
        manager = PreferenceManager()
        
        result = manager.record_feedback(rating, comment, task, module)
        manager.close()
        
        click.echo(f"feedback_recorded:rating:{rating}:task:{task}:module:{module}")
        
    except Exception as e:
        click.echo(f"error:feedback_failed:{e}")


@preferences.command()
def stats():
    """Show preference statistics."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.preferences import PreferenceManager
        manager = PreferenceManager()
        
        stats = manager.get_preference_stats()
        manager.close()
        
        click.echo(f"preference_stats:categories:{stats['categories']} "
                  f"total:{stats['total_preferences']} "
                  f"feedback_count:{stats['feedback_count']} "
                  f"avg_rating:{stats['avg_rating']:.1f}")
        
    except Exception as e:
        click.echo(f"error:stats_failed:{e}")