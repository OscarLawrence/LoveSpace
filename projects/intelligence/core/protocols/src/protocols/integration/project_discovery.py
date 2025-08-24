"""
Project discovery for workspace integration
"""

from typing import List, Dict, Any
from pathlib import Path

from .data_models import ProjectIntegration


class ProjectDiscovery:
    """Discovers and analyzes projects in workspace"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
    
    def discover_projects(self) -> Dict[str, ProjectIntegration]:
        """Discover and analyze all projects in workspace"""
        projects = {}
        
        # Look for project directories
        project_dirs = [d for d in self.workspace_root.rglob("*") 
                       if d.is_dir() and self._is_project_directory(d)]
        
        for project_path in project_dirs:
            project_name = project_path.name
            hooks = self._determine_integration_hooks(project_path)
            
            integration = ProjectIntegration(
                project_name=project_name,
                project_path=project_path,
                integration_hooks=hooks
            )
            
            projects[project_name] = integration
            print(f"  📦 Discovered: {project_name}")
        
        return projects
    
    def _is_project_directory(self, path: Path) -> bool:
        """Check if directory is a project directory"""
        # Check for common project indicators
        indicators = [
            "src", "lib", "tests", "test",
            "pyproject.toml", "setup.py", "package.json",
            "Cargo.toml", "go.mod", "pom.xml"
        ]
        
        return any((path / indicator).exists() for indicator in indicators)
    
    def _determine_integration_hooks(self, project_path: Path) -> List[str]:
        """Determine appropriate integration hooks for project"""
        hooks = []
        
        # Check for specific project types
        if (project_path / "src").exists():
            hooks.append("source_monitoring")
        
        if (project_path / "tests").exists():
            hooks.append("test_monitoring")
        
        # Check for AI/ML related files
        src_files = list(project_path.rglob("*.py"))
        for src_file in src_files[:10]:  # Check first 10 files
            try:
                content = src_file.read_text()
                if any(keyword in content.lower() for keyword in ["ai", "ml", "model", "optimizer"]):
                    hooks.append("ai_performance_monitoring")
                    break
            except:
                continue
        
        # Default hooks
        if not hooks:
            hooks = ["basic_monitoring"]
        
        return hooks
