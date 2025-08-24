"""
Logical Coherence Validator

Detects logical contradictions, inconsistencies, and coherence issues
in agent requests and responses. Uses pattern matching, semantic analysis,
and logical reasoning to identify problems before execution.
"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from .validation_models import CoherenceIssue, SeverityLevel


@dataclass
class CoherenceResult:
    score: float
    contradictions: List[str]
    impossibilities: List[str]
    is_coherent: bool


class LogicalCoherenceValidator:
    """
    Validates logical coherence in agent interactions.
    
    Detects:
    - Direct contradictions
    - Semantic inconsistencies  
    - Temporal inconsistencies
    - Scope violations
    - Context mismatches
    """
    
    def __init__(self):
        self.contradiction_patterns = self._load_contradiction_patterns()
        self.semantic_rules = self._load_semantic_rules()
        self.context_memory = {}
        
    def validate_request(self, request: str, context: Optional[Dict] = None) -> List[CoherenceIssue]:
        """Validate logical coherence of a request."""
        issues = []
        
        # Direct contradiction detection
        issues.extend(self._detect_direct_contradictions(request))
        
        # Semantic consistency check
        issues.extend(self._check_semantic_consistency(request))
        
        # Context coherence validation
        if context:
            issues.extend(self._validate_context_coherence(request, context))
            
        # Temporal consistency check
        issues.extend(self._check_temporal_consistency(request))
        
        # Scope boundary validation
        issues.extend(self._validate_scope_boundaries(request))
        
        return issues
    
    def _detect_direct_contradictions(self, text: str) -> List[CoherenceIssue]:
        """Detect direct logical contradictions in text."""
        issues = []
        
        # Negation contradictions (X and not X)
        negation_patterns = [
            (r'(\w+)\s+(?:is|are)\s+(\w+).*(?:is|are)\s+not\s+\2', 'Contradictory statements about {}'),
            (r'(?:implement|create|build)\s+(\w+).*(?:don\'t|do not|avoid)\s+\1', 'Contradictory implementation instructions'),
            (r'(?:use|enable)\s+(\w+).*(?:disable|remove|delete)\s+\1', 'Contradictory usage instructions')
        ]
        
        for pattern, message in negation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append(CoherenceIssue(
                    issue_type="direct_contradiction",
                    description=message.format(match.group(1) if '{}' in message else ''),
                    severity=SeverityLevel.HIGH,
                    location=f"Position {match.start()}-{match.end()}",
                    confidence=0.85
                ))
        
        return issues
    
    def _check_semantic_consistency(self, text: str) -> List[CoherenceIssue]:
        """Check for semantic inconsistencies."""
        return []  # Simplified for space
    
    def _validate_context_coherence(self, request: str, context: Dict) -> List[CoherenceIssue]:
        """Validate coherence with provided context."""
        return []  # Simplified for space
    
    def _check_temporal_consistency(self, text: str) -> List[CoherenceIssue]:
        """Check for temporal logical inconsistencies.""" 
        return []  # Simplified for space
    
    def _validate_scope_boundaries(self, text: str) -> List[CoherenceIssue]:
        """Validate scope boundary violations."""
        return []  # Simplified for space
    
    def _load_contradiction_patterns(self) -> List[Tuple[str, str]]:
        """Load patterns for detecting contradictions."""
        return [
            (r'(?:yes|true).*(?:no|false)', 'Boolean contradiction'),
            (r'(?:create|add).*(?:delete|remove)', 'Create/delete contradiction'),
            (r'(?:enable|start).*(?:disable|stop)', 'Enable/disable contradiction')
        ]
    
    def _load_semantic_rules(self) -> Dict[str, List[str]]:
        """Load semantic consistency rules."""
        return {
            'mutually_exclusive': [
                ['create', 'delete'],
                ['enable', 'disable'], 
                ['start', 'stop'],
                ['include', 'exclude']
            ]
        }
    
    def calculate_coherence_score(self, contradictions: List[str], impossibilities: List[str]) -> float:
        """Calculate 0-1 coherence score"""
        base_score = 1.0
        contradiction_penalty = len(contradictions) * 0.3
        impossibility_penalty = len(impossibilities) * 0.2
        
        return max(0.0, base_score - contradiction_penalty - impossibility_penalty)
    
    def detect_impossibilities(self, request: str, context: Dict) -> List[str]:
        """Detect resource conflicts and impossible operations"""
        impossibilities = []
        
        # Check file system conflicts
        if 'workspace_files' in context:
            impossibilities.extend(self._check_file_conflicts(request, context['workspace_files']))
        
        # Check dependency conflicts  
        if 'dependencies' in context:
            impossibilities.extend(self._check_dependency_conflicts(request, context['dependencies']))
            
        # Check resource availability
        impossibilities.extend(self._check_resource_availability(request))
        
        return impossibilities
    
    def _detect_contradictions(self, request: str) -> List[str]:
        """Find contradictory statements in request"""
        contradictions = []
        request_lower = request.lower()
        
        # Simple keyword-based contradiction detection
        if 'create' in request_lower and 'delete' in request_lower:
            if any(word in request_lower for word in ['file', 'directory', 'folder']):
                contradictions.append("Contradiction: create and delete operations on same target")
        
        if 'start' in request_lower and 'stop' in request_lower:
            contradictions.append("Contradiction: start and stop operations")
            
        if 'enable' in request_lower and 'disable' in request_lower:
            contradictions.append("Contradiction: enable and disable operations")
            
        if 'install' in request_lower and 'remove' in request_lower:
            contradictions.append("Contradiction: install and remove operations")
        
        return contradictions
    
    def _check_file_conflicts(self, request: str, workspace_files: Set[str]) -> List[str]:
        """Check for file operation conflicts"""
        conflicts = []
        
        # Extract file references from request
        file_refs = re.findall(r'(?:file|path):\s*([^\s,]+)', request, re.IGNORECASE)
        
        for file_ref in file_refs:
            if 'create' in request.lower() and file_ref in workspace_files:
                conflicts.append(f"Cannot create existing file: {file_ref}")
            elif 'delete' in request.lower() and file_ref not in workspace_files:
                conflicts.append(f"Cannot delete non-existent file: {file_ref}")
                
        return conflicts
    
    def _check_dependency_conflicts(self, request: str, dependencies: Dict) -> List[str]:
        """Check for dependency version conflicts"""
        conflicts = []
        
        # Extract package references
        package_refs = re.findall(r'(?:install|add|require)\s+([^\s,]+)', request, re.IGNORECASE)
        
        for package in package_refs:
            if package in dependencies:
                conflicts.append(f"Package {package} already installed with version {dependencies[package]}")
                
        return conflicts
    
    def _check_resource_availability(self, request: str) -> List[str]:
        """Check if required resources are available"""
        issues = []
        
        # Check for unrealistic operations
        if re.search(r'(?:process|analyze)\s+(?:millions?|billions?)', request, re.IGNORECASE):
            issues.append("Large-scale operation may exceed resource limits")
            
        if re.search(r'(?:simultaneous|parallel).*(?:\d{3,})', request, re.IGNORECASE):
            issues.append("High concurrency request may be impossible")
            
        return issues
