#!/usr/bin/env python3
"""
Codebase analysis for architecture understanding and optimization.
Smart summaries for rapid development acceleration.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
import networkx as nx


@dataclass 
class ModuleInfo:
    """Information about a Python module."""
    name: str
    path: str
    lines: int
    functions: int
    classes: int
    imports: List[str]
    dependencies: List[str]
    complexity_score: float


@dataclass
class ArchitectureNode:
    """Node in architecture dependency graph."""
    name: str
    node_type: str  # module, class, function
    dependencies: List[str]
    dependents: List[str]
    centrality: float
    cluster: str


@dataclass
class PatternUsage:
    """Code pattern usage statistics."""
    pattern_name: str
    usage_count: int
    success_rate: float
    locations: List[str]
    effectiveness: float


class CodebaseAnalyzer:
    """Analyzes codebase structure for architecture insights."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.modules = {}
        self.dependency_graph = nx.DiGraph()
        self.patterns = {}
        
    def analyze_architecture(self) -> Dict:
        """Complete architecture analysis."""
        modules = self._scan_modules()
        dependencies = self._analyze_dependencies(modules)
        clusters = self._identify_clusters(dependencies)
        critical_paths = self._find_critical_paths(dependencies)
        
        return {
            'modules': len(modules),
            'dependencies': len(dependencies),
            'clusters': len(clusters),
            'critical_paths': critical_paths,
            'bottlenecks': self._identify_bottlenecks(dependencies),
            'modularity_score': self._calculate_modularity(clusters),
            'coupling_score': self._calculate_coupling(dependencies)
        }
    
    def analyze_dependencies(self) -> Dict:
        """Dependency analysis with critical path detection."""
        modules = self._scan_modules()
        dep_graph = self._build_dependency_graph(modules)
        
        # Critical path analysis
        critical_paths = []
        try:
            # Find longest paths (most dependencies)
            for node in dep_graph.nodes():
                if dep_graph.in_degree(node) == 0:  # Root nodes
                    paths = nx.single_source_shortest_path(dep_graph, node)
                    longest = max(paths.values(), key=len, default=[])
                    if len(longest) > 3:
                        critical_paths.append(longest)
        except:
            pass
        
        # Circular dependencies
        try:
            cycles = list(nx.simple_cycles(dep_graph))
        except:
            cycles = []
        
        # High-impact nodes (many dependents)
        high_impact = []
        for node in dep_graph.nodes():
            if dep_graph.out_degree(node) > 5:
                high_impact.append({
                    'module': node,
                    'dependents': dep_graph.out_degree(node),
                    'impact_score': dep_graph.out_degree(node) * (dep_graph.in_degree(node) + 1)
                })
        
        return {
            'total_modules': len(modules),
            'total_dependencies': dep_graph.number_of_edges(),
            'circular_dependencies': len(cycles),
            'critical_paths': len(critical_paths),
            'high_impact_modules': len(high_impact),
            'dependency_ratio': dep_graph.number_of_edges() / max(len(modules), 1),
            'cycles': cycles[:3],  # Show first 3 cycles
            'bottlenecks': self._identify_bottlenecks(dep_graph)
        }
    
    def analyze_patterns(self) -> Dict:
        """Pattern usage analysis."""
        try:
            from knowledge.db_manager import ContextDB
            db = ContextDB()
            
            # Get pattern usage statistics
            patterns = db.find_patterns()
            pattern_stats = []
            
            for pattern in patterns:
                # Count usage in codebase
                usage_count = self._count_pattern_usage(pattern.name)
                effectiveness = pattern.success_count / max(usage_count, 1)
                
                pattern_stats.append({
                    'name': pattern.name,
                    'type': pattern.pattern_type,
                    'usage_count': usage_count,
                    'success_count': pattern.success_count,
                    'effectiveness': effectiveness,
                    'context': pattern.usage_context[:50] if pattern.usage_context else ''
                })
            
            # Sort by effectiveness
            pattern_stats.sort(key=lambda x: x['effectiveness'], reverse=True)
            
            db.close()
            
            return {
                'total_patterns': len(patterns),
                'most_used': pattern_stats[:5],
                'most_effective': pattern_stats[:3],
                'underutilized': [p for p in pattern_stats if p['usage_count'] < 2][:3]
            }
            
        except Exception:
            return {'error': 'Pattern analysis requires knowledge database'}
    
    def analyze_gaps(self) -> Dict:
        """Identify missing implementations and inconsistencies."""
        modules = self._scan_modules()
        gaps = {
            'missing_tests': [],
            'incomplete_modules': [],
            'inconsistent_patterns': [],
            'unused_imports': [],
            'missing_docstrings': []
        }
        
        for module in modules.values():
            # Missing tests
            test_path = self._find_test_file(module.path)
            if not test_path:
                gaps['missing_tests'].append(module.name)
            
            # Incomplete modules (very few functions/classes)
            if module.lines > 50 and module.functions + module.classes < 2:
                gaps['incomplete_modules'].append({
                    'module': module.name,
                    'lines': module.lines,
                    'implementations': module.functions + module.classes
                })
            
            # Missing docstrings (analyze actual files)
            docstring_coverage = self._analyze_docstring_coverage(module.path)
            if docstring_coverage < 0.5:
                gaps['missing_docstrings'].append({
                    'module': module.name,
                    'coverage': docstring_coverage
                })
        
        return gaps
    
    def _scan_modules(self) -> Dict[str, ModuleInfo]:
        """Scan all Python modules in workspace."""
        modules = {}
        
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                # Count elements
                functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                imports = self._extract_imports(tree)
                
                # Calculate complexity score
                complexity = self._calculate_complexity(tree)
                
                relative_path = py_file.relative_to(self.workspace_root)
                module_name = str(relative_path).replace('/', '.').replace('.py', '')
                
                modules[module_name] = ModuleInfo(
                    name=module_name,
                    path=str(relative_path),
                    lines=len(content.splitlines()),
                    functions=functions,
                    classes=classes,
                    imports=imports,
                    dependencies=[],  # Will be filled later
                    complexity_score=complexity
                )
                
            except Exception:
                continue
        
        return modules
    
    def _build_dependency_graph(self, modules: Dict[str, ModuleInfo]) -> nx.DiGraph:
        """Build dependency graph from modules."""
        graph = nx.DiGraph()
        
        # Add nodes
        for module in modules.values():
            graph.add_node(module.name)
        
        # Add edges based on imports
        for module in modules.values():
            for import_name in module.imports:
                # Try to match imports to modules
                for target_module in modules.keys():
                    if import_name in target_module or target_module.endswith(import_name):
                        graph.add_edge(module.name, target_module)
                        break
        
        return graph
    
    def _analyze_dependencies(self, modules: Dict[str, ModuleInfo]) -> nx.DiGraph:
        """Analyze module dependencies."""
        return self._build_dependency_graph(modules)
    
    def _identify_clusters(self, dep_graph: nx.DiGraph) -> List[List[str]]:
        """Identify architectural clusters."""
        try:
            # Convert to undirected for community detection
            undirected = dep_graph.to_undirected()
            
            # Simple clustering based on connectivity
            clusters = []
            visited = set()
            
            for node in undirected.nodes():
                if node not in visited:
                    # Find connected component
                    component = nx.node_connected_component(undirected, node)
                    if len(component) > 1:
                        clusters.append(list(component))
                        visited.update(component)
            
            return clusters
        except:
            return []
    
    def _find_critical_paths(self, dep_graph: nx.DiGraph) -> List[List[str]]:
        """Find critical dependency paths."""
        try:
            critical_paths = []
            
            # Find paths longer than 3 modules
            for source in dep_graph.nodes():
                if dep_graph.in_degree(source) == 0:  # Source node
                    for target in dep_graph.nodes():
                        if dep_graph.out_degree(target) == 0:  # Sink node
                            try:
                                path = nx.shortest_path(dep_graph, source, target)
                                if len(path) > 3:
                                    critical_paths.append(path)
                            except nx.NetworkXNoPath:
                                continue
            
            return critical_paths[:5]  # Return top 5
        except:
            return []
    
    def _identify_bottlenecks(self, dep_graph: nx.DiGraph) -> List[Dict]:
        """Identify dependency bottlenecks."""
        bottlenecks = []
        
        for node in dep_graph.nodes():
            in_degree = dep_graph.in_degree(node)
            out_degree = dep_graph.out_degree(node)
            
            # High fan-in or fan-out = potential bottleneck
            if in_degree > 3 or out_degree > 5:
                bottlenecks.append({
                    'module': node,
                    'incoming': in_degree,
                    'outgoing': out_degree,
                    'bottleneck_score': float(in_degree * out_degree)
                })
        
        return sorted(bottlenecks, key=lambda x: x['bottleneck_score'], reverse=True)[:5]
    
    def _calculate_modularity(self, clusters: List[List[str]]) -> float:
        """Calculate architectural modularity score."""
        if not clusters:
            return 0.0
        
        # Simple modularity: ratio of intra-cluster to total connections
        total_modules = sum(len(cluster) for cluster in clusters)
        cluster_sizes = [len(cluster) for cluster in clusters]
        
        # Higher score for more balanced clusters
        size_variance = sum((size - total_modules/len(clusters))**2 for size in cluster_sizes)
        modularity = 1.0 / (1.0 + size_variance / max(total_modules, 1))
        
        return round(modularity, 3)
    
    def _calculate_coupling(self, dep_graph: nx.DiGraph) -> float:
        """Calculate coupling score."""
        if dep_graph.number_of_nodes() == 0:
            return 0.0
        
        # Coupling = edges / possible_edges
        nodes = dep_graph.number_of_nodes()
        edges = dep_graph.number_of_edges()
        possible_edges = nodes * (nodes - 1)
        
        coupling = edges / max(possible_edges, 1)
        return round(coupling, 3)
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        # Count decision points
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _should_skip_file(self, path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            'venv', '.venv', 'build', 'dist', '.tox'
        }
        
        return any(pattern in str(path) for pattern in skip_patterns)
    
    def _find_test_file(self, module_path: str) -> Optional[str]:
        """Find corresponding test file."""
        test_patterns = [
            f"test_{Path(module_path).stem}.py",
            f"{Path(module_path).stem}_test.py",
            f"tests/test_{Path(module_path).stem}.py"
        ]
        
        for pattern in test_patterns:
            test_path = self.workspace_root / pattern
            if test_path.exists():
                return str(test_path)
        
        return None
    
    def _analyze_docstring_coverage(self, module_path: str) -> float:
        """Analyze docstring coverage for module."""
        try:
            file_path = self.workspace_root / module_path
            content = file_path.read_text()
            tree = ast.parse(content)
            
            total_items = 0
            documented_items = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1
            
            return documented_items / max(total_items, 1)
            
        except Exception:
            return 0.0
    
    def _count_pattern_usage(self, pattern_name: str) -> int:
        """Count usage of specific pattern in codebase."""
        count = 0
        
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                content = py_file.read_text()
                # Simple pattern matching (could be enhanced)
                count += content.lower().count(pattern_name.lower())
            except Exception:
                continue
        
        return count