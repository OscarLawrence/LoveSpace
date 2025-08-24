"""
Integration layer connecting our coherence engine with existing OM validation components.
Provides unified interface for all coherence validation needs.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the validation modules to path
validation_path = Path(__file__).parent.parent.parent / "core" / "validation"
if validation_path.exists():
    sys.path.insert(0, str(validation_path.parent))

try:
    from core.validation.logical_coherence_validator import LogicalCoherenceValidator as OMValidator
    from core.validation.coherence_scorer import CoherenceScorer
    from core.validation.contradiction_detector import ContradictionDetector
    OM_AVAILABLE = True
except ImportError:
    OM_AVAILABLE = False
    OMValidator = None
    CoherenceScorer = None
    ContradictionDetector = None

from .validator import LogicalCoherenceValidator, CoherenceResult, CoherenceLevel
from .monitor import CoherenceMonitor


class UnifiedCoherenceEngine:
    """
    Unified coherence engine that combines our new validator with existing OM components.
    Provides the best of both systems.
    """
    
    def __init__(self):
        self.our_validator = LogicalCoherenceValidator()
        self.monitor = CoherenceMonitor(self.our_validator)
        
        # Initialize OM components if available
        self.om_validator = None
        self.om_scorer = None
        self.om_detector = None
        
        if OM_AVAILABLE:
            try:
                self.om_validator = OMValidator()
                self.om_scorer = CoherenceScorer()
                self.om_detector = ContradictionDetector()
                print("✅ OM validation components loaded successfully")
            except Exception as e:
                print(f"⚠️  Could not initialize OM components: {e}")
        else:
            print("ℹ️  OM validation components not available, using built-in validator")
    
    def validate_statement(self, statement: str, use_om: bool = True) -> CoherenceResult:
        """Validate a statement using the best available method"""
        # Always use our validator as baseline
        our_result = self.our_validator.validate_statement(statement)
        
        # If OM is available and requested, enhance with OM validation
        if OM_AVAILABLE and use_om and self.om_validator:
            try:
                # Use OM validator for additional validation
                om_result = self.om_validator.validate(statement)
                
                # Combine results (our validator is primary, OM enhances)
                enhanced_result = self._combine_results(our_result, om_result, statement)
                return enhanced_result
            except Exception as e:
                print(f"⚠️  OM validation failed, using built-in: {e}")
        
        return our_result
    
    def validate_reasoning_chain(self, reasoning_steps: List[str], use_om: bool = True) -> CoherenceResult:
        """Validate a reasoning chain using the best available method"""
        # Always use our validator as baseline
        our_result = self.our_validator.validate_reasoning_chain(reasoning_steps)
        
        # If OM is available, enhance with OM validation
        if OM_AVAILABLE and use_om and self.om_validator:
            try:
                # Validate each step with OM and combine
                om_contradictions = []
                for i, step in enumerate(reasoning_steps):
                    om_result = self.om_validator.validate(step)
                    if hasattr(om_result, 'contradictions'):
                        om_contradictions.extend([f"OM Step {i+1}: {c}" for c in om_result.contradictions])
                
                # Enhance our result with OM findings
                enhanced_contradictions = our_result.contradictions + om_contradictions
                enhanced_score = max(0.0, our_result.score - len(om_contradictions) * 0.1)
                
                return CoherenceResult(
                    level=self.our_validator._score_to_level(enhanced_score),
                    score=enhanced_score,
                    contradictions=enhanced_contradictions,
                    reasoning_chain=our_result.reasoning_chain,
                    confidence=min(our_result.confidence, 0.9)  # Slightly lower confidence when combining
                )
            except Exception as e:
                print(f"⚠️  OM reasoning validation failed, using built-in: {e}")
        
        return our_result
    
    def validate_with_monitoring(self, content: str, source: str = "unknown", 
                               context: Optional[Dict[str, Any]] = None) -> CoherenceResult:
        """Validate with real-time monitoring"""
        return self.monitor.validate_and_monitor(content, source, context)
    
    def start_monitoring(self):
        """Start real-time coherence monitoring"""
        self.monitor.start_monitoring()
    
    def stop_monitoring(self):
        """Stop real-time coherence monitoring"""
        self.monitor.stop_monitoring()
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get coherence monitoring statistics"""
        return self.monitor.get_coherence_statistics()
    
    def _combine_results(self, our_result: CoherenceResult, om_result: Any, statement: str) -> CoherenceResult:
        """Combine our validation result with OM validation result"""
        try:
            # Extract OM contradictions if available
            om_contradictions = []
            if hasattr(om_result, 'contradictions'):
                om_contradictions = [f"OM: {c}" for c in om_result.contradictions]
            elif hasattr(om_result, 'issues'):
                om_contradictions = [f"OM: {issue}" for issue in om_result.issues]
            
            # Combine contradictions
            all_contradictions = our_result.contradictions + om_contradictions
            
            # Adjust score based on OM findings
            om_penalty = len(om_contradictions) * 0.15
            combined_score = max(0.0, our_result.score - om_penalty)
            
            # Determine final level
            final_level = self.our_validator._score_to_level(combined_score)
            
            return CoherenceResult(
                level=final_level,
                score=combined_score,
                contradictions=all_contradictions,
                reasoning_chain=our_result.reasoning_chain,
                confidence=min(our_result.confidence, 0.95)  # High confidence when both agree
            )
        except Exception as e:
            print(f"⚠️  Error combining results: {e}")
            return our_result


# Global engine instance
_global_engine: Optional[UnifiedCoherenceEngine] = None


def get_coherence_engine() -> UnifiedCoherenceEngine:
    """Get or create the global coherence engine"""
    global _global_engine
    if _global_engine is None:
        _global_engine = UnifiedCoherenceEngine()
    return _global_engine


def validate_statement(statement: str, monitor: bool = False) -> CoherenceResult:
    """Convenience function for statement validation"""
    engine = get_coherence_engine()
    if monitor:
        return engine.validate_with_monitoring(statement, "api_call")
    else:
        return engine.validate_statement(statement)


def validate_reasoning(reasoning_steps: List[str], monitor: bool = False) -> CoherenceResult:
    """Convenience function for reasoning chain validation"""
    engine = get_coherence_engine()
    if monitor:
        # For reasoning chains, validate as a single monitored event
        content = " → ".join(reasoning_steps)
        return engine.monitor.validate_reasoning_chain_and_monitor(reasoning_steps, "reasoning_api")
    else:
        return engine.validate_reasoning_chain(reasoning_steps)


def start_coherence_monitoring():
    """Start global coherence monitoring"""
    engine = get_coherence_engine()
    engine.start_monitoring()
    return engine