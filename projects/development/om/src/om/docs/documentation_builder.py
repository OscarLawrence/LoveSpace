"""Documentation builder for coordinating the documentation generation process."""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from .code_analyzer import CodeAnalyzer, CodeElement
from .sphinx_generator import SphinxGenerator


class DocumentationBuilder:
    """Coordinates the complete documentation building process."""
    
    def __init__(self, source_dir: Path, output_dir: Path, project_name: str = "Project"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.project_name = project_name
        self.analyzer = CodeAnalyzer()
        self.generator = SphinxGenerator(output_dir)
        self.elements: List[CodeElement] = []
    
    def build_documentation(self, file_patterns: List[str] = None) -> bool:
        """Build complete documentation from source files."""
        try:
            # Step 1: Analyze source files
            self._analyze_source_files(file_patterns or ["**/*.py"])
            
            # Step 2: Generate Sphinx documentation
            success = self.generator.generate_documentation(self.elements, self.project_name)
            if not success:
                return False
            
            # Step 3: Build HTML output
            return self.generator.build_html()
            
        except Exception as e:
            print(f"Documentation build failed: {e}")
            return False
    
    def _analyze_source_files(self, patterns: List[str]):
        """Analyze all source files matching the given patterns."""
        self.elements = []
        
        for pattern in patterns:
            for file_path in self.source_dir.rglob(pattern):
                if self._should_analyze_file(file_path):
                    elements = self.analyzer.analyze_file(file_path)
                    self.elements.extend(elements)
        
        print(f"Analyzed {len(self.elements)} code elements from {len(set(e.source_file for e in self.elements))} files")
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed."""
        # Skip common non-source directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        # Skip test files for now (could be configurable)
        if 'test_' in file_path.name or file_path.name.endswith('_test.py'):
            return False
        
        # Only analyze Python files
        return file_path.suffix == '.py'
    
    def generate_coverage_report(self) -> Dict[str, any]:
        """Generate documentation coverage report."""
        total_elements = len(self.elements)
        documented_elements = len([e for e in self.elements if e.docstring and e.docstring.strip()])
        
        coverage = (documented_elements / total_elements * 100) if total_elements > 0 else 0
        
        # Group by type
        by_type = {}
        for element in self.elements:
            if element.type not in by_type:
                by_type[element.type] = {'total': 0, 'documented': 0}
            
            by_type[element.type]['total'] += 1
            if element.docstring and element.docstring.strip():
                by_type[element.type]['documented'] += 1
        
        # Calculate coverage by type
        for type_name, stats in by_type.items():
            stats['coverage'] = (stats['documented'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        return {
            'total_elements': total_elements,
            'documented_elements': documented_elements,
            'overall_coverage': coverage,
            'by_type': by_type,
            'files_analyzed': len(set(e.source_file for e in self.elements))
        }
    
    def export_elements_json(self, output_path: Path) -> bool:
        """Export analyzed elements to JSON for external processing."""
        try:
            import json
            
            elements_data = []
            for element in self.elements:
                elements_data.append({
                    'name': element.name,
                    'type': element.type,
                    'signature': element.signature,
                    'source_file': str(element.source_file),
                    'line_number': element.line_number,
                    'docstring': element.docstring,
                    'complexity': element.complexity,
                    'dependencies': element.dependencies,
                    'annotations': element.annotations
                })
            
            with open(output_path, 'w') as f:
                json.dump(elements_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to export elements: {e}")
            return False


def batch_parse_with_sphinx(source_dir: Path, output_dir: Path = None, project_name: str = "Project") -> Dict[str, any]:
    """Batch parse source directory and generate Sphinx documentation."""
    if output_dir is None:
        output_dir = source_dir / "docs"
    
    builder = DocumentationBuilder(source_dir, output_dir, project_name)
    
    try:
        success = builder.build_documentation()
        coverage = builder.generate_coverage_report()
        
        return {
            "status": "success" if success else "failed",
            "total_files": coverage['files_analyzed'],
            "functions_extracted": sum(1 for e in builder.elements if e.type in ('function', 'async_function')),
            "classes_extracted": sum(1 for e in builder.elements if e.type == 'class'),
            "patterns_extracted": len(builder.elements),
            "errors": 0,  # Could be enhanced to track actual errors
            "enhancement_rate": coverage['overall_coverage'],
            "output_dir": str(output_dir)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "total_files": 0,
            "functions_extracted": 0,
            "classes_extracted": 0,
            "patterns_extracted": 0,
            "errors": 1,
            "enhancement_rate": 0
        }