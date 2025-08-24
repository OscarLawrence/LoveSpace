"""Tests for Sphinx Auto-Generation System."""

import pytest
import tempfile
import ast
from pathlib import Path
from unittest.mock import patch, MagicMock

from om.sphinx_auto import (
    CodeAnalyzer, SphinxGenerator, DocumentationBuilder,
    CodeElement
)
from om.docless_architecture import CodeDocumentationExtractor, DoclessSphinxGenerator


class TestCodeAnalyzer:
    """Test code analysis functionality."""
    
    def setup_method(self):
        self.analyzer = CodeAnalyzer()
    
    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        code = '''
def hello_world(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.analyzer.analyze_file(Path(f.name))
            
            # Should find module and function
            assert len(elements) >= 2
            
            func_element = next((e for e in elements if e.type == 'function'), None)
            assert func_element is not None
            assert func_element.name == 'hello_world'
            assert 'name: str' in func_element.signature
            assert '-> str' in func_element.signature
            assert func_element.docstring == "Say hello to someone."
        
        Path(f.name).unlink()
    
    def test_analyze_class_with_methods(self):
        """Test analyzing a class with methods."""
        code = '''
class Calculator:
    """A simple calculator."""
    
    def __init__(self, precision: int = 2):
        self.precision = precision
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return round(a + b, self.precision)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            elements = self.analyzer.analyze_file(Path(f.name))
            
            class_element = next((e for e in elements if e.type == 'class'), None)
            assert class_element is not None
            assert class_element.name == 'Calculator'
            assert class_element.docstring == "A simple calculator."
            
            # Check methods are found
            methods = [e for e in elements if e.type == 'function']
            method_names = [m.name for m in methods]
            assert '__init__' in method_names
            assert 'add' in method_names
        
        Path(f.name).unlink()
    
    def test_complexity_calculation(self):
        """Test complexity calculation."""
        simple_code = '''
def simple():
    return 1
'''
        
        complex_code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = i / 2
                except ZeroDivisionError:
                    result = 0
    return result
'''
        
        # Test simple function
        tree = ast.parse(simple_code)
        func_node = tree.body[0]
        simple_complexity = self.analyzer._calculate_complexity(func_node)
        assert simple_complexity == 1
        
        # Test complex function
        tree = ast.parse(complex_code)
        func_node = tree.body[0]
        complex_complexity = self.analyzer._calculate_complexity(func_node)
        assert complex_complexity > 3


class TestSphinxGenerator:
    """Test Sphinx documentation generation."""
    
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = SphinxGenerator(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_generate_conf_py(self):
        """Test conf.py generation."""
        conf_path = self.generator._generate_conf_py()
        
        assert conf_path.exists()
        content = conf_path.read_text()
        assert 'project =' in content
        assert 'sphinx.ext.autodoc' in content
        assert 'html_theme' in content
    
    def test_generate_index_rst(self):
        """Test index.rst generation."""
        # Add some sample elements
        elements = [
            CodeElement('test_module', 'module', 'module test_module', 
                       Path('test.py'), 1, 'Test module'),
            CodeElement('TestClass', 'class', 'class TestClass', 
                       Path('test.py'), 5, 'Test class')
        ]
        self.generator.add_elements(elements)
        
        index_path = self.generator._generate_index()
        
        assert index_path.exists()
        content = index_path.read_text()
        assert 'Om Documentation' in content
        assert 'test' in content  # Uses source_file.stem
    
    def test_generate_module_docs(self):
        """Test module documentation generation."""
        elements = [
            CodeElement('example', 'module', 'module example', 
                       Path('example.py'), 1, 'Example module'),
            CodeElement('ExampleClass', 'class', 'class ExampleClass', 
                       Path('example.py'), 5, 'Example class'),
            CodeElement('example_function', 'function', 'def example_function()', 
                       Path('example.py'), 10, 'Example function')
        ]
        self.generator.add_elements(elements)
        
        module_files = self.generator._generate_module_docs()
        
        assert 'example.rst' in module_files
        example_file = module_files['example.rst']
        assert example_file.exists()
        
        content = example_file.read_text()
        assert 'example' in content
        assert 'ExampleClass' in content
        assert 'example_function' in content


class TestDocumentationBuilder:
    """Test complete documentation building."""
    
    def setup_method(self):
        self.source_dir = Path(tempfile.mkdtemp())
        self.output_dir = Path(tempfile.mkdtemp())
        self.builder = DocumentationBuilder(self.source_dir, self.output_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.output_dir)
    
    def test_build_documentation_from_source(self):
        """Test building documentation from source directory."""
        # Create sample Python files
        (self.source_dir / 'module1.py').write_text('''
"""Module 1 documentation."""

def function1():
    """Function 1."""
    pass

class Class1:
    """Class 1."""
    pass
''')
        
        (self.source_dir / 'module2.py').write_text('''
"""Module 2 documentation."""

def function2(x: int) -> str:
    """Function 2."""
    return str(x)
''')
        
        result = self.builder.build_documentation()
        
        assert 'generated_files' in result
        assert 'analysis_stats' in result
        
        stats = result['analysis_stats']
        assert stats['files_processed'] == 2
        assert stats['elements_found'] > 0
        
        # Check generated files
        generated = result['generated_files']
        assert 'conf.py' in generated
        assert 'index.rst' in generated
        assert 'Makefile' in generated


class TestDoclessArchitecture:
    """Test docless architecture implementation."""
    
    def setup_method(self):
        self.extractor = CodeDocumentationExtractor()
    
    def test_infer_purpose_from_name(self):
        """Test purpose inference from function names."""
        assert "Retrieves user data" in self.extractor._infer_purpose_from_name('get_user_data')
        assert "Creates new session" in self.extractor._infer_purpose_from_name('create_new_session')
        assert "Validates input" in self.extractor._infer_purpose_from_name('validate_input')
        assert "Checks if valid" in self.extractor._infer_purpose_from_name('is_valid')
    
    def test_infer_parameter_purpose(self):
        """Test parameter purpose inference."""
        # Test with type annotation
        annotation = ast.parse('str').body[0].value
        purpose = self.extractor._infer_parameter_purpose('file_path', annotation)
        assert 'File path' in purpose
        assert 'string value' in purpose
        
        # Test without annotation
        purpose = self.extractor._infer_parameter_purpose('config_option', None)
        assert 'configuration' in purpose.lower()
    
    def test_extract_function_docs(self):
        """Test extracting documentation from function."""
        code = '''
def calculate_total(items: list, tax_rate: float = 0.1) -> float:
    total = 0
    for item in items:
        total += item.price
    return total * (1 + tax_rate)
'''
        
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        docs = self.extractor.extract_function_docs(func_node, code)
        
        assert 'calculate' in docs.purpose.lower()
        assert 'total' in docs.purpose.lower()
        assert 'items' in docs.parameters
        assert 'tax_rate' in docs.parameters
        assert 'float' in docs.returns
    
    def test_extract_class_docs(self):
        """Test extracting documentation from class."""
        code = '''
class UserManager:
    def __init__(self, database_url: str):
        self.db_url = database_url
    
    def create_user(self, name: str):
        pass
    
    def delete_user(self, user_id: int):
        pass
'''
        
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        docs = self.extractor.extract_class_docs(class_node, code)
        
        assert 'user' in docs.purpose.lower()
        assert 'manager' in docs.purpose.lower()
        assert 'methods' in docs.behavior
        assert 'create_user' in docs.behavior


class TestDoclessSphinxGenerator:
    """Test docless Sphinx generation."""
    
    def setup_method(self):
        self.extractor = CodeDocumentationExtractor()
        self.generator = DoclessSphinxGenerator(self.extractor)
    
    def test_generate_rst_for_function(self):
        """Test RST generation for function."""
        code = '''
def process_data(input_file: str, output_dir: str) -> bool:
    # Process the data
    return True
'''
        
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        rst = self.generator.generate_rst_for_function(func_node, code)
        
        assert 'process_data' in rst
        assert 'Purpose:' in rst
        assert 'Parameters:' in rst
        assert 'input_file' in rst
        assert 'output_dir' in rst
        assert 'Returns:' in rst
    
    def test_generate_rst_for_class(self):
        """Test RST generation for class."""
        code = '''
class DataProcessor:
    def __init__(self):
        pass
    
    def process(self):
        pass
'''
        
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        rst = self.generator.generate_rst_for_class(class_node, code)
        
        assert 'DataProcessor' in rst
        assert 'Purpose:' in rst
        assert 'Behavior:' in rst
        assert 'Complexity:' in rst


if __name__ == "__main__":
    pytest.main([__file__, "-v"])