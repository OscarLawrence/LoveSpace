"""
OM Integration Module

Integrates validation system with OM workflow pipeline.
Provides hooks for validation at key decision points.
"""

import json
from typing import Dict, List, Optional, Any
from .logical_coherence_validator import LogicalCoherenceValidator
from .prerequisite_checker import PrerequisiteChecker
from .token_efficiency_optimizer import TokenEfficiencyOptimizer
from .auto_halt_controller import AutoHaltController
from .validation_models import ValidationResult


class OMIntegration:
    """
    Integrates validation system with OM workflow.
    
    Provides:
    - Pre-command validation
    - Post-command verification
    - Continuous monitoring
    - Quality gates
    - Recovery mechanisms
    """
    
    def __init__(self, workspace_root: str = None):
        self.coherence_validator = LogicalCoherenceValidator()
        self.prerequisite_checker = PrerequisiteChecker(workspace_root)
        self.token_optimizer = TokenEfficiencyOptimizer()
        self.halt_controller = AutoHaltController()
        
    def validate_command_request(self, command: str, args: List[str], context: Dict = None) -> ValidationResult:
        """Validate command request before execution."""
        request_text = f"{command} {' '.join(args)}"
        
        # Logical coherence validation
        coherence_issues = self.coherence_validator.validate_request(request_text, context)
        
        # Prerequisite checking
        prerequisite_status = self.prerequisite_checker.check_prerequisites(request_text, context)
        
        # Token analysis
        token_analysis = self.token_optimizer.analyze_request(request_text, context)
        
        # Check halt conditions
        halt_context = {
            'request': request_text,
            'coherence_result': {'is_coherent': len(coherence_issues) == 0},
            'prerequisites': [p.__dict__ for p in prerequisite_status],
            'token_analysis': token_analysis.__dict__,
            'context': context or {}
        }
        
        halt_event = self.halt_controller.check_halt_conditions(halt_context)
        halt_events = [halt_event] if halt_event else []
        
        # Calculate overall validation score
        overall_score = self._calculate_overall_score(
            coherence_issues, prerequisite_status, token_analysis, halt_events
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            coherence_issues, prerequisite_status, token_analysis
        )
        
        is_valid = overall_score > 0.7 and len(halt_events) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            coherence_issues=coherence_issues,
            prerequisite_status=prerequisite_status,
            token_analysis=token_analysis,
            halt_events=halt_events,
            overall_score=overall_score,
            recommendations=recommendations
        )
    
    def optimize_command_request(self, command: str, args: List[str]) -> tuple[str, List[str]]:
        """Optimize command request for efficiency."""
        request_text = f"{command} {' '.join(args)}"
        optimized_text = self.token_optimizer.optimize_request(request_text)
        
        # Parse back into command and args
        parts = optimized_text.split()
        optimized_command = parts[0] if parts else command
        optimized_args = parts[1:] if len(parts) > 1 else args
        
        return optimized_command, optimized_args
    
    def pre_command_hook(self, command: str, args: List[str], context: Dict = None) -> bool:
        """Hook called before command execution."""
        validation_result = self.validate_command_request(command, args, context)
        
        # Log validation result
        self._log_validation_result(command, validation_result)
        
        # Return whether command should proceed
        return validation_result.is_valid
    
    def post_command_hook(self, command: str, result: Any, context: Dict = None) -> Dict:
        """Hook called after command execution."""
        # Verify expected outcomes
        verification_result = self._verify_command_outcome(command, result, context)
        
        # Update token usage
        if hasattr(result, 'token_usage'):
            self.token_optimizer.used_tokens += getattr(result, 'token_usage', 0)
        
        return verification_result
    
    def continuous_monitoring_hook(self, context: Dict) -> Optional[Dict]:
        """Hook for continuous monitoring during execution."""
        # Check system health
        system_health = self._check_system_health(context)
        
        # Check for degradation patterns
        degradation_detected = self._check_degradation_patterns(context)
        
        if system_health['critical_issues'] or degradation_detected:
            return {
                'action': 'halt',
                'reason': 'System health degradation detected',
                'details': system_health
            }
        
        return None
    
    def _calculate_overall_score(self, coherence_issues, prerequisite_status, 
                                token_analysis, halt_events) -> float:
        """Calculate overall validation score."""
        base_score = 1.0
        
        # Coherence penalty
        high_severity_issues = sum(1 for issue in coherence_issues if issue.severity.value in ['high', 'critical'])
        coherence_penalty = high_severity_issues * 0.2
        
        # Prerequisite penalty
        unsatisfied_prereqs = sum(1 for status in prerequisite_status if not status.satisfied)
        prerequisite_penalty = unsatisfied_prereqs * 0.15
        
        # Token efficiency factor
        efficiency_factor = token_analysis.efficiency_score
        
        # Halt event penalty
        halt_penalty = len(halt_events) * 0.5
        
        final_score = base_score - coherence_penalty - prerequisite_penalty - halt_penalty
        final_score *= efficiency_factor
        
        return max(0.0, min(1.0, final_score))
    
    def _generate_recommendations(self, coherence_issues, prerequisite_status, token_analysis) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Coherence recommendations
        if coherence_issues:
            recommendations.append("Review request for logical consistency")
            
        # Prerequisite recommendations
        unsatisfied = [p for p in prerequisite_status if not p.satisfied]
        if unsatisfied:
            recommendations.append(f"Address {len(unsatisfied)} missing prerequisites")
            
        # Token efficiency recommendations
        if token_analysis.efficiency_score < 0.5:
            recommendations.extend(token_analysis.optimization_suggestions[:2])
        
        return recommendations
    
    def _verify_command_outcome(self, command: str, result: Any, context: Dict = None) -> Dict:
        """Verify command executed as expected."""
        verification = {
            'command': command,
            'success': True,
            'issues': [],
            'metrics': {}
        }
        
        # Basic success verification
        if hasattr(result, 'success'):
            verification['success'] = result.success
        elif hasattr(result, 'error'):
            verification['success'] = result.error is None
        
        # Command-specific verification
        if command == 'code':
            verification['metrics']['files_processed'] = getattr(result, 'files_processed', 0)
        elif command == 'workspace':
            verification['metrics']['modules_analyzed'] = getattr(result, 'modules_analyzed', 0)
        
        return verification
    
    def _check_system_health(self, context: Dict) -> Dict:
        """Check overall system health."""
        health = {
            'status': 'healthy',
            'warnings': [],
            'critical_issues': []
        }
        
        # Check memory usage
        memory_usage = context.get('memory_usage_percent', 0)
        if memory_usage > 90:
            health['critical_issues'].append(f"High memory usage: {memory_usage}%")
        elif memory_usage > 75:
            health['warnings'].append(f"Moderate memory usage: {memory_usage}%")
        
        # Check token budget
        token_usage = context.get('token_usage_percent', 0)
        if token_usage > 90:
            health['critical_issues'].append(f"Token budget nearly exhausted: {token_usage}%")
        elif token_usage > 75:
            health['warnings'].append(f"High token usage: {token_usage}%")
        
        # Update overall status
        if health['critical_issues']:
            health['status'] = 'critical'
        elif health['warnings']:
            health['status'] = 'warning'
        
        return health
    
    def _check_degradation_patterns(self, context: Dict) -> bool:
        """Check for performance degradation patterns."""
        # Check response time trends
        response_times = context.get('recent_response_times', [])
        if len(response_times) >= 5:
            avg_recent = sum(response_times[-5:]) / 5
            avg_baseline = sum(response_times[:-5]) / max(1, len(response_times) - 5)
            
            if avg_recent > avg_baseline * 2:  # 2x slower
                return True
        
        # Check error rate trends
        error_rates = context.get('recent_error_rates', [])
        if error_rates and error_rates[-1] > 0.1:  # 10% error rate
            return True
        
        return False
    
    def _log_validation_result(self, command: str, result: ValidationResult):
        """Log validation result for analysis."""
        log_entry = {
            'timestamp': json.dumps(result, default=str),
            'command': command,
            'validation_result': result.__dict__
        }
        
        try:
            with open('validation_log.jsonl', 'a') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            print(f"Failed to log validation result: {e}")
    
    def get_validation_metrics(self) -> Dict:
        """Get validation system metrics."""
        return {
            'halt_status': self.halt_controller.get_halt_status(),
            'token_usage': {
                'used': self.token_optimizer.used_tokens,
                'budget': self.token_optimizer.daily_budget,
                'remaining': self.token_optimizer.daily_budget - self.token_optimizer.used_tokens
            },
            'validation_history': len(getattr(self, '_validation_history', []))
        }
