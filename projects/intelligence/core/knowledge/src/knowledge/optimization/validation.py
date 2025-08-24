"""
Decision validation for optimization
"""

import asyncio
from typing import Dict, Any

from .data_models import OptimizationContext, OptimizationDecision


class DecisionValidator:
    """Validates optimization decisions before execution"""
    
    def __init__(self):
        self.validation_rules = {
            "confidence_threshold": 0.1,
            "improvement_threshold": 0.01,
            "parameter_bounds": {
                "batch_size": (1, 512),
                "learning_rate": (1e-6, 1.0),
                "threads": (1, 32)
            }
        }
    
    async def validate_decision(self, decision: OptimizationDecision, 
                              context: OptimizationContext) -> OptimizationDecision:
        """Validate optimization decision"""
        validated_decision = decision
        
        # Check confidence threshold
        if decision.confidence < self.validation_rules["confidence_threshold"]:
            validated_decision.confidence = self.validation_rules["confidence_threshold"]
            validated_decision.reasoning += " (confidence adjusted to minimum threshold)"
        
        # Check improvement threshold
        if decision.expected_improvement < self.validation_rules["improvement_threshold"]:
            validated_decision.expected_improvement = self.validation_rules["improvement_threshold"]
            validated_decision.reasoning += " (improvement adjusted to minimum threshold)"
        
        # Validate parameter bounds
        validated_parameters = {}
        for param, value in decision.parameters.items():
            if param in self.validation_rules["parameter_bounds"]:
                min_val, max_val = self.validation_rules["parameter_bounds"][param]
                validated_value = max(min_val, min(max_val, value))
                validated_parameters[param] = validated_value
            else:
                validated_parameters[param] = value
        
        validated_decision.parameters = validated_parameters
        
        # Check constraint compliance
        constraint_violations = self._check_constraint_compliance(validated_decision, context)
        if constraint_violations:
            validated_decision.reasoning += f" (constraints adjusted: {', '.join(constraint_violations)})"
        
        return validated_decision
    
    def _check_constraint_compliance(self, decision: OptimizationDecision, 
                                   context: OptimizationContext) -> list:
        """Check if decision complies with system constraints"""
        violations = []
        
        for constraint_name, constraint_value in context.system_constraints.items():
            if constraint_name in decision.parameters:
                param_value = decision.parameters[constraint_name]
                
                if isinstance(constraint_value, dict):
                    min_val = constraint_value.get("min")
                    max_val = constraint_value.get("max")
                    
                    if min_val and param_value < min_val:
                        decision.parameters[constraint_name] = min_val
                        violations.append(f"{constraint_name} raised to minimum")
                    
                    if max_val and param_value > max_val:
                        decision.parameters[constraint_name] = max_val
                        violations.append(f"{constraint_name} lowered to maximum")
        
        return violations
