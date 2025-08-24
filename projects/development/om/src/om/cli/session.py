"""Session management commands."""

import click
from .utils import _check_memory


@click.group()
def session():
    """Session management commands."""
    pass


@session.command()
@click.argument('project_id')
@click.option('--module', '-m', help='Specific module to save')
def save(project_id, module):
    """Save current session state."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.session_manager import SessionManager
        manager = SessionManager()
        
        # Create context data from current workspace state
        import os
        import json
        context_data = {
            "current_task": f"session_save_{project_id}",
            "active_files": [],
            "decision_history": [],
            "module_context": {"module": module} if module else {},
            "workspace_path": os.getcwd()
        }
        
        session_id = manager.store_session_context(project_id, context_data, module)
        result = {
            "session_id": session_id,
            "modules_saved": 1 if module else 0,
            "size_mb": 0.1  # Estimate
        }
        manager.close()
        
        click.echo(f"session_saved:{project_id}:{result['session_id']} "
                  f"modules:{result['modules_saved']} "
                  f"size:{result['size_mb']:.1f}MB")
        
    except Exception as e:
        click.echo(f"error:save_failed:{e}")


@session.command()
@click.argument('project_id')
@click.option('--module', '-m', help='Specific module to restore')
def restore(project_id, module):
    """Restore session state."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.session_manager import SessionManager
        manager = SessionManager()
        
        result = manager.restore_session_context(project_id, module)
        
        # Transform result to match expected format
        if result.get("status") == "restored":
            result.update({
                "modules_restored": 1 if module else 0,
                "timestamp": result.get("created_at", "unknown")
            })
        manager.close()
        
        click.echo(f"session_restored:{project_id}:{result['session_id']} "
                  f"modules:{result['modules_restored']} "
                  f"timestamp:{result['timestamp']}")
        
    except Exception as e:
        click.echo(f"error:restore_failed:{e}")


@session.command()
def list():
    """List saved sessions."""
    if not _check_memory():
        click.echo("error:memory_not_available")
        return
    
    try:
        from om.session_manager import SessionManager
        manager = SessionManager()
        
        sessions = manager.list_active_sessions()
        
        # Transform to expected format
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                "project_id": session["project_id"],
                "session_id": session["key"],
                "module_count": 1 if session["module_name"] else 0,
                "created": session["last_accessed"],
                "size_mb": 0.1  # Estimate
            })
        sessions = formatted_sessions
        manager.close()
        
        if not sessions:
            click.echo("sessions:none")
            return
        
        for session in sessions:
            click.echo(f"session:{session['project_id']}:{session['session_id']} "
                      f"modules:{session['module_count']} "
                      f"created:{session['created']} "
                      f"size:{session['size_mb']:.1f}MB")
        
    except Exception as e:
        click.echo(f"error:list_failed:{e}")