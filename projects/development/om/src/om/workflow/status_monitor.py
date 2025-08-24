"""
Workflow status monitoring
"""

from typing import Dict, List, Any

from ..task_management import TaskManager, TaskStatus


class WorkflowStatusMonitor:
    """Monitors and reports workflow execution status"""
    
    def __init__(self, task_manager: TaskManager, execution_engine):
        self.task_manager = task_manager
        self.execution_engine = execution_engine
    
    def get_workflow_status(self, workflow_task_id: str) -> Dict[str, Any]:
        """Get detailed status of workflow execution."""
        workflow_task = self.task_manager.get_task(workflow_task_id)
        if not workflow_task:
            return {}
        
        status = {
            'workflow_id': workflow_task_id,
            'title': workflow_task.title,
            'status': workflow_task.status.value,
            'progress': workflow_task.metrics.progress_percentage,
            'steps': [],
            'next_steps': [],
            'blocked_steps': []
        }
        
        # Analyze each step
        for subtask_id in workflow_task.subtasks:
            subtask = self.task_manager.get_task(subtask_id)
            if not subtask:
                continue
            
            step_info = {
                'id': subtask.id,
                'name': subtask.title,
                'status': subtask.status.value,
                'can_execute': self.execution_engine.can_execute_step(subtask.id)
            }
            
            status['steps'].append(step_info)
            
            if subtask.status == TaskStatus.PENDING:
                if step_info['can_execute']:
                    status['next_steps'].append(step_info)
                else:
                    status['blocked_steps'].append(step_info)
        
        return status
    
    def get_workflow_summary(self, workflow_task_id: str) -> Dict[str, Any]:
        """Get a summary of workflow progress."""
        status = self.get_workflow_status(workflow_task_id)
        
        if not status:
            return {}
        
        total_steps = len(status['steps'])
        completed_steps = len([s for s in status['steps'] if s['status'] == 'COMPLETED'])
        next_steps = len(status['next_steps'])
        blocked_steps = len(status['blocked_steps'])
        
        return {
            'workflow_id': workflow_task_id,
            'title': status['title'],
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'next_steps': next_steps,
            'blocked_steps': blocked_steps,
            'progress_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'is_complete': completed_steps == total_steps,
            'can_continue': next_steps > 0
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflow executions."""
        active_workflows = []
        
        # Find all workflow tasks
        for task in self.task_manager.tasks.values():
            # Check if this is a workflow task (has workflow_id in notes)
            is_workflow = any(note.startswith('workflow_id:') for note in task.notes)
            
            if is_workflow and task.status != TaskStatus.COMPLETED:
                summary = self.get_workflow_summary(task.id)
                if summary:
                    active_workflows.append(summary)
        
        return active_workflows
