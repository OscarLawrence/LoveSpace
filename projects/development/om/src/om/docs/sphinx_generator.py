"""Sphinx documentation generator."""

import os
import sys
from pathlib import Path
from typing import Dict, List
from .code_analyzer import CodeElement


class SphinxGenerator:
    """Generates Sphinx documentation from code elements."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_documentation(self, elements: List[CodeElement], project_name: str = "Project") -> bool:
        """Generate complete Sphinx documentation."""
        try:
            # Create Sphinx configuration
            self._create_conf_py(project_name)
            
            # Create index file
            self._create_index_rst(elements, project_name)
            
            # Create module documentation files
            modules = self._group_elements_by_module(elements)
            for module_name, module_elements in modules.items():
                self._create_module_rst(module_name, module_elements)
            
            # Create API reference
            self._create_api_rst(modules)
            
            return True
            
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return False
    
    def _create_conf_py(self, project_name: str):
        """Create Sphinx configuration file."""
        conf_content = f'''"""Sphinx configuration file."""

project = '{project_name}'
copyright = '2024, Auto-generated'
author = 'Auto-generated'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {{
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
'''
        
        conf_path = self.output_dir / 'conf.py'
        with open(conf_path, 'w') as f:
            f.write(conf_content)
    
    def _create_index_rst(self, elements: List[CodeElement], project_name: str):
        """Create main index.rst file."""
        modules = self._group_elements_by_module(elements)
        
        content = f'''{project_name}
{'=' * len(project_name)}

Welcome to {project_name}'s documentation!

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Modules
-------

'''
        
        for module_name in sorted(modules.keys()):
            content += f"* :doc:`modules/{module_name}`\\n"
        
        content += '''

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''
        
        index_path = self.output_dir / 'index.rst'
        with open(index_path, 'w') as f:
            f.write(content)
    
    def _create_module_rst(self, module_name: str, elements: List[CodeElement]):
        """Create documentation for a single module."""
        modules_dir = self.output_dir / 'modules'
        modules_dir.mkdir(exist_ok=True)
        
        content = f'''{module_name}
{'=' * len(module_name)}

.. automodule:: {module_name}
   :members:
   :undoc-members:
   :show-inheritance:

'''
        
        # Add detailed sections for classes and functions
        classes = [e for e in elements if e.type == 'class']
        functions = [e for e in elements if e.type in ('function', 'async_function')]
        
        if classes:
            content += "Classes\\n-------\\n\\n"
            for cls in classes:
                content += f".. autoclass:: {module_name}.{cls.name}\\n"
                content += "   :members:\\n"
                content += "   :undoc-members:\\n"
                content += "   :show-inheritance:\\n\\n"
        
        if functions:
            content += "Functions\\n---------\\n\\n"
            for func in functions:
                content += f".. autofunction:: {module_name}.{func.name}\\n\\n"
        
        module_path = modules_dir / f'{module_name}.rst'
        with open(module_path, 'w') as f:
            f.write(content)
    
    def _create_api_rst(self, modules: Dict[str, List[CodeElement]]):
        """Create API reference file."""
        content = '''API Reference
=============

This page contains the API reference for all modules.

.. toctree::
   :maxdepth: 2

'''
        
        for module_name in sorted(modules.keys()):
            content += f"   modules/{module_name}\\n"
        
        api_path = self.output_dir / 'api.rst'
        with open(api_path, 'w') as f:
            f.write(content)
    
    def _group_elements_by_module(self, elements: List[CodeElement]) -> Dict[str, List[CodeElement]]:
        """Group code elements by their module."""
        modules = {}
        for element in elements:
            if element.type == 'module':
                module_name = element.name
            else:
                # Extract module name from source file
                module_name = element.source_file.stem
            
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(element)
        
        return modules
    
    def build_html(self) -> bool:
        """Build HTML documentation using Sphinx."""
        try:
            import subprocess
            
            # Change to output directory
            original_cwd = os.getcwd()
            os.chdir(self.output_dir)
            
            try:
                # Run sphinx-build
                result = subprocess.run([
                    sys.executable, '-m', 'sphinx',
                    '-b', 'html',
                    '.',  # source directory
                    '_build/html'  # output directory
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Documentation built successfully!")
                    print(f"Output: {self.output_dir / '_build' / 'html' / 'index.html'}")
                    return True
                else:
                    print(f"Sphinx build failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Error building documentation: {e}")
            return False