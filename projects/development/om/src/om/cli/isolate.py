"""Module isolation commands."""

import click
from .utils import _check_memory


@click.group()
def isolate():
    """Module isolation commands."""
    pass


@isolate.command()
@click.argument('module_name')
@click.argument('task_type')
def create(module_name, task_type):
    """Create isolated module environment."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.module_isolation import ModuleIsolation
        isolation = ModuleIsolation()
        
        result = isolation.create_isolated_environment(module_name, task_type)
        isolation.close()
        
        click.echo(f"isolation_created:{module_name}:{task_type}:env_id:{result['env_id']}")
        
    except Exception as e:
        click.echo(f"error:isolation_create_failed:{e}")


@isolate.command()
@click.argument('module_name')
def focus(module_name):
    """Focus on specific module."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.module_isolation import ModuleIsolation
        isolation = ModuleIsolation()
        
        result = isolation.focus_module(module_name)
        isolation.close()
        
        click.echo(f"module_focused:{module_name}:dependencies:{result['dependencies']} "
                  f"isolation_level:{result['isolation_level']}")
        
    except Exception as e:
        click.echo(f"error:focus_failed:{e}")


@isolate.command()
@click.argument('module_name')
@click.option('--dependencies', '-d', multiple=True, help='Allowed dependencies')
@click.option('--rules', '-r', multiple=True, help='Isolation rules')
def boundaries(module_name, dependencies, rules):
    """Set module boundaries."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.module_isolation import ModuleIsolation
        isolation = ModuleIsolation()
        
        result = isolation.set_module_boundaries(
            module_name, 
            list(dependencies), 
            list(rules)
        )
        isolation.close()
        
        click.echo(f"boundaries_set:{module_name}:deps:{len(dependencies)}:rules:{len(rules)}")
        
    except Exception as e:
        click.echo(f"error:boundaries_failed:{e}")


@isolate.command()
@click.argument('module_name')
@click.argument('task')
def inject(module_name, task):
    """Inject task into isolated module."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.module_isolation import ModuleIsolation
        isolation = ModuleIsolation()
        
        result = isolation.inject_task(module_name, task)
        isolation.close()
        
        click.echo(f"task_injected:{module_name}:task_id:{result['task_id']} "
                  f"status:{result['status']}")
        
    except Exception as e:
        click.echo(f"error:inject_failed:{e}")


@isolate.command()
@click.argument('from_module')
@click.argument('to_module')
def handoff(from_module, to_module):
    """Clean handoff between modules."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.memory_integration import MemoryIntegration
        
        memory = MemoryIntegration()
        result = memory.manage_module_handoffs(from_module, to_module)
        memory.close()
        
        click.echo(f"handoff:completed:{from_module}:{to_module}:{result['status']}")
        
    except Exception as e:
        click.echo(f"error:handoff_failed:{e}")