"""
Main workflow engine using modular components
"""

from typing import Dict, List, Any

from ..task_management import TaskManager, Task
from ..agent_scoping import ScopeManager
from .data_models import Workflow
from .templates import WorkflowTemplates
from .execution_engine import WorkflowExecutionEngine
from .status_monitor import WorkflowStatusMonitor


class WorkflowEngine:
    """Executes automated workflows for agent task management."""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.scope_manager = ScopeManager()
        self.workflows: Dict[str, Workflow] = {}
        self.active_executions: Dict[str, Dict] = {}
        
        # Components
        self.execution_engine = WorkflowExecutionEngine(task_manager, self.scope_manager)
        self.status_monitor = WorkflowStatusMonitor(task_manager, self.execution_engine)
        
        # Register built-in workflows
        self._register_builtin_workflows()
    
    def _register_builtin_workflows(self):
        """Register built-in workflow templates."""
        # Documentation workflow
        doc_workflow = WorkflowTemplates.create_documentation_workflow()
        self.workflows[doc_workflow.id] = doc_workflow
        
        # Quality workflow
        quality_workflow = WorkflowTemplates.create_quality_workflow()
        self.workflows[quality_workflow.id] = quality_workflow
    
    def register_workflow(self, workflow: Workflow):
        """Register a custom workflow."""
        self.workflows[workflow.id] = workflow
    
    def create_workflow_task(self, workflow_id: str, title: str, 
                           variables: Dict[str, Any] = None) -> Task:
        """Create a task that executes a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        return self.execution_engine.create_workflow_task(workflow, title, variables)
    
    def execute_workflow_step(self, task_id: str) -> bool:
        """Execute a single workflow step."""
        return self.execution_engine.execute_workflow_step(task_id)
    
    def can_execute_step(self, task_id: str) -> bool:
        """Check if a workflow step can be executed (dependencies met)."""
        return self.execution_engine.can_execute_step(task_id)
    
    def get_next_workflow_steps(self, workflow_task_id: str) -> List[Task]:
        """Get the next workflow steps that can be executed."""
        return self.execution_engine.get_next_workflow_steps(workflow_task_id)
    
    def auto_execute_workflow(self, workflow_task_id: str) -> Dict[str, Any]:
        """Automatically execute all ready workflow steps."""
        return self.execution_engine.auto_execute_workflow(workflow_task_id)
    
    def get_workflow_status(self, workflow_task_id: str) -> Dict[str, Any]:
        """Get detailed status of workflow execution."""
        return self.status_monitor.get_workflow_status(workflow_task_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflow templates."""
        return [
            {
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'step_count': len(workflow.steps),
                'triggers': workflow.triggers
            }
            for workflow in self.workflows.values()
        ]
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflow executions."""
        return self.status_monitor.list_active_workflows()
