"""Workspace structure mapping - 200 LOC max"""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class ModuleInfo:
    """Information about a module"""
    name: str
    path: str
    line_count: int
    module_type: str
    dependencies: List[str]
    is_compliant: bool


@dataclass
class WorkspaceMap:
    """Complete workspace structure map"""
    root_path: str
    modules: Dict[str, ModuleInfo]
    structure: Dict[str, List[str]]
    compliance_summary: Dict[str, int]


class WorkspaceMapper:
    """Maps and analyzes workspace structure"""
    
    def __init__(self):
        self.module_types = {
            'models': ['models.py', 'data_models.py', 'schema.py'],
            'algorithms': ['detector.py', 'analyzer.py', 'optimizer.py', 'scorer.py'],
            'utilities': ['utils.py', 'helpers.py', 'tools.py'],
            'integration': ['integration.py', 'hooks.py', 'connector.py'],
            'validation': ['validator.py', 'checker.py'],
            'onboarding': ['trainer.py', 'mapper.py', 'tracker.py']
        }
        
        self.line_limits = {
            'models': 200,
            'algorithms': 300,
            'utilities': 250,
            'integration': 250,
            'validation': 300,
            'onboarding': 200
        }
    
    def map_workspace(self, root_path: str = ".") -> WorkspaceMap:
        """Create complete workspace map"""
        
        modules = {}
        structure = {}
        
        # Scan for Python files
        for py_file in Path(root_path).rglob("*.py"):
            if self._should_include_file(py_file):
                module_info = self._analyze_module(py_file)
                modules[module_info.name] = module_info
        
        # Build directory structure
        structure = self._build_structure_tree(root_path)
        
        # Generate compliance summary
        compliance_summary = self._generate_compliance_summary(modules)
        
        return WorkspaceMap(
            root_path=root_path,
            modules=modules,
            structure=structure,
            compliance_summary=compliance_summary
        )
    
    def get_module_dependencies(self, module_path: str) -> List[str]:
        """Extract module dependencies"""
        
        dependencies = []
        
        try:
            with open(module_path, 'r') as f:
                content = f.read()
            
            # Extract import statements
            import re
            import_patterns = [
                r'from\s+(\w+(?:\.\w+)*)\s+import',
                r'import\s+(\w+(?:\.\w+)*)'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)
            
            # Filter to local dependencies only
            local_deps = []
            for dep in dependencies:
                if not dep.startswith(('os', 'sys', 'json', 'typing', 'datetime', 'pathlib')):
                    local_deps.append(dep)
            
            return list(set(local_deps))
            
        except Exception:
            return []
    
    def check_module_compliance(self, module_info: ModuleInfo) -> bool:
        """Check if module complies with line limits"""
        
        limit = self.line_limits.get(module_info.module_type, 200)
        return module_info.line_count <= limit
    
    def get_navigation_guide(self) -> Dict[str, str]:
        """Generate navigation guide for new agents"""
        
        guide = {
            'core_systems': 'projects/core/ - Main system modules',
            'validation': 'projects/core/validation/ - Validation and coherence',
            'onboarding': 'projects/core/onboarding/ - Agent training system',
            'quality': 'projects/core/quality/ - Quality enforcement',
            'knowledge': 'projects/core/knowledge/ - Knowledge management',
            'protocols': 'projects/core/protocols/ - Communication protocols',
            'revenue': 'projects/revenue/ - Trading and revenue systems',
            'tools': 'projects/tools/ - Development tools',
            'parsers': 'projects/parsers/ - Code and doc parsers',
            'analytics': 'analytics/ - Data analysis and visualization',
            'automation': 'automation/ - Workflow automation'
        }
        
        return guide
    
    def find_key_files(self) -> Dict[str, str]:
        """Identify key files agents should know"""
        
        key_files = {}
        
        # Configuration files
        for config_file in ['pyproject.toml', 'requirements.txt', 'uv.lock']:
            if os.path.exists(config_file):
                key_files[f'config_{config_file}'] = config_file
        
        # Key system files
        important_patterns = [
            ('main_entry', 'projects/tools/om/src/om/main.py'),
            ('validation_models', 'projects/core/validation/models.py'),
            ('onboarding_system', 'projects/core/onboarding/__init__.py'),
            ('quality_gate', 'projects/core/quality/quality_gate_system.py')
        ]
        
        for name, pattern in important_patterns:
            if os.path.exists(pattern):
                key_files[name] = pattern
        
        return key_files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in mapping"""
        
        # Exclude cache and build directories
        exclude_dirs = {'__pycache__', '.git', 'node_modules', 'dist', 'build'}
        
        for part in file_path.parts:
            if part in exclude_dirs:
                return False
        
        # Include only Python files
        return file_path.suffix == '.py'
    
    def _analyze_module(self, file_path: Path) -> ModuleInfo:
        """Analyze individual module"""
        
        # Count lines
        try:
            with open(file_path, 'r') as f:
                line_count = len(f.readlines())
        except Exception:
            line_count = 0
        
        # Determine module type
        module_type = self._classify_module(file_path)
        
        # Get dependencies
        dependencies = self.get_module_dependencies(str(file_path))
        
        # Check compliance
        is_compliant = line_count <= self.line_limits.get(module_type, 200)
        
        return ModuleInfo(
            name=file_path.stem,
            path=str(file_path),
            line_count=line_count,
            module_type=module_type,
            dependencies=dependencies,
            is_compliant=is_compliant
        )
    
    def _classify_module(self, file_path: Path) -> str:
        """Classify module type based on name and location"""
        
        filename = file_path.name
        
        for module_type, patterns in self.module_types.items():
            for pattern in patterns:
                if pattern in filename:
                    return module_type
        
        # Classification by directory
        path_str = str(file_path)
        if 'validation' in path_str:
            return 'validation'
        elif 'onboarding' in path_str:
            return 'onboarding'
        elif 'quality' in path_str:
            return 'validation'
        elif 'knowledge' in path_str:
            return 'utilities'
        elif 'protocols' in path_str:
            return 'integration'
        
        return 'utilities'  # Default
    
    def _build_structure_tree(self, root_path: str) -> Dict[str, List[str]]:
        """Build directory structure tree"""
        
        structure = {}
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Skip hidden and cache directories
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
            
            rel_path = os.path.relpath(dirpath, root_path)
            if rel_path == '.':
                rel_path = 'root'
            
            # Add directories
            structure[rel_path] = list(dirnames)
            
            # Add Python files
            py_files = [f for f in filenames if f.endswith('.py')]
            if py_files:
                if rel_path not in structure:
                    structure[rel_path] = []
                structure[rel_path].extend(py_files)
        
        return structure
    
    def _generate_compliance_summary(self, modules: Dict[str, ModuleInfo]) -> Dict[str, int]:
        """Generate compliance summary statistics"""
        
        summary = {
            'total_modules': len(modules),
            'compliant_modules': 0,
            'violation_modules': 0,
            'models_compliant': 0,
            'algorithms_compliant': 0,
            'utilities_compliant': 0
        }
        
        for module in modules.values():
            if module.is_compliant:
                summary['compliant_modules'] += 1
                summary[f'{module.module_type}_compliant'] += 1
            else:
                summary['violation_modules'] += 1
        
        return summary
