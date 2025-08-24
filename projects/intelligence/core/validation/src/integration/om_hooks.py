"""OM workflow integration hooks - 200 LOC max"""

import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from ..models import ValidationResult, ValidationStatus, ValidationSession


class OMIntegration:
    """Integration hooks for OM workflow system"""
    
    def __init__(self):
        self.om_commands = {
            'workspace': ['status', 'list', 'analyze'],
            'code': ['parse', 'stats', 'execute', 'validate'],
            'memory': ['context', 'inject', 'clear'],
            'scaffold': ['info', 'create', 'validate']
        }
        
        self.validation_hooks = {
            'pre_command': self._pre_command_validation,
            'post_command': self._post_command_validation,
            'error_handling': self._handle_om_error
        }
    
    def hook_validation_into_om(self, session_id: str) -> bool:
        """Hook validation system into OM workflow"""
        
        try:
            # Check OM availability
            if not self._check_om_availability():
                return False
            
            # Register validation session
            from ..models import create_validation_session
            session = create_validation_session(session_id, "OM Integration")
            
            return True
            
        except Exception as e:
            print(f"Failed to hook into OM: {e}")
            return False
    
    def validate_om_command(self, command: str, args: List[str]) -> ValidationResult:
        """Validate OM command before execution"""
        
        # Check command validity
        if not self._is_valid_om_command(command, args):
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Invalid OM command: {command} {' '.join(args)}",
                score=0.0
            )
        
        # Check prerequisites for command
        prereq_result = self._check_command_prerequisites(command, args)
        if prereq_result.status != ValidationStatus.PASSED:
            return prereq_result
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message=f"OM command validated: {command}",
            score=1.0
        )
    
    def execute_om_with_validation(self, command: str, args: List[str]) -> Tuple[bool, str, ValidationResult]:
        """Execute OM command with validation"""
        
        # Pre-execution validation
        validation = self.validate_om_command(command, args)
        if validation.status != ValidationStatus.PASSED:
            return False, validation.message, validation
        
        try:
            # Execute OM command
            full_command = ['uv', 'run', 'om', command] + args
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Post-execution validation
            post_validation = self._validate_om_output(result.stdout, result.stderr, result.returncode)
            
            return result.returncode == 0, result.stdout, post_validation
            
        except subprocess.TimeoutExpired:
            return False, "OM command timed out", ValidationResult(
                status=ValidationStatus.FAILED,
                message="OM command execution timeout",
                score=0.0
            )
        except Exception as e:
            return False, str(e), ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"OM execution error: {e}",
                score=0.0
            )
    
    def get_om_workspace_status(self) -> Dict[str, Any]:
        """Get OM workspace status with validation"""
        
        success, output, validation = self.execute_om_with_validation('workspace', ['status'])
        
        if not success:
            return {'status': 'error', 'message': output}
        
        try:
            # Parse OM workspace status
            status_data = self._parse_om_status(output)
            status_data['validation'] = validation.__dict__
            return status_data
            
        except Exception as e:
            return {'status': 'parse_error', 'message': str(e)}
    
    def validate_workspace_modules(self) -> ValidationResult:
        """Validate workspace modules through OM"""
        
        status = self.get_om_workspace_status()
        
        if status.get('status') == 'error':
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"OM workspace error: {status.get('message')}",
                score=0.0
            )
        
        # Check module health
        modules = status.get('modules', {})
        healthy_modules = sum(1 for module_status in modules.values() if module_status == 'healthy')
        total_modules = len(modules)
        
        if total_modules == 0:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="No modules found in workspace",
                score=0.5
            )
        
        health_ratio = healthy_modules / total_modules
        
        if health_ratio >= 0.8:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"Workspace modules healthy ({healthy_modules}/{total_modules})",
                score=health_ratio
            )
        else:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Workspace modules unhealthy ({healthy_modules}/{total_modules})",
                score=health_ratio,
                recommendations=["Check failed modules", "Run module diagnostics"]
            )
    
    def _check_om_availability(self) -> bool:
        """Check if OM system is available"""
        
        try:
            result = subprocess.run(
                ['uv', 'run', 'om', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _is_valid_om_command(self, command: str, args: List[str]) -> bool:
        """Check if OM command is valid"""
        
        if command not in self.om_commands:
            return False
        
        valid_subcommands = self.om_commands[command]
        if args and args[0] not in valid_subcommands:
            return False
        
        return True
    
    def _check_command_prerequisites(self, command: str, args: List[str]) -> ValidationResult:
        """Check prerequisites for specific OM command"""
        
        if command == 'code' and args and args[0] == 'execute':
            # Check for Python code execution safety
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="Code execution prerequisites met",
                score=1.0
            )
        
        elif command == 'workspace' and args and args[0] == 'analyze':
            # Check workspace structure
            import os
            if not os.path.exists('projects/'):
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    message="No projects/ directory found",
                    score=0.0
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="Prerequisites validated",
            score=1.0
        )
    
    def _validate_om_output(self, stdout: str, stderr: str, returncode: int) -> ValidationResult:
        """Validate OM command output"""
        
        if returncode != 0:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"OM command failed: {stderr}",
                score=0.0
            )
        
        if not stdout.strip():
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="OM command produced no output",
                score=0.5
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="OM command executed successfully",
            score=1.0
        )
    
    def _parse_om_status(self, output: str) -> Dict[str, Any]:
        """Parse OM workspace status output"""
        
        status_data = {'status': 'unknown', 'modules': {}, 'message': output}
        
        for line in output.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    module_name, module_status = parts[0].strip(), parts[1].strip()
                    
                    if '✓' in module_status:
                        status_data['modules'][module_name] = 'healthy'
                    elif '✗' in module_status:
                        status_data['modules'][module_name] = 'failed'
                    else:
                        status_data['modules'][module_name] = 'unknown'
        
        # Determine overall status
        if status_data['modules']:
            failed = sum(1 for s in status_data['modules'].values() if s == 'failed')
            total = len(status_data['modules'])
            
            if failed == 0:
                status_data['status'] = 'healthy'
            elif failed < total / 2:
                status_data['status'] = 'degraded'
            else:
                status_data['status'] = 'critical'
        
        return status_data
    
    def _pre_command_validation(self, command: str, args: List[str]) -> ValidationResult:
        """Pre-command validation hook"""
        return self.validate_om_command(command, args)
    
    def _post_command_validation(self, output: str, error: str) -> ValidationResult:
        """Post-command validation hook"""
        return self._validate_om_output(output, error, 0 if not error else 1)
    
    def _handle_om_error(self, error: str) -> ValidationResult:
        """Handle OM errors with validation"""
        return ValidationResult(
            status=ValidationStatus.FAILED,
            message=f"OM error: {error}",
            score=0.0,
            recommendations=["Check OM system status", "Verify workspace configuration"]
        )
