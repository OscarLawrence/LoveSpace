"""
Predefined workflow templates for common development tasks
"""

from typing import List
from .data_models import Workflow, WorkflowStep


class WorkflowTemplates:
    """Predefined workflow templates for common development tasks."""
    
    @staticmethod
    def create_documentation_workflow(source_dir: str = "src", 
                                    output_dir: str = "docs",
                                    min_coverage: float = 85.0) -> Workflow:
        """Create documentation generation workflow."""
        return Workflow(
            id="custom_documentation",
            name="Custom Documentation Workflow",
            description=f"Generate documentation from {source_dir} to {output_dir}",
            steps=[
                WorkflowStep(
                    name="generate",
                    description="Generate Sphinx documentation",
                    command=f"docs generate --source {source_dir} --output {output_dir} --build-html",
                    scopes=["docs"]
                ),
                WorkflowStep(
                    name="coverage",
                    description="Check coverage",
                    command=f"docs coverage gate {source_dir} --min-coverage {min_coverage}",
                    scopes=["docs"],
                    dependencies=["generate"]
                ),
                WorkflowStep(
                    name="schemas",
                    description="Generate schemas",
                    command=f"docs schema batch {source_dir} --output-dir schemas",
                    scopes=["docs"],
                    dependencies=["coverage"]
                )
            ]
        )
    
    @staticmethod
    def create_feature_workflow(feature_name: str, 
                              target_files: List[str] = None) -> Workflow:
        """Create feature implementation workflow."""
        files_str = " ".join(target_files) if target_files else f"src/*{feature_name}*"
        
        return Workflow(
            id=f"feature_{feature_name}",
            name=f"Implement {feature_name} Feature",
            description=f"Complete implementation of {feature_name} feature",
            steps=[
                WorkflowStep(
                    name="analyze",
                    description="Analyze requirements",
                    command=f"analyze architecture --focus {feature_name}",
                    scopes=["analysis"]
                ),
                WorkflowStep(
                    name="parse",
                    description="Parse target files",
                    command=f"code parse {files_str}",
                    scopes=["code"],
                    dependencies=["analyze"]
                ),
                WorkflowStep(
                    name="test",
                    description="Run tests",
                    command=f"code execute tests/test_{feature_name}.py",
                    scopes=["code"],
                    dependencies=["parse"]
                ),
                WorkflowStep(
                    name="document",
                    description="Generate documentation",
                    command=f"docs generate --source src --focus {feature_name}",
                    scopes=["docs"],
                    dependencies=["test"]
                )
            ]
        )
    
    @staticmethod
    def create_quality_workflow(source_dir: str = "src") -> Workflow:
        """Create quality assurance workflow."""
        return Workflow(
            id="quality_assurance",
            name="Quality Assurance Workflow",
            description=f"Complete quality check for {source_dir}",
            steps=[
                WorkflowStep(
                    name="docs_coverage",
                    description="Check documentation coverage",
                    command=f"docs coverage gate {source_dir} --min-coverage 90",
                    scopes=["docs"]
                ),
                WorkflowStep(
                    name="schema_validation",
                    description="Validate schemas",
                    command=f"docs schema batch {source_dir} --validate-all",
                    scopes=["docs"],
                    dependencies=["docs_coverage"]
                ),
                WorkflowStep(
                    name="architecture_analysis",
                    description="Analyze architecture",
                    command=f"analyze architecture --comprehensive",
                    scopes=["analysis"],
                    dependencies=["schema_validation"]
                )
            ]
        )
