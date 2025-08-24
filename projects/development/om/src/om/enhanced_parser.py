#!/usr/bin/env python3
"""Enhanced parsing integration with Sphinx autodoc for improved context extraction."""

from pathlib import Path
from typing import Dict, Any

def integrate_sphinx_parser():
    """Integrate Sphinx parser into OM tool for enhanced code analysis."""
    try:
        from code_parser import create_enhanced_parser
        from knowledge.db_manager import ContextDB
        
        # Initialize database
        db = ContextDB()
        
        # Create enhanced parser
        sphinx_parser = create_enhanced_parser(db)
        
        return sphinx_parser, db
        
    except ImportError as e:
        raise RuntimeError(f"Failed to initialize Sphinx parser: {e}")


def parse_with_sphinx(file_path: Path) -> Dict[str, Any]:
    """Parse a single file with Sphinx for enhanced documentation extraction."""
    try:
        sphinx_parser, db = integrate_sphinx_parser()
        
        # Parse file
        results = sphinx_parser.parse_file(file_path)
        
        return {
            "status": "success",
            "results": results,
            "enhanced": True,
            "parser_type": "sphinx_autodoc"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "enhanced": False,
            "parser_type": "fallback"
        }


def batch_parse_with_sphinx(workspace_root: Path) -> Dict[str, Any]:
    """Parse entire workspace with Sphinx for enhanced context extraction."""
    try:
        sphinx_parser, db = integrate_sphinx_parser()
        
        python_files = list(workspace_root.rglob("*.py"))
        
        total_functions = 0
        total_classes = 0
        total_patterns = 0
        errors = 0
        
        for py_file in python_files:
            # Skip certain directories
            if any(skip in str(py_file) for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                continue
                
            results = sphinx_parser.parse_file(py_file)
            
            if "error" in results:
                errors += 1
            else:
                total_functions += results.get("functions", 0)
                total_classes += results.get("classes", 0)
                total_patterns += results.get("patterns", 0)
        
        return {
            "status": "success",
            "total_files": len(python_files),
            "functions_extracted": total_functions,
            "classes_extracted": total_classes,
            "patterns_extracted": total_patterns,
            "errors": errors,
            "enhancement_rate": f"{((len(python_files) - errors) / len(python_files) * 100):.1f}%",
            "parser_type": "sphinx_autodoc_batch"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "parser_type": "batch_fallback"
        }