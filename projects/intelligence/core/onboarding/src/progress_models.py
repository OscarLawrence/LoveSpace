"""Progress data models - under 200 LOC"""

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


class ProgressStepFactory:
    """Factory for creating standard progress steps"""
    
    @staticmethod
    def create_standard_steps() -> Dict[str, ProgressStep]:
        """Create standard onboarding steps"""
        
        return {
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
                requirements=['hybrid_limits', 'module_boundaries']
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


class ProgressMetrics:
    """Calculate progress metrics"""
    
    @staticmethod
    def calculate_completion_percentage(steps: Dict[str, ProgressStep]) -> float:
        """Calculate completion percentage"""
        if not steps:
            return 0.0
        
        completed = sum(1 for step in steps.values() if step.completed)
        return completed / len(steps)
    
    @staticmethod
    def is_complete(steps: Dict[str, ProgressStep]) -> bool:
        """Check if all steps are complete"""
        return all(step.completed for step in steps.values())
    
    @staticmethod
    def get_next_step(steps: Dict[str, ProgressStep], step_order: List[str]) -> Optional[str]:
        """Get next uncompleted step"""
        for step_id in step_order:
            if step_id in steps and not steps[step_id].completed:
                return step_id
        return None
    
    @staticmethod
    def validate_prerequisites(step_id: str, steps: Dict[str, ProgressStep], 
                             step_order: List[str]) -> bool:
        """Validate step prerequisites are met"""
        if step_id not in step_order:
            return False
        
        current_index = step_order.index(step_id)
        
        for i in range(current_index):
            prev_step_id = step_order[i]
            if prev_step_id in steps and not steps[prev_step_id].completed:
                return False
        
        return True


class ProgressStorage:
    """Handle progress data persistence"""
    
    def __init__(self, storage_file: str = "onboarding_progress.json"):
        self.storage_file = storage_file
    
    def save_progress(self, progress: OnboardingProgress) -> bool:
        """Save progress to storage"""
        try:
            # Load existing data
            data = self.load_all_progress()
            
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
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save progress: {e}")
            return False
    
    def load_progress(self, agent_id: str) -> Optional[OnboardingProgress]:
        """Load progress for specific agent"""
        try:
            data = self.load_all_progress()
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
            
        except Exception:
            return None
    
    def load_all_progress(self) -> Dict:
        """Load all progress data"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
