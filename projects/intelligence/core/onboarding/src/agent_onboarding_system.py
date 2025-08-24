"""
Agent Onboarding System

Main onboarding orchestrator that guides new agents through workspace setup,
command training, and constraint understanding.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OnboardingProgress:
    """Tracks agent onboarding progress."""
    agent_id: str
    current_stage: str
    completed_stages: List[str]
    progress_percent: float
    start_time: str
    estimated_completion: str
    issues_encountered: List[str]


class AgentOnboardingSystem:
    """
    Comprehensive agent onboarding system.
    
    Features:
    - Progressive workspace introduction
    - Interactive command training
    - Constraint validation learning
    - Progress tracking
    - Competency assessment
    """
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.onboarding_stages = self._define_onboarding_stages()
        self.progress_tracker = {}
        
    def start_onboarding(self, agent_id: str) -> OnboardingProgress:
        """Start onboarding process for new agent."""
        progress = OnboardingProgress(
            agent_id=agent_id,
            current_stage="workspace_orientation",
            completed_stages=[],
            progress_percent=0.0,
            start_time=datetime.now().isoformat(),
            estimated_completion=self._estimate_completion_time(),
            issues_encountered=[]
        )
        
        self.progress_tracker[agent_id] = progress
        self._save_progress(progress)
        
        return progress
    
    def get_next_training_module(self, agent_id: str) -> Optional[Dict]:
        """Get next training module for agent."""
        progress = self.progress_tracker.get(agent_id)
        if not progress:
            return None
            
        current_stage = progress.current_stage
        stage_config = self.onboarding_stages.get(current_stage)
        
        if not stage_config:
            return None
            
        return {
            'stage': current_stage,
            'title': stage_config['title'],
            'description': stage_config['description'],
            'tasks': stage_config['tasks'],
            'resources': stage_config['resources'],
            'validation_criteria': stage_config['validation_criteria']
        }
    
    def complete_training_module(self, agent_id: str, module_results: Dict) -> bool:
        """Mark training module as complete and advance."""
        progress = self.progress_tracker.get(agent_id)
        if not progress:
            return False
            
        # Validate completion criteria
        if not self._validate_module_completion(progress.current_stage, module_results):
            progress.issues_encountered.append(f"Failed validation for {progress.current_stage}")
            return False
        
        # Mark stage as complete
        progress.completed_stages.append(progress.current_stage)
        
        # Advance to next stage
        next_stage = self._get_next_stage(progress.current_stage)
        if next_stage:
            progress.current_stage = next_stage
        else:
            progress.current_stage = "completed"
            
        # Update progress percentage
        progress.progress_percent = (len(progress.completed_stages) / len(self.onboarding_stages)) * 100
        
        self._save_progress(progress)
        return True
    
    def get_onboarding_status(self, agent_id: str) -> Optional[OnboardingProgress]:
        """Get current onboarding status."""
        return self.progress_tracker.get(agent_id)
    
    def generate_onboarding_report(self, agent_id: str) -> Dict:
        """Generate comprehensive onboarding report."""
        progress = self.progress_tracker.get(agent_id)
        if not progress:
            return {"error": "Agent not found"}
            
        return {
            'agent_id': agent_id,
            'progress': progress.__dict__,
            'competency_assessment': self._assess_competency(agent_id),
            'recommendations': self._generate_recommendations(progress),
            'next_steps': self._get_next_steps(progress)
        }
    
    def _define_onboarding_stages(self) -> Dict[str, Dict]:
        """Define the onboarding stages and their requirements."""
        return {
            'workspace_orientation': {
                'title': 'Workspace Orientation',
                'description': 'Learn workspace structure and navigation',
                'tasks': [
                    'Explore directory structure',
                    'Identify key project modules',
                    'Understand file organization'
                ],
                'resources': ['workspace_map.json', 'directory_guide.md'],
                'validation_criteria': {
                    'can_navigate_workspace': True,
                    'understands_module_structure': True
                }
            },
            'om_command_training': {
                'title': 'OM Command Training',
                'description': 'Master OM command system usage',
                'tasks': [
                    'Learn basic OM commands',
                    'Practice workspace analysis',
                    'Execute code operations'
                ],
                'resources': ['om_command_reference.md', 'command_examples.json'],
                'validation_criteria': {
                    'can_use_basic_commands': True,
                    'understands_command_syntax': True,
                    'can_analyze_workspace': True
                }
            },
            'constraint_understanding': {
                'title': 'Constraint Understanding', 
                'description': 'Learn CLU and quality constraints',
                'tasks': [
                    'Understand 200-line file limit',
                    'Learn collaboration principles',
                    'Practice constraint validation'
                ],
                'resources': ['clu_guide.md', 'constraint_examples.json'],
                'validation_criteria': {
                    'respects_file_size_limits': True,
                    'follows_collaboration_principles': True
                }
            },
            'quality_standards': {
                'title': 'Quality Standards',
                'description': 'Learn code quality and documentation standards',
                'tasks': [
                    'Review coding standards',
                    'Practice documentation',
                    'Understand testing requirements'
                ],
                'resources': ['quality_guide.md', 'style_examples.py'],
                'validation_criteria': {
                    'writes_quality_code': True,
                    'documents_appropriately': True
                }
            },
            'practical_exercises': {
                'title': 'Practical Exercises',
                'description': 'Complete hands-on coding exercises',
                'tasks': [
                    'Implement small feature',
                    'Refactor existing code',
                    'Write comprehensive tests'
                ],
                'resources': ['exercise_prompts.md', 'solution_templates/'],
                'validation_criteria': {
                    'completes_exercises_correctly': True,
                    'follows_best_practices': True
                }
            }
        }
    
    def _estimate_completion_time(self) -> str:
        """Estimate completion time based on stage complexity."""
        # Rough estimate: 1 hour total
        estimated_hours = len(self.onboarding_stages) * 0.2
        completion_time = datetime.now()
        # Add estimated hours (simplified)
        return completion_time.isoformat()
    
    def _validate_module_completion(self, stage: str, results: Dict) -> bool:
        """Validate that module completion criteria are met."""
        stage_config = self.onboarding_stages.get(stage)
        if not stage_config:
            return False
            
        criteria = stage_config['validation_criteria']
        
        # Check each criterion
        for criterion, required_value in criteria.items():
            if results.get(criterion) != required_value:
                return False
                
        return True
    
    def _get_next_stage(self, current_stage: str) -> Optional[str]:
        """Get the next stage in the onboarding sequence."""
        stages = list(self.onboarding_stages.keys())
        try:
            current_index = stages.index(current_stage)
            if current_index + 1 < len(stages):
                return stages[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _assess_competency(self, agent_id: str) -> Dict:
        """Assess agent competency based on onboarding performance."""
        progress = self.progress_tracker.get(agent_id)
        if not progress:
            return {}
            
        competency = {
            'overall_score': 0.0,
            'individual_scores': {},
            'strengths': [],
            'areas_for_improvement': []
        }
        
        # Calculate scores for each completed stage
        total_score = 0
        for stage in progress.completed_stages:
            # Simplified scoring - in practice would be more sophisticated
            stage_score = 1.0 if stage in progress.completed_stages else 0.0
            competency['individual_scores'][stage] = stage_score
            total_score += stage_score
        
        competency['overall_score'] = total_score / len(self.onboarding_stages)
        
        # Identify strengths and improvement areas
        if competency['overall_score'] > 0.8:
            competency['strengths'].append('Quick learner')
        if len(progress.issues_encountered) == 0:
            competency['strengths'].append('Error-free execution')
        if len(progress.issues_encountered) > 2:
            competency['areas_for_improvement'].append('Error handling')
            
        return competency
    
    def _generate_recommendations(self, progress: OnboardingProgress) -> List[str]:
        """Generate recommendations based on onboarding progress."""
        recommendations = []
        
        if progress.progress_percent < 50:
            recommendations.append("Continue with structured learning path")
        
        if len(progress.issues_encountered) > 1:
            recommendations.append("Review areas with difficulties")
            
        if progress.current_stage == "completed":
            recommendations.append("Begin supervised work assignments")
        
        return recommendations
    
    def _get_next_steps(self, progress: OnboardingProgress) -> List[str]:
        """Get recommended next steps."""
        if progress.current_stage == "completed":
            return [
                "Begin independent work assignments",
                "Schedule regular check-ins",
                "Gradual increase in responsibility"
            ]
        else:
            return [
                f"Complete {progress.current_stage} module",
                "Review any failed validation criteria",
                "Practice hands-on exercises"
            ]
    
    def _save_progress(self, progress: OnboardingProgress):
        """Save progress to persistent storage."""
        try:
            progress_file = os.path.join(self.workspace_root, f"onboarding_progress_{progress.agent_id}.json")
            with open(progress_file, 'w') as f:
                json.dump(progress.__dict__, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save onboarding progress: {e}")
    
    def load_progress(self, agent_id: str) -> Optional[OnboardingProgress]:
        """Load progress from persistent storage."""
        try:
            progress_file = os.path.join(self.workspace_root, f"onboarding_progress_{agent_id}.json")
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    progress = OnboardingProgress(**data)
                    self.progress_tracker[agent_id] = progress
                    return progress
        except Exception as e:
            print(f"Failed to load onboarding progress: {e}")
        return None
