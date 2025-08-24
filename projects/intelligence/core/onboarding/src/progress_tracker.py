"""Progress tracking for agent onboarding - 200 LOC max"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import json


@dataclass
class ProgressStep:
    """Individual progress step"""
    step_id: str
    name: str
    description: str
    completed: bool = False
    completion_time: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    validation_score: float = 0.0


@dataclass
class OnboardingProgress:
    """Overall onboarding progress"""
    agent_id: str
    start_time: str
    steps: Dict[str, ProgressStep] = field(default_factory=dict)
    current_step: Optional[str] = None
    completion_percentage: float = 0.0
    is_complete: bool = False


class ProgressTracker:
    """Tracks agent onboarding progress"""
    
    def __init__(self):
        self.progress_file = "onboarding_progress.json"
        self.required_steps = {
            'workspace_exploration': ProgressStep(
                step_id='workspace_exploration',
                name='Workspace Exploration',
                description='Learn workspace structure and navigation',
                requirements=['understand_directory_structure', 'locate_key_files']
            ),
            'command_training': ProgressStep(
                step_id='command_training',
                name='OM Command Training',
                description='Master OM system commands',
                requirements=['basic_commands', 'advanced_operations']
            ),
            'constraint_learning': ProgressStep(
                step_id='constraint_learning',
                name='Constraint Understanding',
                description='Learn file size and architectural constraints',
                requirements=['200_line_limit', 'module_boundaries']
            ),
            'validation_system': ProgressStep(
                step_id='validation_system',
                name='Validation System Training',
                description='Understand logical coherence validation',
                requirements=['contradiction_detection', 'context_validation']
            ),
            'collaboration_principles': ProgressStep(
                step_id='collaboration_principles',
                name='Collaboration Principles',
                description='Learn agent collaboration patterns',
                requirements=['handoff_protocols', 'communication_standards']
            )
        }
    
    def start_onboarding(self, agent_id: str) -> OnboardingProgress:
        """Start onboarding process for agent"""
        
        progress = OnboardingProgress(
            agent_id=agent_id,
            start_time=datetime.now().isoformat(),
            steps=self.required_steps.copy(),
            current_step=list(self.required_steps.keys())[0]
        )
        
        self._save_progress(progress)
        return progress
    
    def complete_step(self, agent_id: str, step_id: str, validation_score: float = 1.0) -> bool:
        """Mark step as completed"""
        
        progress = self.load_progress(agent_id)
        if not progress or step_id not in progress.steps:
            return False
        
        step = progress.steps[step_id]
        step.completed = True
        step.completion_time = datetime.now().isoformat()
        step.validation_score = validation_score
        
        # Update overall progress
        self._update_progress_metrics(progress)
        
        # Move to next step
        self._advance_to_next_step(progress)
        
        self._save_progress(progress)
        return True
    
    def get_current_step(self, agent_id: str) -> Optional[ProgressStep]:
        """Get current step for agent"""
        
        progress = self.load_progress(agent_id)
        if not progress or not progress.current_step:
            return None
        
        return progress.steps.get(progress.current_step)
    
    def get_next_requirements(self, agent_id: str) -> List[str]:
        """Get requirements for current step"""
        
        current_step = self.get_current_step(agent_id)
        if not current_step:
            return []
        
        return current_step.requirements
    
    def validate_step_completion(self, agent_id: str, step_id: str) -> float:
        """Validate if step can be marked complete"""
        
        progress = self.load_progress(agent_id)
        if not progress or step_id not in progress.steps:
            return 0.0
        
        step = progress.steps[step_id]
        
        # Check if previous steps are complete
        step_order = list(self.required_steps.keys())
        current_index = step_order.index(step_id)
        
        for i in range(current_index):
            prev_step_id = step_order[i]
            if not progress.steps[prev_step_id].completed:
                return 0.0  # Prerequisites not met
        
        # Validate specific step requirements
        validation_score = self._validate_step_requirements(step_id, agent_id)
        
        return validation_score
    
    def load_progress(self, agent_id: str) -> Optional[OnboardingProgress]:
        """Load progress from storage"""
        
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                
            agent_data = data.get(agent_id)
            if not agent_data:
                return None
            
            # Reconstruct progress object
            progress = OnboardingProgress(
                agent_id=agent_id,
                start_time=agent_data['start_time'],
                current_step=agent_data.get('current_step'),
                completion_percentage=agent_data.get('completion_percentage', 0.0),
                is_complete=agent_data.get('is_complete', False)
            )
            
            # Reconstruct steps
            for step_id, step_data in agent_data.get('steps', {}).items():
                progress.steps[step_id] = ProgressStep(
                    step_id=step_data['step_id'],
                    name=step_data['name'],
                    description=step_data['description'],
                    completed=step_data.get('completed', False),
                    completion_time=step_data.get('completion_time'),
                    requirements=step_data.get('requirements', []),
                    validation_score=step_data.get('validation_score', 0.0)
                )
            
            return progress
            
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_progress(self, progress: OnboardingProgress) -> None:
        """Save progress to storage"""
        
        try:
            # Load existing data
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
            
            # Convert progress to dict
            steps_data = {}
            for step_id, step in progress.steps.items():
                steps_data[step_id] = {
                    'step_id': step.step_id,
                    'name': step.name,
                    'description': step.description,
                    'completed': step.completed,
                    'completion_time': step.completion_time,
                    'requirements': step.requirements,
                    'validation_score': step.validation_score
                }
            
            data[progress.agent_id] = {
                'start_time': progress.start_time,
                'current_step': progress.current_step,
                'completion_percentage': progress.completion_percentage,
                'is_complete': progress.is_complete,
                'steps': steps_data
            }
            
            # Save back to file
            with open(self.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save progress: {e}")
    
    def _update_progress_metrics(self, progress: OnboardingProgress) -> None:
        """Update completion percentage and overall status"""
        
        total_steps = len(progress.steps)
        completed_steps = sum(1 for step in progress.steps.values() if step.completed)
        
        progress.completion_percentage = completed_steps / total_steps if total_steps > 0 else 0
        progress.is_complete = completed_steps == total_steps
    
    def _advance_to_next_step(self, progress: OnboardingProgress) -> None:
        """Advance to next uncompleted step"""
        
        step_order = list(self.required_steps.keys())
        
        for step_id in step_order:
            if not progress.steps[step_id].completed:
                progress.current_step = step_id
                return
        
        # All steps complete
        progress.current_step = None
    
    def _validate_step_requirements(self, step_id: str, agent_id: str) -> float:
        """Validate specific step requirements"""
        
        # Simplified validation - can be enhanced with actual checks
        validation_map = {
            'workspace_exploration': 0.8,
            'command_training': 0.9,
            'constraint_learning': 0.85,
            'validation_system': 0.75,
            'collaboration_principles': 0.8
        }
        
        return validation_map.get(step_id, 0.5)
