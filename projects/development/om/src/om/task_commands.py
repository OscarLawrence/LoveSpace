"""Task management commands for Om CLI."""

import click
from datetime import datetime, timedelta
from pathlib import Path
import json

from .task_management import TaskManager, Task, TaskStatus, TaskPriority, TaskType
from .scoped_cli import scoped_command, validate_scope


@click.group()
def task():
    """AI-optimized task management commands."""
    pass


@task.command()
@click.argument('title')
@click.argument('description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium')
@click.option('--due', help='Due date (YYYY-MM-DD or relative like "3d", "1w")')
@click.option('--assign', help='Assign to user/agent')
@click.option('--tags', help='Comma-separated tags')
@scoped_command(['memory'])
@validate_scope
def create(title, description, priority, due, assign, tags):
    """Create a new task with intelligent analysis."""
    manager = TaskManager()
    
    # Parse due date
    due_date = None
    if due:
        due_date = _parse_due_date(due)
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    # Create task
    task = manager.create_task(
        title=title,
        description=description,
        priority=TaskPriority(priority),
        due_date=due_date,
        assigned_to=assign,
        tags=tag_list
    )
    
    click.echo(f"task:created:{task.id}")
    click.echo(f"task:type:{task.task_type.value}")
    click.echo(f"task:complexity:{task.metrics.complexity_score:.1f}")
    click.echo(f"task:estimated_duration:{task.metrics.estimated_duration}min")
    click.echo(f"task:scopes:{':'.join(task.context.scopes)}")
    
    if task.subtasks:
        click.echo(f"task:subtasks:{len(task.subtasks)}_suggested")


@task.command()
@click.argument('task_id')
@scoped_command(['memory'])
@validate_scope
def start(task_id):
    """Start working on a task (sets scope and status)."""
    manager = TaskManager()
    
    try:
        task = manager.start_task(task_id)
        click.echo(f"task:started:{task.id}")
        click.echo(f"task:title:{task.title}")
        click.echo(f"task:scopes_set:{':'.join(task.context.scopes)}")
        click.echo(f"task:status:{task.status.value}")
    except ValueError as e:
        click.echo(f"task:error:{e}")


@task.command()
@click.argument('task_id')
@click.option('--quality', type=float, help='Quality score (0-10)')
@scoped_command(['memory'])
@validate_scope
def complete(task_id, quality):
    """Mark task as completed."""
    manager = TaskManager()
    
    try:
        task = manager.complete_task(task_id, quality_score=quality)
        click.echo(f"task:completed:{task.id}")
        click.echo(f"task:progress:{task.metrics.progress_percentage:.1f}%")
        
        if task.metrics.quality_score:
            click.echo(f"task:quality:{task.metrics.quality_score:.1f}")
    except ValueError as e:
        click.echo(f"task:error:{e}")


@task.command()
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'blocked', 'completed', 'cancelled']))
@click.option('--type', 'task_type', type=click.Choice(['documentation', 'analysis', 'implementation', 'testing', 'refactoring', 'research', 'maintenance']))
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']))
@click.option('--assigned', help='Filter by assignee')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'summary']))
@scoped_command(['memory'])
@validate_scope
def list(status, task_type, priority, assigned, output_format):
    """List tasks with optional filtering."""
    manager = TaskManager()
    
    # Convert string enums
    status_filter = TaskStatus(status) if status else None
    type_filter = TaskType(task_type) if task_type else None
    priority_filter = TaskPriority(priority) if priority else None
    
    tasks = manager.list_tasks(
        status=status_filter,
        task_type=type_filter,
        priority=priority_filter,
        assigned_to=assigned
    )
    
    if output_format == 'json':
        task_data = [_task_to_dict(task) for task in tasks]
        click.echo(json.dumps(task_data, indent=2, default=str))
    
    elif output_format == 'summary':
        click.echo(f"task:list:total:{len(tasks)}")
        
        # Group by status
        by_status = {}
        for task in tasks:
            status_key = task.status.value
            if status_key not in by_status:
                by_status[status_key] = 0
            by_status[status_key] += 1
        
        for status_key, count in by_status.items():
            click.echo(f"task:list:status:{status_key}:{count}")
    
    else:  # table format
        if not tasks:
            click.echo("task:list:empty")
            return
        
        click.echo("task:list:header:ID:Title:Type:Status:Priority:Due")
        
        for task in tasks:
            due_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
            click.echo(f"task:list:row:{task.id[:8]}:{task.title}:{task.task_type.value}:{task.status.value}:{task.priority.value}:{due_str}")


@task.command()
@click.argument('task_id')
@click.option('--format', 'output_format', default='detailed', type=click.Choice(['detailed', 'json', 'tree']))
@scoped_command(['memory'])
@validate_scope
def show(task_id, output_format):
    """Show detailed task information."""
    manager = TaskManager()
    
    task = manager.get_task(task_id)
    if not task:
        click.echo(f"task:error:not_found:{task_id}")
        return
    
    if output_format == 'json':
        click.echo(json.dumps(_task_to_dict(task), indent=2, default=str))
    
    elif output_format == 'tree':
        tree_data = manager.get_task_tree(task_id)
        click.echo(json.dumps(tree_data, indent=2, default=str))
    
    else:  # detailed format
        click.echo(f"task:show:id:{task.id}")
        click.echo(f"task:show:title:{task.title}")
        click.echo(f"task:show:description:{task.description}")
        click.echo(f"task:show:type:{task.task_type.value}")
        click.echo(f"task:show:status:{task.status.value}")
        click.echo(f"task:show:priority:{task.priority.value}")
        click.echo(f"task:show:created:{task.created_at.isoformat()}")
        click.echo(f"task:show:updated:{task.updated_at.isoformat()}")
        
        if task.due_date:
            click.echo(f"task:show:due:{task.due_date.isoformat()}")
        
        if task.assigned_to:
            click.echo(f"task:show:assigned:{task.assigned_to}")
        
        if task.tags:
            click.echo(f"task:show:tags:{':'.join(task.tags)}")
        
        click.echo(f"task:show:complexity:{task.metrics.complexity_score:.1f}")
        click.echo(f"task:show:estimated_duration:{task.metrics.estimated_duration}min")
        click.echo(f"task:show:progress:{task.metrics.progress_percentage:.1f}%")
        
        if task.metrics.quality_score:
            click.echo(f"task:show:quality:{task.metrics.quality_score:.1f}")
        
        click.echo(f"task:show:scopes:{':'.join(task.context.scopes)}")
        
        if task.subtasks:
            click.echo(f"task:show:subtasks:{len(task.subtasks)}")
            for subtask_id in task.subtasks:
                subtask = manager.get_task(subtask_id)
                if subtask:
                    click.echo(f"task:show:subtask:{subtask_id[:8]}:{subtask.title}:{subtask.status.value}")


@task.command()
@scoped_command(['memory'])
@validate_scope
def dashboard():
    """Show task management dashboard."""
    manager = TaskManager()
    dashboard_data = manager.get_dashboard_data()
    
    click.echo("=== Task Management Dashboard ===")
    click.echo(f"task:dashboard:total:{dashboard_data['total_tasks']}")
    click.echo(f"task:dashboard:productivity:{dashboard_data['productivity_score']:.1f}/10")
    click.echo(f"task:dashboard:avg_completion:{dashboard_data['avg_completion_time_minutes']:.0f}min")
    
    click.echo("\nStatus Distribution:")
    for status, count in dashboard_data['status_distribution'].items():
        click.echo(f"task:dashboard:status:{status}:{count}")
    
    click.echo("\nType Distribution:")
    for task_type, count in dashboard_data['type_distribution'].items():
        click.echo(f"task:dashboard:type:{task_type}:{count}")
    
    click.echo("\nPriority Distribution:")
    for priority, count in dashboard_data['priority_distribution'].items():
        click.echo(f"task:dashboard:priority:{priority}:{count}")
    
    if dashboard_data['overdue_tasks']:
        click.echo(f"\nOverdue Tasks: {len(dashboard_data['overdue_tasks'])}")
        for task_data in dashboard_data['overdue_tasks'][:5]:
            click.echo(f"task:dashboard:overdue:{task_data['id'][:8]}:{task_data['title']}")


@task.command()
@click.argument('task_id')
@click.option('--status', type=click.Choice(['pending', 'in_progress', 'blocked', 'completed', 'cancelled']))
@click.option('--priority', type=click.Choice(['low', 'medium', 'high', 'critical']))
@click.option('--assign', help='Assign to user/agent')
@click.option('--due', help='Due date (YYYY-MM-DD or relative)')
@click.option('--add-tag', help='Add tag')
@click.option('--remove-tag', help='Remove tag')
@scoped_command(['memory'])
@validate_scope
def update(task_id, status, priority, assign, due, add_tag, remove_tag):
    """Update task properties."""
    manager = TaskManager()
    
    task = manager.get_task(task_id)
    if not task:
        click.echo(f"task:error:not_found:{task_id}")
        return
    
    updates = {}
    
    if status:
        updates['status'] = TaskStatus(status)
    
    if priority:
        updates['priority'] = TaskPriority(priority)
    
    if assign:
        updates['assigned_to'] = assign
    
    if due:
        updates['due_date'] = _parse_due_date(due)
    
    # Handle tags
    if add_tag:
        new_tags = task.tags.copy()
        if add_tag not in new_tags:
            new_tags.append(add_tag)
        updates['tags'] = new_tags
    
    if remove_tag:
        new_tags = [tag for tag in task.tags if tag != remove_tag]
        updates['tags'] = new_tags
    
    if updates:
        updated_task = manager.update_task(task_id, **updates)
        click.echo(f"task:updated:{task_id}")
        
        for field, value in updates.items():
            click.echo(f"task:update:{field}:{value}")
    else:
        click.echo("task:update:no_changes")


def _parse_due_date(due_str: str) -> datetime:
    """Parse due date string."""
    try:
        # Try ISO format first
        return datetime.fromisoformat(due_str)
    except ValueError:
        pass
    
    # Try relative formats
    now = datetime.now()
    
    if due_str.endswith('d'):
        days = int(due_str[:-1])
        return now + timedelta(days=days)
    elif due_str.endswith('w'):
        weeks = int(due_str[:-1])
        return now + timedelta(weeks=weeks)
    elif due_str.endswith('h'):
        hours = int(due_str[:-1])
        return now + timedelta(hours=hours)
    
    raise ValueError(f"Invalid due date format: {due_str}")


def _task_to_dict(task: Task) -> dict:
    """Convert task to dictionary for JSON output."""
    from dataclasses import asdict
    
    task_dict = asdict(task)
    
    # Convert enums to strings
    task_dict['status'] = task.status.value
    task_dict['priority'] = task.priority.value
    task_dict['task_type'] = task.task_type.value
    
    return task_dict


# Register with main CLI
def register_task_commands(main_cli):
    """Register task commands with main CLI."""
    main_cli.add_command(task)