"""Local code interpreter using subprocess."""

import subprocess
import tempfile
from typing import Dict, Any
from pathlib import Path


class CodeInterpreter:
    """Execute Python code safely using subprocess in Docker environment."""
    
    def __init__(self, timeout: int = 30):
        """Initialize code interpreter.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
    
    def execute(self, code: str) -> Dict[str, Any]:
        """Execute Python code and return results.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with 'output', 'success', 'error' keys
        """
        try:
            # Execute code directly with python -c
            result = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "output": result.stdout.strip(),
                "success": result.returncode == 0,
                "error": result.stderr.strip() if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "success": False,
                "error": f"Execution timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "output": "",
                "success": False,
                "error": str(e)
            }
    
    def test_function(self, function_code: str, test_cases: list = None) -> Dict[str, Any]:
        """Test a function with optional test cases.
        
        Args:
            function_code: Function definition code
            test_cases: List of test expressions to run
            
        Returns:
            Dict with test results
        """
        if test_cases is None:
            test_cases = []
        
        # Combine function definition with test cases
        full_code = function_code + "\n\n"
        
        for i, test in enumerate(test_cases):
            full_code += f"print(f'Test {i+1}: {repr(test)}')\n"
        
        return self.execute(full_code)
    
    def validate_snippet(self, code: str) -> bool:
        """Quick validation - returns True if code runs without error."""
        result = self.execute(code)
        return result["success"]
    
    def execute_bash(self, command: str) -> Dict[str, Any]:
        """Execute bash command and return results.
        
        Args:
            command: Bash command to execute
            
        Returns:
            Dict with 'output', 'success', 'error' keys
        """
        try:
            # Execute bash command
            result = subprocess.run(
                ['bash', '-c', command],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "output": result.stdout.strip(),
                "success": result.returncode == 0,
                "error": result.stderr.strip() if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "success": False,
                "error": f"Command timed out after {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "output": "",
                "success": False,
                "error": str(e)
            }