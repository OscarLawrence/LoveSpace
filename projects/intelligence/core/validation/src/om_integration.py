"""Integration hooks for OM workflow system"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add OM tools to path
om_path = Path(__file__).parent.parent.parent / "tools" / "om"
if om_path.exists():
    sys.path.insert(0, str(om_path))

from .logical_coherence_validator import LogicalCoherenceValidator, CoherenceResult


class OMIntegration:
    """Integrates logical coherence validation with OM workflow"""
    
    def __init__(self):
        self.validator = LogicalCoherenceValidator()
        self.om_scoped_cli_path = self._find_scoped_cli()
        
    def _find_scoped_cli(self) -> Optional[str]:
        """Locate scoped_cli.py in OM tools"""
        om_src = Path(__file__).parent.parent.parent / "tools" / "om" / "src"
        if om_src.exists():
            for file in om_src.rglob("scoped_cli.py"):
                return str(file)
        return None
    
    def validate_before_execution(self, command: str, context: Dict[str, Any]) -> CoherenceResult:
        """Hook to validate commands before OM execution"""
        # Extract workspace context
        workspace_context = self._extract_workspace_context(context)
        
        # Validate coherence
        result = self.validator.validate_request_coherence(command, workspace_context)
        
        # Log validation result
        self._log_validation(command, result)
        
        return result
    
    def should_halt_execution(self, result: CoherenceResult) -> bool:
        """Determine if execution should be halted based on coherence"""
        return not result.is_coherent or result.score < 0.5
    
    def inject_validation_hook(self) -> bool:
        """Inject validation into scoped_cli.py process_command method"""
        if not self.om_scoped_cli_path or not os.path.exists(self.om_scoped_cli_path):
            return False
            
        try:
            # Read current scoped_cli.py
            with open(self.om_scoped_cli_path, 'r') as f:
                content = f.read()
            
            # Check if already injected
            if 'logical_coherence_validation' in content:
                return True
                
            # Find process_command method
            hook_code = '''
        # Logical coherence validation hook
        from projects.core.validation.om_integration import OMIntegration
        om_integration = OMIntegration()
        coherence_result = om_integration.validate_before_execution(command, locals())
        if om_integration.should_halt_execution(coherence_result):
            print(f"HALTED: {coherence_result.contradictions}")
            return False
'''
            
            # Insert hook at start of process_command method
            if 'def process_command(' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'def process_command(' in line:
                        # Find method body start
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() and not lines[j].startswith(' ' * 4):
                                break
                            if lines[j].strip() and lines[j].startswith(' ' * 4):
                                lines.insert(j, hook_code)
                                break
                        break
                
                # Write back
                with open(self.om_scoped_cli_path, 'w') as f:
                    f.write('\n'.join(lines))
                return True
                
        except Exception as e:
            print(f"Failed to inject validation hook: {e}")
            return False
        
        return False
    
    def _extract_workspace_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant workspace information for validation"""
        workspace_context = {}
        
        # Get workspace files
        if 'workspace' in context:
            workspace_context['workspace_files'] = set()
            workspace_path = Path(context.get('workspace', '.'))
            if workspace_path.exists():
                for file in workspace_path.rglob('*'):
                    if file.is_file():
                        workspace_context['workspace_files'].add(str(file))
        
        # Get dependencies from pyproject.toml files
        workspace_context['dependencies'] = {}
        for pyproject in Path('.').rglob('pyproject.toml'):
            try:
                import tomllib
                with open(pyproject, 'rb') as f:
                    data = tomllib.load(f)
                deps = data.get('tool', {}).get('uv', {}).get('dependencies', [])
                for dep in deps:
                    if '==' in dep:
                        name, version = dep.split('==', 1)
                        workspace_context['dependencies'][name] = version
            except:
                pass
                
        return workspace_context
    
    def _log_validation(self, command: str, result: CoherenceResult):
        """Log validation results for analytics"""
        log_entry = {
            'command': command[:100],  # Truncate for privacy
            'coherence_score': result.score,
            'contradictions_count': len(result.contradictions),
            'impossibilities_count': len(result.impossibilities),
            'is_coherent': result.is_coherent
        }
        
        # Simple file logging
        log_file = Path('.') / 'coherence_validation.log'
        try:
            import json
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
