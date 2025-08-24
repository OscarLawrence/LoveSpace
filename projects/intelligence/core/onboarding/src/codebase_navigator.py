"""
Codebase Navigator

Provides intelligent navigation and exploration of the workspace codebase.
Helps agents understand structure, dependencies, and key components.
"""

import os
import json
import ast
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModuleInfo:
    """Information about a code module."""
    name: str
    path: str
    type: str  # 'package', 'module', 'script'
    size_loc: int
    dependencies: List[str]
    exports: List[str]
    description: str


@dataclass
class NavigationMap:
    """Complete navigation map of the codebase."""
    modules: List[ModuleInfo]
    dependency_graph: Dict[str, List[str]]
    entry_points: List[str]
    critical_paths: List[str]
    architecture_overview: str


class CodebaseNavigator:
    """
    Intelligent codebase navigation system.
    
    Features:
    - Module discovery and analysis
    - Dependency mapping
    - Entry point identification
    - Architecture overview generation
    - Interactive exploration guides
    """
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.navigation_map = None
        self.file_cache = {}
        
    def generate_navigation_map(self) -> NavigationMap:
        """Generate complete navigation map of codebase."""
        modules = []
        dependency_graph = {}
        
        # Discover all Python modules
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_info = self._analyze_module(file_path)
                    if module_info:
                        modules.append(module_info)
                        dependency_graph[module_info.name] = module_info.dependencies
        
        # Identify entry points and critical paths
        entry_points = self._identify_entry_points(modules)
        critical_paths = self._identify_critical_paths(dependency_graph)
        
        # Generate architecture overview
        architecture_overview = self._generate_architecture_overview(modules, dependency_graph)
        
        self.navigation_map = NavigationMap(
            modules=modules,
            dependency_graph=dependency_graph,
            entry_points=entry_points,
            critical_paths=critical_paths,
            architecture_overview=architecture_overview
        )
        
        return self.navigation_map
    
    def get_module_recommendations(self, role: str = "new_developer") -> List[str]:
        """Get recommended modules to explore based on role."""
        if not self.navigation_map:
            self.generate_navigation_map()
            
        recommendations = []
        
        if role == "new_developer":
            # Start with entry points and core modules
            recommendations.extend(self.navigation_map.entry_points[:3])
            
            # Add modules with good documentation
            documented_modules = [
                m.name for m in self.navigation_map.modules 
                if m.description and len(m.description) > 50
            ]
            recommendations.extend(documented_modules[:2])
            
        elif role == "system_architect":
            # Focus on critical paths and dependencies
            recommendations.extend(self.navigation_map.critical_paths[:5])
            
        elif role == "quality_assurance":
            # Focus on test modules and validation components
            test_modules = [
                m.name for m in self.navigation_map.modules
                if 'test' in m.name.lower() or 'validation' in m.name.lower()
            ]
            recommendations.extend(test_modules[:3])
        
        return list(set(recommendations))  # Remove duplicates
    
    def get_exploration_guide(self, module_name: str) -> Dict:
        """Get detailed exploration guide for a specific module."""
        if not self.navigation_map:
            self.generate_navigation_map()
            
        module = next((m for m in self.navigation_map.modules if m.name == module_name), None)
        if not module:
            return {"error": f"Module {module_name} not found"}
        
        guide = {
            'module': module.__dict__,
            'exploration_steps': self._generate_exploration_steps(module),
            'related_modules': self._find_related_modules(module_name),
            'learning_objectives': self._define_learning_objectives(module),
            'key_concepts': self._extract_key_concepts(module),
            'hands_on_exercises': self._suggest_exercises(module)
        }
        
        return guide
    
    def find_implementation_examples(self, concept: str) -> List[Dict]:
        """Find implementation examples of a specific concept."""
        if not self.navigation_map:
            self.generate_navigation_map()
            
        examples = []
        
        for module in self.navigation_map.modules:
            file_path = module.path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Search for concept in code
                if concept.lower() in content.lower():
                    # Extract relevant code snippets
                    snippets = self._extract_code_snippets(content, concept)
                    
                    for snippet in snippets:
                        examples.append({
                            'module': module.name,
                            'file_path': file_path,
                            'snippet': snippet,
                            'context': self._get_snippet_context(content, snippet)
                        })
                        
            except Exception as e:
                continue
        
        return examples[:5]  # Return top 5 examples
    
    def get_dependency_analysis(self, module_name: str) -> Dict:
        """Get detailed dependency analysis for a module."""
        if not self.navigation_map:
            self.generate_navigation_map()
            
        dependencies = self.navigation_map.dependency_graph.get(module_name, [])
        dependents = [
            name for name, deps in self.navigation_map.dependency_graph.items()
            if module_name in deps
        ]
        
        return {
            'module': module_name,
            'direct_dependencies': dependencies,
            'dependents': dependents,
            'dependency_depth': self._calculate_dependency_depth(module_name),
            'circular_dependencies': self._detect_circular_dependencies(module_name),
            'impact_analysis': self._analyze_change_impact(module_name)
        }
    
    def _analyze_module(self, file_path: str) -> Optional[ModuleInfo]:
        """Analyze a Python module and extract information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to extract information
            tree = ast.parse(content)
            
            # Extract module name
            rel_path = os.path.relpath(file_path, self.workspace_root)
            module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Count lines of code
            loc = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            
            # Extract dependencies
            dependencies = self._extract_dependencies(tree)
            
            # Extract exports (__all__, classes, functions)
            exports = self._extract_exports(tree)
            
            # Extract description from docstring
            description = self._extract_module_description(tree)
            
            # Determine module type
            module_type = self._determine_module_type(file_path, content)
            
            return ModuleInfo(
                name=module_name,
                path=file_path,
                type=module_type,
                size_loc=loc,
                dependencies=dependencies,
                exports=exports,
                description=description
            )
            
        except Exception as e:
            return None
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract import dependencies from AST."""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module.split('.')[0])
        
        return list(set(dependencies))
    
    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """Extract exported names from AST."""
        exports = []
        
        # Check for __all__
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    exports.append(elt.s)
        
        # If no __all__, extract class and function names
        if not exports:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith('_'):
                        exports.append(node.name)
        
        return exports
    
    def _extract_module_description(self, tree: ast.AST) -> str:
        """Extract module description from docstring."""
        if isinstance(tree, ast.Module) and tree.body:
            first_stmt = tree.body[0]
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
                return first_stmt.value.s.strip()
        return ""
    
    def _determine_module_type(self, file_path: str, content: str) -> str:
        """Determine the type of module."""
        if '__init__.py' in file_path:
            return 'package'
        elif 'if __name__ == "__main__"' in content:
            return 'script'
        else:
            return 'module'
    
    def _identify_entry_points(self, modules: List[ModuleInfo]) -> List[str]:
        """Identify main entry points in the codebase."""
        entry_points = []
        
        # Look for main scripts
        main_scripts = [m.name for m in modules if m.type == 'script']
        entry_points.extend(main_scripts)
        
        # Look for CLI modules
        cli_modules = [m.name for m in modules if any(keyword in m.name.lower() for keyword in ['cli', 'main', 'app'])]
        entry_points.extend(cli_modules)
        
        # Look for __init__.py files with substantial content
        init_modules = [m.name for m in modules if m.name.endswith('__init__') and m.size_loc > 10]
        entry_points.extend(init_modules)
        
        return list(set(entry_points))
    
    def _identify_critical_paths(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Identify critical modules based on dependency analysis."""
        # Count how many modules depend on each module
        dependents_count = {}
        for module, deps in dependency_graph.items():
            for dep in deps:
                dependents_count[dep] = dependents_count.get(dep, 0) + 1
        
        # Sort by dependency count
        critical_modules = sorted(dependents_count.items(), key=lambda x: x[1], reverse=True)
        
        return [module for module, count in critical_modules[:5]]
    
    def _generate_architecture_overview(self, modules: List[ModuleInfo], dependency_graph: Dict[str, List[str]]) -> str:
        """Generate high-level architecture overview."""
        overview = []
        
        # Basic statistics
        total_modules = len(modules)
        total_loc = sum(m.size_loc for m in modules)
        
        overview.append(f"Codebase Overview: {total_modules} modules, {total_loc} lines of code")
        
        # Module breakdown by type
        type_counts = {}
        for module in modules:
            type_counts[module.type] = type_counts.get(module.type, 0) + 1
        
        overview.append(f"Module Types: {dict(type_counts)}")
        
        # Top-level packages
        packages = set()
        for module in modules:
            parts = module.name.split('.')
            if len(parts) > 1:
                packages.add(parts[0])
        
        overview.append(f"Main Packages: {sorted(list(packages))}")
        
        return "\n".join(overview)
    
    def _generate_exploration_steps(self, module: ModuleInfo) -> List[str]:
        """Generate step-by-step exploration guide."""
        steps = [
            f"1. Open {module.path} in your editor",
            f"2. Read the module docstring: {module.description[:100]}...",
            f"3. Examine the main exports: {', '.join(module.exports[:3])}",
            f"4. Review the dependencies: {', '.join(module.dependencies[:3])}"
        ]
        
        if module.type == 'script':
            steps.append("5. Look for the main execution block")
        elif module.type == 'package':
            steps.append("5. Explore the package structure")
        
        steps.append("6. Try running or importing the module")
        
        return steps
    
    def _find_related_modules(self, module_name: str) -> List[str]:
        """Find modules related to the given module."""
        if not self.navigation_map:
            return []
            
        related = set()
        
        # Add dependencies
        dependencies = self.navigation_map.dependency_graph.get(module_name, [])
        related.update(dependencies)
        
        # Add dependents
        for name, deps in self.navigation_map.dependency_graph.items():
            if module_name in deps:
                related.add(name)
        
        # Add modules with similar names
        module_parts = module_name.split('.')
        for module in self.navigation_map.modules:
            other_parts = module.name.split('.')
            if any(part in other_parts for part in module_parts):
                related.add(module.name)
        
        related.discard(module_name)  # Remove self
        return list(related)[:5]
    
    def _define_learning_objectives(self, module: ModuleInfo) -> List[str]:
        """Define learning objectives for the module."""
        objectives = []
        
        if module.type == 'script':
            objectives.append("Understand the main execution flow")
            objectives.append("Identify key command-line arguments")
        elif module.type == 'package':
            objectives.append("Understand the package structure")
            objectives.append("Learn the main API entry points")
        else:
            objectives.append("Understand the module's purpose and functionality")
            objectives.append("Learn how to use the exported functions/classes")
        
        if module.dependencies:
            objectives.append("Understand dependencies and their roles")
        
        return objectives
    
    def _extract_key_concepts(self, module: ModuleInfo) -> List[str]:
        """Extract key concepts from the module."""
        concepts = []
        
        # Extract from exports
        concepts.extend(module.exports[:3])
        
        # Extract from module name
        name_parts = module.name.split('.')
        concepts.extend([part for part in name_parts if len(part) > 3])
        
        # Extract from description keywords
        if module.description:
            words = module.description.lower().split()
            keywords = [word for word in words if len(word) > 5 and word.isalpha()]
            concepts.extend(keywords[:3])
        
        return list(set(concepts))
    
    def _suggest_exercises(self, module: ModuleInfo) -> List[str]:
        """Suggest hands-on exercises for the module."""
        exercises = []
        
        if module.exports:
            exercises.append(f"Try importing and using {module.exports[0]}")
        
        if module.type == 'script':
            exercises.append("Run the script with different arguments")
        
        exercises.append("Read through the source code line by line")
        exercises.append("Identify potential improvements or questions")
        
        return exercises
    
    def _extract_code_snippets(self, content: str, concept: str) -> List[str]:
        """Extract relevant code snippets containing the concept."""
        lines = content.split('\n')
        snippets = []
        
        for i, line in enumerate(lines):
            if concept.lower() in line.lower():
                # Extract context around the line
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                snippet = '\n'.join(lines[start:end])
                snippets.append(snippet)
        
        return snippets[:3]  # Return first 3 snippets
    
    def _get_snippet_context(self, content: str, snippet: str) -> str:
        """Get context description for a code snippet."""
        # This is a simplified implementation
        if 'class ' in snippet:
            return "Class definition"
        elif 'def ' in snippet:
            return "Function definition"
        elif 'import ' in snippet:
            return "Import statement"
        else:
            return "Code block"
    
    def _calculate_dependency_depth(self, module_name: str) -> int:
        """Calculate dependency depth for a module."""
        if not self.navigation_map:
            return 0
            
        visited = set()
        depth = 0
        queue = [(module_name, 0)]
        
        while queue:
            current, current_depth = queue.pop(0)
            if current in visited:
                continue
                
            visited.add(current)
            depth = max(depth, current_depth)
            
            dependencies = self.navigation_map.dependency_graph.get(current, [])
            for dep in dependencies:
                if dep not in visited:
                    queue.append((dep, current_depth + 1))
        
        return depth
    
    def _detect_circular_dependencies(self, module_name: str) -> List[List[str]]:
        """Detect circular dependencies involving the module."""
        # Simplified circular dependency detection
        # In practice, this would be more sophisticated
        return []
    
    def _analyze_change_impact(self, module_name: str) -> Dict:
        """Analyze the impact of changes to the module."""
        if not self.navigation_map:
            return {}
            
        # Find all modules that depend on this one
        dependents = []
        for name, deps in self.navigation_map.dependency_graph.items():
            if module_name in deps:
                dependents.append(name)
        
        return {
            'direct_impact': len(dependents),
            'affected_modules': dependents,
            'risk_level': 'high' if len(dependents) > 5 else 'medium' if len(dependents) > 2 else 'low'
        }
