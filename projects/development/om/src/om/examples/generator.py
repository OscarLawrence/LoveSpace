"""
Main example generator using modular components
"""

from pathlib import Path
from typing import List
from .data_models import IntegrationExample
from .workflow_generator import WorkflowGenerator
from .patterns_generator import PatternsGenerator
from .use_cases_generator import UseCasesGenerator
from .markdown_generator import MarkdownGenerator


class ExampleGenerator:
    """Generates integration examples from codebase analysis."""
    
    def __init__(self):
        self.examples: List[IntegrationExample] = []
        self.command_patterns = {
            'docs': ['docs generate', 'docs coverage', 'docs schema'],
            'memory': ['memory stats', 'session save', 'preferences set'],
            'analysis': ['analyze architecture', 'analyze dependencies'],
            'code': ['code parse', 'code execute'],
            'parsing': ['populate-patterns', 'modules list']
        }
        
        # Generators
        self.workflow_generator = WorkflowGenerator()
        self.patterns_generator = PatternsGenerator()
        self.use_cases_generator = UseCasesGenerator()
        self.markdown_generator = MarkdownGenerator()
    
    def generate_workflow_examples(self) -> List[IntegrationExample]:
        """Generate workflow-based integration examples."""
        return self.workflow_generator.generate_examples()
    
    def generate_integration_patterns(self) -> List[IntegrationExample]:
        """Generate common integration patterns."""
        return self.patterns_generator.generate_examples()
    
    def generate_use_case_examples(self) -> List[IntegrationExample]:
        """Generate specific use case examples."""
        return self.use_cases_generator.generate_examples()
    
    def generate_all_examples(self) -> List[IntegrationExample]:
        """Generate all types of examples."""
        all_examples = []
        all_examples.extend(self.generate_workflow_examples())
        all_examples.extend(self.generate_integration_patterns())
        all_examples.extend(self.generate_use_case_examples())
        return all_examples
    
    def save_examples_to_markdown(self, examples: List[IntegrationExample], output_path: Path):
        """Save examples to markdown file."""
        self.markdown_generator.save_examples_to_markdown(examples, output_path)
