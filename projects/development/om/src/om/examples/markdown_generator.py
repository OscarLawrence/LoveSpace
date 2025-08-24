"""
Markdown documentation generator for examples
"""

from pathlib import Path
from typing import List
from .data_models import IntegrationExample


class MarkdownGenerator:
    """Generates markdown documentation from examples"""
    
    def save_examples_to_markdown(self, examples: List[IntegrationExample], output_path: Path):
        """Save examples to markdown file."""
        lines = [
            "# Om Integration Examples",
            "",
            "Comprehensive examples demonstrating Om's capabilities and integration patterns.",
            ""
        ]
        
        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        
        for i, example in enumerate(examples, 1):
            anchor = example.title.lower().replace(' ', '-').replace('/', '-')
            lines.append(f"{i}. [{example.title}](#{anchor})")
        
        lines.append("")
        
        # Generate examples
        for i, example in enumerate(examples, 1):
            lines.extend(self._generate_example_markdown(example, i))
            lines.append("")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
    
    def _generate_example_markdown(self, example: IntegrationExample, number: int) -> List[str]:
        """Generate markdown for single example."""
        lines = [
            f"## {number}. {example.title}",
            "",
            f"**Category:** {example.category}  ",
            f"**Difficulty:** {example.difficulty}  ",
            f"**Tags:** {', '.join(example.tags)}",
            "",
            example.description,
            ""
        ]
        
        if example.prerequisites:
            lines.append("### Prerequisites")
            lines.append("")
            for prereq in example.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")
        
        lines.append("### Code")
        lines.append("")
        lines.append("```bash")
        lines.extend(example.code.split('\n'))
        lines.append("```")
        lines.append("")
        
        lines.append("### Explanation")
        lines.append("")
        lines.extend(example.explanation.split('\n'))
        lines.append("")
        
        if example.related_commands:
            lines.append("### Related Commands")
            lines.append("")
            for cmd in example.related_commands:
                lines.append(f"- `{cmd}`")
            lines.append("")
        
        lines.append("### Expected Output")
        lines.append("")
        lines.append(example.expected_output)
        
        return lines
