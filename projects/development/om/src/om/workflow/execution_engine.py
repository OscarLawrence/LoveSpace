"""
Workflow execution engine
"""

import json
from typing import Dict, List, Any, Optional

from ..task_management import TaskManager, Task, TaskType, TaskPriority
from ..agent_scoping import ScopeManager, create_scope_context
from .data_models import Workflow


class WorkflowExecutionEngine:
    """Executes workflow steps and manages workflow state"""
    
    def __init__(self, task_manager: TaskManager, scope_manager: ScopeManager):
        self.task_manager = task_manager
        self.scope_manager = scope_manager
    
    def create_workflow_task(self, workflow: Workflow, title: str, 
                           variables: Dict[str, Any] = None) -> Task:
        """Create a task that executes a workflow."""
        # Create main workflow task
        workflow_task = self.task_manager.create_task(
            title=title,
            description=f"Execute workflow: {workflow.description}",
            task_type=TaskType.IMPLEMENTATION,
            priority=TaskPriority.MEDIUM
        )
        
        # Create subtasks for each workflow step
        step_tasks = []
        for step in workflow.steps:
            step_title = f"{title} - {step.name}"
            step_description = step.description
            
            # Substitute variables in command
            command = step.command
            if variables:
                for var, value in variables.items():
                    command = command.replace(f"{{{var}}}", str(value))
            
            step_task = self.task_manager.create_subtask(
                parent_id=workflow_task.id,
                title=step_title,
                description=f"{step_description}\nCommand: {command}"
            )
            
            # Set step-specific context
            step_task.context.scopes = step.scopes
            step_task.notes.append(f"workflow_step:{step.name}")
            step_task.notes.append(f"command:{command}")
            step_task.notes.append(f"dependencies:{','.join(step.dependencies)}")
            
            step_tasks.append(step_task)
        
        # Update main task with subtask references
        workflow_task.subtasks = [task.id for task in step_tasks]
        workflow_task.notes.append(f"workflow_id:{workflow.id}")
        if variables:
            workflow_task.notes.append(f"variables:{json.dumps(variables)}")
        
        self.task_manager._save_tasks()
        
        return workflow_task
    
    def execute_workflow_step(self, task_id: str) -> bool:
        """Execute a single workflow step."""
        task = self.task_manager.get_task(task_id)
        if not task:
            return False
        
        # Extract command from task notes
        command = None
        for note in task.notes:
            if note.startswith("command:"):
                command = note[8:]  # Remove "command:" prefix
                break
        
        if not command:
            return False
        
        # Set appropriate scope
        if task.context.scopes:
            context = create_scope_context(
                command=command,
                task=task.description
            )
            self.scope_manager.update_scope(context, force_scopes=task.context.scopes)
        
        # Start the task
        self.task_manager.start_task(task_id)
        
        # For now, mark as completed (in real implementation, would execute command)
        # This is a framework for command execution
        self.task_manager.complete_task(task_id, quality_score=8.0)
        
        return True
    
    def can_execute_step(self, task_id: str) -> bool:
        """Check if a workflow step can be executed (dependencies met)."""
        task = self.task_manager.get_task(task_id)
        if not task or not task.parent_task:
            return False
        
        # Get dependencies from task notes
        dependencies = []
        for note in task.notes:
            if note.startswith("dependencies:"):
                dep_str = note[13:]  # Remove "dependencies:" prefix
                if dep_str:
                    dependencies = dep_str.split(",")
                break
        
        if not dependencies:
            return True  # No dependencies
        
        # Check if all dependencies are completed
        parent_task = self.task_manager.get_task(task.parent_task)
        if not parent_task:
            return False
        
        for dep_step_name in dependencies:
            dep_completed = False
            for subtask_id in parent_task.subtasks:
                subtask = self.task_manager.get_task(subtask_id)
                if subtask and f"workflow_step:{dep_step_name}" in subtask.notes:
                    if subtask.status.name == "COMPLETED":
                        dep_completed = True
                    break
            
            if not dep_completed:
                return False
        
        return True
    
    def get_next_workflow_steps(self, workflow_task_id: str) -> List[Task]:
        """Get the next workflow steps that can be executed."""
        workflow_task = self.task_manager.get_task(workflow_task_id)
        if not workflow_task:
            return []
        
        next_steps = []
        for subtask_id in workflow_task.subtasks:
            subtask = self.task_manager.get_task(subtask_id)
            if (subtask and 
                subtask.status.name in ["CREATED", "BLOCKED"] and
                self.can_execute_step(subtask_id)):
                next_steps.append(subtask)
        
        return next_steps
    
    def auto_execute_workflow(self, workflow_task_id: str) -> Dict[str, Any]:
        """Automatically execute all ready workflow steps."""
        results = {
            "executed_steps": [],
            "blocked_steps": [],
            "completed": False,
            "errors": []
        }
        
        max_iterations = 20  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            next_steps = self.get_next_workflow_steps(workflow_task_id)
            
            if not next_steps:
                # Check if workflow is complete
                workflow_task = self.task_manager.get_task(workflow_task_id)
                if workflow_task:
                    all_completed = True
                    for subtask_id in workflow_task.subtasks:
                        subtask = self.task_manager.get_task(subtask_id)
                        if subtask and subtask.status.name != "COMPLETED":
                            all_completed = False
                            results["blocked_steps"].append({
                                "task_id": subtask_id,
                                "title": subtask.title,
                                "status": subtask.status.name
                            })
                    
                    if all_completed:
                        results["completed"] = True
                        self.task_manager.complete_task(workflow_task_id)
                
                break
            
            # Execute ready steps
            for step_task in next_steps:
                try:
                    success = self.execute_workflow_step(step_task.id)
                    if success:
                        results["executed_steps"].append({
                            "task_id": step_task.id,
                            "title": step_task.title
                        })
                    else:
                        results["errors"].append(f"Failed to execute step: {step_task.title}")
                except Exception as e:
                    results["errors"].append(f"Error executing {step_task.title}: {e}")
            
            iteration += 1
        
        return results
