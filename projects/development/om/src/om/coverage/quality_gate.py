"""
Quality gate enforcement for documentation coverage
"""

from typing import Dict, List, Tuple, Any

from .data_models import CoverageMetrics


class QualityGate:
    """Enforces quality gates for documentation coverage."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'min_coverage': 80.0,
            'min_quality_score': 7.0,
            'max_errors': 0,
            'max_warnings': 10,
            'fail_on_missing_critical': True
        }
    
    def check_quality_gate(self, metrics: CoverageMetrics) -> Tuple[bool, List[str]]:
        """Check if metrics pass quality gate."""
        failures = []
        
        # Check coverage percentage
        if metrics.coverage_percentage < self.config['min_coverage']:
            failures.append(
                f"Coverage {metrics.coverage_percentage:.1f}% below minimum {self.config['min_coverage']}%"
            )
        
        # Check quality score
        if metrics.quality_score < self.config['min_quality_score']:
            failures.append(
                f"Quality score {metrics.quality_score} below minimum {self.config['min_quality_score']}"
            )
        
        # Count issues by severity
        error_count = sum(1 for issue in metrics.issues if issue['severity'] == 'error')
        warning_count = sum(1 for issue in metrics.issues if issue['severity'] == 'warning')
        
        # Check error threshold
        if error_count > self.config['max_errors']:
            failures.append(f"{error_count} errors exceed maximum {self.config['max_errors']}")
        
        # Check warning threshold
        if warning_count > self.config['max_warnings']:
            failures.append(f"{warning_count} warnings exceed maximum {self.config['max_warnings']}")
        
        # Check for critical missing documentation
        if self.config['fail_on_missing_critical']:
            critical_missing = [
                issue for issue in metrics.issues 
                if issue['issue_type'] == 'missing_documentation' 
                and issue['severity'] == 'error'
            ]
            if critical_missing:
                failures.append(f"{len(critical_missing)} critical elements lack documentation")
        
        return len(failures) == 0, failures
    
    def create_config_file(self, output_path: str, custom_config: Dict[str, Any] = None):
        """Create a quality gate configuration file."""
        import json
        
        config = self.config.copy()
        if custom_config:
            config.update(custom_config)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config_file(self, config_path: str):
        """Load quality gate configuration from file."""
        import json
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
