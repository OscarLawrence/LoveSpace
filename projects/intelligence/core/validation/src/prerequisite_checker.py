"""Context validation and prerequisite checking system"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PrerequisiteResult:
    missing_info: List[str]
    workspace_issues: List[str]
    success_probability: float
    recommendations: List[str]
    is_ready: bool


class PrerequisiteChecker:
    """Validates context completeness and workspace state"""
    
    def __init__(self):
        self.required_file_patterns = {
            'python_project': ['pyproject.toml', 'requirements.txt', '*.py'],
            'node_project': ['package.json', '*.js', '*.ts'],
            'generic_project': ['README.md', 'src/', 'tests/']
        }
        
        self.dependency_indicators = {
            'python': ['import ', 'from ', 'pip install', 'uv add'],
            'node': ['require(', 'import ', 'npm install', 'yarn add'],
            'system': ['apt install', 'brew install', 'pacman -S']
        }
    
    def check_context_completeness(self, request: str, context: Optional[Dict] = None) -> PrerequisiteResult:
        """Detect missing information needed for successful execution"""
        
        missing_info = []
        workspace_issues = []
        recommendations = []
        
        context = context or {}
        
        # Check for missing file references
        missing_info.extend(self._check_missing_file_references(request, context))
        
        # Check workspace state
        workspace_issues.extend(self._validate_workspace_structure(request))
        
        # Check dependency requirements
        missing_deps = self._check_missing_dependencies(request, context)
        missing_info.extend(missing_deps)
        
        # Check for ambiguous operations
        ambiguous_ops = self._detect_ambiguous_operations(request)
        missing_info.extend(ambiguous_ops)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing_info, workspace_issues)
        
        # Calculate success probability
        success_prob = self.estimate_success_probability(missing_info, workspace_issues)
        
        is_ready = len(missing_info) == 0 and len(workspace_issues) == 0 and success_prob > 0.7
        
        return PrerequisiteResult(
            missing_info=missing_info,
            workspace_issues=workspace_issues,
            success_probability=success_prob,
            recommendations=recommendations,
            is_ready=is_ready
        )
    
    def validate_workspace_state(self, request: str) -> List[str]:
        """Check file and dependency state in workspace"""
        
        issues = []
        
        # Check if workspace exists
        if not os.path.exists('.'):
            issues.append("Workspace directory not accessible")
            return issues
        
        # Detect project type
        project_type = self._detect_project_type()
        
        # Check for required files based on project type
        if project_type:
            missing_files = self._check_required_files(project_type)
            issues.extend(missing_files)
        
        # Check for broken imports/dependencies
        broken_deps = self._check_broken_dependencies(request)
        issues.extend(broken_deps)
        
        # Check for write permissions
        if any(op in request.lower() for op in ['create', 'write', 'save', 'generate']):
            if not os.access('.', os.W_OK):
                issues.append("No write permission in current directory")
        
        return issues
    
    def estimate_success_probability(self, missing_info: List[str], workspace_issues: List[str]) -> float:
        """Predict likelihood of successful execution"""
        
        base_probability = 1.0
        
        # Penalty for missing information
        info_penalty = len(missing_info) * 0.15
        
        # Penalty for workspace issues
        workspace_penalty = len(workspace_issues) * 0.2
        
        # Bonus for complete context
        if len(missing_info) == 0:
            base_probability += 0.1
        
        # Penalty for critical issues
        critical_issues = [
            'missing dependency',
            'file not found',
            'permission denied',
            'syntax error'
        ]
        
        for issue in missing_info + workspace_issues:
            if any(critical in issue.lower() for critical in critical_issues):
                base_probability -= 0.3
                break
        
        final_probability = max(0.0, min(1.0, base_probability - info_penalty - workspace_penalty))
        
        return final_probability
    
    def _check_missing_file_references(self, request: str, context: Dict) -> List[str]:
        """Check for file references that don't exist"""
        
        missing = []
        
        # Extract file paths from request
        import re
        file_patterns = [
            r'file[:\s]+([^\s,]+)',
            r'path[:\s]+([^\s,]+)',
            r'([/\w.-]+\.\w+)',  # File extensions
            r'in\s+([/\w.-]+)'   # "in directory" patterns
        ]
        
        referenced_files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, request, re.IGNORECASE)
            referenced_files.update(matches)
        
        # Check if files exist
        workspace_files = context.get('workspace_files', set())
        for file_ref in referenced_files:
            if file_ref and not any(file_ref in existing for existing in workspace_files):
                if not os.path.exists(file_ref):
                    missing.append(f"Referenced file not found: {file_ref}")
        
        return missing
    
    def _validate_workspace_structure(self, request: str) -> List[str]:
        """Validate workspace has expected structure for operation"""
        
        issues = []
        
        # Check for code operations without source directory
        if any(op in request.lower() for op in ['refactor', 'analyze code', 'test']):
            if not any(os.path.exists(d) for d in ['src/', 'lib/', '*.py', '*.js', '*.ts']):
                issues.append("Code operation requested but no source files found")
        
        # Check for package operations without package files
        if any(op in request.lower() for op in ['install', 'dependency', 'package']):
            if not any(os.path.exists(f) for f in ['requirements.txt', 'package.json', 'pyproject.toml']):
                issues.append("Package operation requested but no package configuration found")
        
        return issues
    
    def _check_missing_dependencies(self, request: str, context: Dict) -> List[str]:
        """Check for missing dependencies mentioned in request"""
        
        missing = []
        
        # Extract dependency mentions
        import re
        
        for dep_type, indicators in self.dependency_indicators.items():
            for indicator in indicators:
                if indicator in request:
                    # Extract package names after indicators
                    pattern = f"{re.escape(indicator)}\\s*([\\w-]+)"
                    matches = re.findall(pattern, request)
                    
                    for package in matches:
                        if not self._is_dependency_available(package, dep_type, context):
                            missing.append(f"Missing {dep_type} dependency: {package}")
        
        return missing
    
    def _detect_ambiguous_operations(self, request: str) -> List[str]:
        """Detect operations that need clarification"""
        
        ambiguous = []
        
        # Check for vague quantifiers
        if any(word in request.lower() for word in ['all', 'some', 'many', 'few']):
            ambiguous.append("Vague quantifiers found - specify exact counts or criteria")
        
        # Check for unclear targets
        if 'this' in request.lower() and request.count('this') > 2:
            ambiguous.append("Multiple 'this' references - clarify specific targets")
        
        # Check for missing operation details
        if any(op in request.lower() for op in ['update', 'modify', 'change']) and 'to' not in request.lower():
            ambiguous.append("Update operation without target specification")
        
        return ambiguous
    
    def _detect_project_type(self) -> Optional[str]:
        """Detect project type from workspace files"""
        
        if os.path.exists('pyproject.toml') or os.path.exists('requirements.txt'):
            return 'python_project'
        elif os.path.exists('package.json'):
            return 'node_project'
        elif os.path.exists('README.md'):
            return 'generic_project'
        
        return None
    
    def _check_required_files(self, project_type: str) -> List[str]:
        """Check for required files based on project type"""
        
        missing = []
        required = self.required_file_patterns.get(project_type, [])
        
        for pattern in required:
            if '*' in pattern:
                # Glob pattern
                import glob
                if not glob.glob(pattern):
                    missing.append(f"No files matching pattern: {pattern}")
            else:
                # Exact file
                if not os.path.exists(pattern):
                    missing.append(f"Required file missing: {pattern}")
        
        return missing
    
    def _check_broken_dependencies(self, request: str) -> List[str]:
        """Check for broken import statements or dependencies"""
        
        issues = []
        
        # Simple check for Python imports
        if 'import' in request:
            import re
            imports = re.findall(r'import\s+(\w+)', request)
            for imp in imports:
                try:
                    __import__(imp)
                except ImportError:
                    issues.append(f"Import not available: {imp}")
        
        return issues
    
    def _is_dependency_available(self, package: str, dep_type: str, context: Dict) -> bool:
        """Check if dependency is available in current environment"""
        
        if dep_type == 'python':
            try:
                __import__(package)
                return True
            except ImportError:
                return False
        
        # For other types, check if mentioned in context
        deps = context.get('dependencies', {})
        return package in deps
    
    def _generate_recommendations(self, missing_info: List[str], workspace_issues: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if missing_info:
            recommendations.append("Provide missing information before proceeding")
        
        if workspace_issues:
            recommendations.append("Resolve workspace issues first")
        
        if any('dependency' in issue for issue in missing_info):
            recommendations.append("Install missing dependencies")
        
        if any('file not found' in issue for issue in missing_info):
            recommendations.append("Create missing files or verify file paths")
        
        return recommendations
    
    def check_om_integration_readiness(self, context: Dict) -> Tuple[bool, List[str]]:
        """Check if OM system is ready for integration"""
        
        issues = []
        
        # Check if OM is available
        om_path = self._find_om_executable()
        if not om_path:
            issues.append("OM executable not found - run 'uv run om' to verify")
        
        # Check workspace status
        try:
            import subprocess
            result = subprocess.run(['uv', 'run', 'om', 'workspace', 'status'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                issues.append("OM workspace status check failed")
        except Exception as e:
            issues.append(f"Cannot check OM status: {str(e)}")
        
        return len(issues) == 0, issues
    
    def _find_om_executable(self) -> Optional[str]:
        """Find OM executable in workspace"""
        
        # Check for OM in projects/tools/om/
        om_paths = [
            'projects/tools/om/src/om/main.py',
            'projects/tools/om/src/main.py',
            'tools/om/main.py'
        ]
        
        for path in om_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def validate_constraint_compliance(self, request: str) -> List[str]:
        """Check compliance with CLU constraints (200-line files)"""
        
        violations = []
        
        # Check for file creation requests
        import re
        file_patterns = [
            r'create[_\s]+file[:\s]+([^\s\n]+)',
            r'new[_\s]+file[:\s]+([^\s\n]+)',
            r'add[_\s]+file[:\s]+([^\s\n]+)'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, request, re.IGNORECASE)
            for match in matches:
                if self._estimate_file_size(request, match) > 200:
                    violations.append(f"Potential CLU violation: {match} may exceed 200 lines")
        
        return violations
    
    def _estimate_file_size(self, request: str, filename: str) -> int:
        """Estimate lines of code for a file based on request description"""
        
        # Simple heuristic based on request complexity
        complexity_keywords = [
            'class', 'function', 'method', 'implementation', 'algorithm',
            'complex', 'comprehensive', 'complete', 'full'
        ]
        
        complexity_score = sum(1 for kw in complexity_keywords if kw in request.lower())
        
        # Base estimate + complexity multiplier
        base_lines = 50
        estimated_lines = base_lines + (complexity_score * 30)
        
        return estimated_lines
    
    def check_workspace_health(self) -> Dict[str, Any]:
        """Comprehensive workspace health check"""
        
        health_report = {
            'overall_health': 'unknown',
            'issues': [],
            'recommendations': [],
            'score': 0.0
        }
        
        issues = []
        score_components = []
        
        # Check directory structure
        if os.path.exists('projects/'):
            score_components.append(0.2)
        else:
            issues.append("Missing projects/ directory")
        
        # Check for pyproject.toml files
        pyproject_files = list(Path('.').rglob('pyproject.toml'))
        if pyproject_files:
            score_components.append(0.2)
        else:
            issues.append("No pyproject.toml files found")
        
        # Check for README files
        readme_files = list(Path('.').rglob('README.md'))
        if readme_files:
            score_components.append(0.1)
        
        # Check for test files
        test_files = list(Path('.').rglob('test_*.py'))
        if test_files:
            score_components.append(0.1)
        
        # Check OM integration
        om_ready, om_issues = self.check_om_integration_readiness({})
        if om_ready:
            score_components.append(0.3)
        else:
            issues.extend(om_issues)
        
        # Calculate overall health
        health_score = sum(score_components)
        health_report['score'] = health_score
        health_report['issues'] = issues
        
        if health_score >= 0.8:
            health_report['overall_health'] = 'excellent'
        elif health_score >= 0.6:
            health_report['overall_health'] = 'good'
        elif health_score >= 0.4:
            health_report['overall_health'] = 'fair'
        else:
            health_report['overall_health'] = 'poor'
        
        # Generate recommendations
        if not om_ready:
            health_report['recommendations'].append("Set up OM integration")
        if not pyproject_files:
            health_report['recommendations'].append("Add pyproject.toml configuration")
        if not test_files:
            health_report['recommendations'].append("Add test coverage")
        
        return health_report
