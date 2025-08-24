"""
Core coherence validation engine - extracted and adapted from OM validation components.
This is the foundation that enables building coherent tools.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class CoherenceLevel(Enum):
    """Coherence quality levels"""
    INCOHERENT = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    PERFECT = 4


@dataclass
class CoherenceResult:
    """Result of coherence validation"""
    level: CoherenceLevel
    score: float  # 0.0 to 1.0
    contradictions: List[str]
    reasoning_chain: List[str]
    confidence: float


class LogicalCoherenceValidator:
    """
    Core coherence validation engine.
    Measures logical consistency without generating content.
    """
    
    def __init__(self):
        self.contradiction_patterns = [
            r"(?i)(not|never|no)\s+.*\s+(always|must|will)",
            r"(?i)(impossible|cannot)\s+.*\s+(will|must|always)",
            r"(?i)(all|every|always)\s+.*\s+(none|never|no)",
            r"(?i)(true|fact|certain)\s+.*\s+(false|wrong|incorrect)",
        ]
        
    def validate_reasoning_chain(self, reasoning_steps: List[str]) -> CoherenceResult:
        """Validate a chain of reasoning for logical consistency"""
        contradictions = []
        reasoning_chain = []
        
        for i, step in enumerate(reasoning_steps):
            # Check for internal contradictions in this step
            step_contradictions = self._detect_contradictions(step)
            contradictions.extend([f"Step {i+1}: {c}" for c in step_contradictions])
            
            # Check for contradictions with previous steps
            for j, prev_step in enumerate(reasoning_steps[:i]):
                cross_contradictions = self._detect_cross_contradictions(prev_step, step)
                contradictions.extend([f"Steps {j+1}-{i+1}: {c}" for c in cross_contradictions])
            
            reasoning_chain.append(f"Step {i+1}: {step}")
        
        # Calculate coherence score
        score = self._calculate_coherence_score(reasoning_steps, contradictions)
        level = self._score_to_level(score)
        confidence = self._calculate_confidence(reasoning_steps, contradictions)
        
        return CoherenceResult(
            level=level,
            score=score,
            contradictions=contradictions,
            reasoning_chain=reasoning_chain,
            confidence=confidence
        )
    
    def validate_statement(self, statement: str) -> CoherenceResult:
        """Validate a single statement for internal coherence"""
        contradictions = self._detect_contradictions(statement)
        
        score = 1.0 if not contradictions else max(0.0, 1.0 - len(contradictions) * 0.3)
        level = self._score_to_level(score)
        confidence = 0.9 if len(statement.split()) > 5 else 0.6
        
        return CoherenceResult(
            level=level,
            score=score,
            contradictions=contradictions,
            reasoning_chain=[statement],
            confidence=confidence
        )
    
    def _detect_contradictions(self, text: str) -> List[str]:
        """Detect logical contradictions within a single text"""
        contradictions = []
        
        # Pattern-based contradiction detection
        for pattern in self.contradiction_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                contradictions.append(f"Contradiction pattern: {match.group()}")
        
        # Semantic contradiction detection (simplified)
        words = text.lower().split()
        
        # Check for direct opposites
        opposites = [
            ("always", "never"), ("all", "none"), ("true", "false"),
            ("possible", "impossible"), ("can", "cannot"), ("will", "won't")
        ]
        
        for pos, neg in opposites:
            if pos in words and neg in words:
                contradictions.append(f"Direct contradiction: '{pos}' and '{neg}' in same statement")
        
        return contradictions
    
    def _detect_cross_contradictions(self, statement1: str, statement2: str) -> List[str]:
        """Detect contradictions between two statements"""
        contradictions = []
        
        # Simple semantic contradiction detection
        s1_words = set(statement1.lower().split())
        s2_words = set(statement2.lower().split())
        s1_lower = statement1.lower()
        s2_lower = statement2.lower()
        
        # Check for negation patterns
        if "not" in s1_words and any(word in s2_words for word in s1_words if word != "not"):
            if not ("not" in s2_words):
                contradictions.append("Negation contradiction between statements")
        
        # Check for logical contradictions in reasoning
        # "All X are Y" vs "X contains non-Y"
        if ("all" in s1_lower or "every" in s1_lower) and ("contain" in s2_lower or "have" in s2_lower):
            if any(word in s1_lower for word in ["perfect", "logical", "consistent"]):
                if any(word in s2_lower for word in ["contradiction", "error", "inconsistent"]):
                    contradictions.append("Universal claim contradicted by existence claim")
        
        # "No X exist" vs "We are using X"
        if ("no" in s1_lower and "exist" in s1_lower) or ("none" in s1_lower):
            if any(word in s2_lower for word in ["using", "have", "current", "this"]):
                contradictions.append("Existence denial contradicted by usage claim")
        
        # "Impossible" vs "Therefore/Thus" (claiming impossible conclusion)
        if "impossible" in s1_lower or "cannot" in s1_lower:
            if "therefore" in s2_lower or "thus" in s2_lower:
                contradictions.append("Impossible premise leads to definitive conclusion")
        
        return contradictions
    
    def _calculate_coherence_score(self, reasoning_steps: List[str], contradictions: List[str]) -> float:
        """Calculate overall coherence score"""
        if not reasoning_steps:
            return 0.0
        
        base_score = 1.0
        
        # Heavy penalty for contradictions in reasoning chains
        if contradictions:
            # Each contradiction is a major logical flaw
            contradiction_penalty = len(contradictions) * 0.4
            # Additional penalty for cross-step contradictions (more severe)
            cross_contradictions = [c for c in contradictions if "between" in c or "Steps" in c]
            contradiction_penalty += len(cross_contradictions) * 0.3
        else:
            contradiction_penalty = 0.0
        
        # Bonus for longer, more detailed reasoning
        length_bonus = min(0.2, len(reasoning_steps) * 0.05)
        
        # Penalty for very short or vague statements
        avg_length = sum(len(step.split()) for step in reasoning_steps) / len(reasoning_steps)
        if avg_length < 5:
            base_score -= 0.3
        
        final_score = max(0.0, base_score - contradiction_penalty + length_bonus)
        return min(1.0, final_score)
    
    def _score_to_level(self, score: float) -> CoherenceLevel:
        """Convert numeric score to coherence level"""
        if score >= 0.9:
            return CoherenceLevel.PERFECT
        elif score >= 0.7:
            return CoherenceLevel.HIGH
        elif score >= 0.5:
            return CoherenceLevel.MEDIUM
        elif score >= 0.3:
            return CoherenceLevel.LOW
        else:
            return CoherenceLevel.INCOHERENT
    
    def _calculate_confidence(self, reasoning_steps: List[str], contradictions: List[str]) -> float:
        """Calculate confidence in the coherence assessment"""
        base_confidence = 0.8
        
        # Higher confidence with more text to analyze
        text_bonus = min(0.2, len(reasoning_steps) * 0.05)
        
        # Lower confidence if many contradictions (might be missing context)
        contradiction_penalty = len(contradictions) * 0.1
        
        return max(0.1, min(1.0, base_confidence + text_bonus - contradiction_penalty))


# Factory function for easy instantiation
def create_coherence_validator() -> LogicalCoherenceValidator:
    """Create a new coherence validator instance"""
    return LogicalCoherenceValidator()