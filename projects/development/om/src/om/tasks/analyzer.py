"""Task analysis for semantic understanding and optimization."""

import re
from typing import Dict, List, Tuple
from .models import TaskType


class TaskAnalyzer:
    """Analyzes tasks for semantic understanding and optimization."""
    
    def __init__(self):
        self.task_patterns = {
            TaskType.DOCUMENTATION: [
                r'document|doc|write.*guide|create.*reference',
                r'generate.*docs|sphinx|api.*doc',
                r'readme|changelog|tutorial'
            ],
            TaskType.ANALYSIS: [
                r'analyze|examine|investigate|review',
                r'audit|assess|evaluate|study',
                r'architecture|dependency|performance'
            ],
            TaskType.IMPLEMENTATION: [
                r'implement|develop|create|build',
                r'add.*feature|new.*functionality',
                r'code|program|write.*function'
            ],
            TaskType.TESTING: [
                r'test|verify|validate|check',
                r'unit.*test|integration.*test',
                r'coverage|quality.*assurance'
            ],
            TaskType.REFACTORING: [
                r'refactor|cleanup|optimize|improve',
                r'restructure|reorganize|simplify',
                r'performance|efficiency'
            ],
            TaskType.RESEARCH: [
                r'research|investigate|explore|study',
                r'prototype|experiment|poc',
                r'feasibility|options|alternatives'
            ],
            TaskType.MAINTENANCE: [
                r'fix|bug|issue|problem',
                r'update|upgrade|maintain',
                r'security|patch|hotfix'
            ]
        }
        
        self.complexity_indicators = {
            'high': [
                r'architecture|framework|system',
                r'integration|migration|refactor',
                r'performance|security|scalability'
            ],
            'medium': [
                r'feature|component|module',
                r'api|interface|service',
                r'database|storage|cache'
            ],
            'low': [
                r'fix|bug|typo|format',
                r'config|setting|parameter',
                r'documentation|comment|readme'
            ]
        }
        
        self.scope_mapping = {
            TaskType.DOCUMENTATION: ['docs'],
            TaskType.ANALYSIS: ['analysis'],
            TaskType.IMPLEMENTATION: ['code', 'parsing'],
            TaskType.TESTING: ['code'],
            TaskType.REFACTORING: ['code', 'analysis'],
            TaskType.RESEARCH: ['analysis'],
            TaskType.MAINTENANCE: ['code']
        }
    
    def analyze_task_description(self, description: str) -> Tuple[TaskType, float, List[str]]:
        """Analyze task description to determine type, complexity, and scopes."""
        description_lower = description.lower()
        
        # Determine task type
        task_type = self._determine_task_type(description_lower)
        
        # Calculate complexity
        complexity = self._calculate_complexity(description_lower)
        
        # Determine scopes
        scopes = self._determine_scopes(task_type, description_lower)
        
        return task_type, complexity, scopes
    
    def _determine_task_type(self, description: str) -> TaskType:
        """Determine task type from description."""
        type_scores = {}
        
        for task_type, patterns in self.task_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, description, re.IGNORECASE))
                score += matches
            type_scores[task_type] = score
        
        # Return type with highest score, default to IMPLEMENTATION
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return TaskType.IMPLEMENTATION
    
    def _calculate_complexity(self, description: str) -> float:
        """Calculate task complexity score (0.0 - 10.0)."""
        complexity_score = 5.0  # Base complexity
        
        # Check for complexity indicators
        for level, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, description, re.IGNORECASE))
                if level == 'high':
                    complexity_score += matches * 2.0
                elif level == 'medium':
                    complexity_score += matches * 1.0
                elif level == 'low':
                    complexity_score -= matches * 0.5
        
        # Normalize to 0.0 - 10.0 range
        return max(0.0, min(10.0, complexity_score))
    
    def _determine_scopes(self, task_type: TaskType, description: str) -> List[str]:
        """Determine appropriate scopes for the task."""
        base_scopes = self.scope_mapping.get(task_type, ['code'])
        
        # Add specific scopes based on keywords
        additional_scopes = []
        
        if re.search(r'memory|session|preference', description):
            additional_scopes.append('memory')
        
        if re.search(r'docs|documentation|sphinx', description):
            additional_scopes.append('docs')
        
        if re.search(r'parse|ast|code.*analysis', description):
            additional_scopes.append('parsing')
        
        if re.search(r'cli|command|interface', description):
            additional_scopes.append('cli')
        
        # Combine and deduplicate
        all_scopes = list(set(base_scopes + additional_scopes))
        return all_scopes
    
    def estimate_effort(self, task_type: TaskType, complexity: float, description: str) -> int:
        """Estimate effort points for the task."""
        base_effort = {
            TaskType.DOCUMENTATION: 2,
            TaskType.ANALYSIS: 3,
            TaskType.IMPLEMENTATION: 5,
            TaskType.TESTING: 3,
            TaskType.REFACTORING: 4,
            TaskType.RESEARCH: 2,
            TaskType.MAINTENANCE: 2
        }
        
        effort = base_effort.get(task_type, 3)
        
        # Adjust based on complexity
        if complexity >= 8.0:
            effort *= 3
        elif complexity >= 6.0:
            effort *= 2
        elif complexity <= 2.0:
            effort = max(1, effort // 2)
        
        return effort
    
    def suggest_dependencies(self, description: str) -> List[str]:
        """Suggest task dependencies based on description."""
        dependencies = []
        
        if re.search(r'test|testing', description):
            dependencies.append('implementation_complete')
        
        if re.search(r'document|docs', description):
            dependencies.append('implementation_complete')
        
        if re.search(r'deploy|release', description):
            dependencies.extend(['testing_complete', 'documentation_complete'])
        
        if re.search(r'refactor|optimize', description):
            dependencies.append('analysis_complete')
        
        return dependencies
    
    def extract_file_patterns(self, description: str) -> List[str]:
        """Extract file patterns that might be relevant to the task."""
        patterns = []
        
        # Look for specific file mentions
        file_matches = re.findall(r'(\w+\.\w+)', description)
        patterns.extend(file_matches)
        
        # Look for directory mentions
        dir_matches = re.findall(r'(\w+/)', description)
        patterns.extend(dir_matches)
        
        # Add common patterns based on task type
        if re.search(r'test|testing', description):
            patterns.extend(['test_*.py', '*_test.py'])
        
        if re.search(r'docs|documentation', description):
            patterns.extend(['*.md', '*.rst', 'docs/**'])
        
        if re.search(r'config|configuration', description):
            patterns.extend(['*.toml', '*.yaml', '*.json', '*.ini'])
        
        return list(set(patterns))