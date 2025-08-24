"""Logical contradiction detection - 200 LOC max"""

import re
from typing import List, Dict, Set, Tuple, Optional
from .models import ContradictionReport, ValidationResult, ValidationStatus


class ContradictionDetector:
    """Detects logical contradictions in text and code"""
    
    def __init__(self):
        self.contradiction_patterns = {
            'negation': [
                (r'(\w+)\s+is\s+(\w+)', r'(\w+)\s+is\s+not\s+(\w+)'),
                (r'(\w+)\s+can\s+(\w+)', r'(\w+)\s+cannot\s+(\w+)'),
                (r'(\w+)\s+should\s+(\w+)', r'(\w+)\s+should\s+not\s+(\w+)')
            ],
            'boolean': [
                (r'(\w+)\s+=\s+True', r'(\w+)\s+=\s+False'),
                (r'if\s+(\w+):', r'if\s+not\s+(\w+):'),
                (r'(\w+)\s+and\s+(\w+)', r'not\s+(\w+)\s+or\s+not\s+(\w+)')
            ],
            'semantic': [
                ('always', 'never'),
                ('all', 'none'),
                ('required', 'forbidden'),
                ('mandatory', 'optional')
            ]
        }
        
        self.confidence_weights = {
            'exact_negation': 0.9,
            'boolean_contradiction': 0.85,
            'semantic_opposition': 0.7,
            'pattern_match': 0.6
        }
    
    def detect_contradictions(self, text: str, context: str = "") -> List[ContradictionReport]:
        """Detect all contradictions in given text"""
        
        contradictions = []
        sentences = self._split_sentences(text)
        
        # Check each sentence pair for contradictions
        for i, sent_a in enumerate(sentences):
            for j, sent_b in enumerate(sentences[i+1:], i+1):
                contradiction = self._check_sentence_pair(sent_a, sent_b, i, j)
                if contradiction:
                    contradiction.context = context
                    contradictions.append(contradiction)
        
        return contradictions
    
    def validate_logical_consistency(self, statements: List[str]) -> ValidationResult:
        """Validate logical consistency across statements"""
        
        all_contradictions = []
        
        for statement in statements:
            contradictions = self.detect_contradictions(statement)
            all_contradictions.extend(contradictions)
        
        if all_contradictions:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Found {len(all_contradictions)} logical contradictions",
                score=0.0,
                details={'contradictions': [c.__dict__ for c in all_contradictions]}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="No logical contradictions detected",
            score=1.0
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences for analysis"""
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _check_sentence_pair(self, sent_a: str, sent_b: str, line_a: int, line_b: int) -> Optional[ContradictionReport]:
        """Check if two sentences contradict each other"""
        
        # Normalize sentences
        norm_a = self._normalize_sentence(sent_a)
        norm_b = self._normalize_sentence(sent_b)
        
        # Check for direct negation patterns
        negation_result = self._check_negation_patterns(norm_a, norm_b)
        if negation_result:
            return ContradictionReport(
                statement_a=sent_a,
                statement_b=sent_b,
                contradiction_type="direct_negation",
                confidence=negation_result[1],
                context="",
                line_numbers=[line_a, line_b]
            )
        
        # Check for boolean contradictions
        boolean_result = self._check_boolean_patterns(norm_a, norm_b)
        if boolean_result:
            return ContradictionReport(
                statement_a=sent_a,
                statement_b=sent_b,
                contradiction_type="boolean_contradiction",
                confidence=boolean_result[1],
                context="",
                line_numbers=[line_a, line_b]
            )
        
        # Check for semantic contradictions
        semantic_result = self._check_semantic_patterns(norm_a, norm_b)
        if semantic_result:
            return ContradictionReport(
                statement_a=sent_a,
                statement_b=sent_b,
                contradiction_type="semantic_contradiction",
                confidence=semantic_result[1],
                context="",
                line_numbers=[line_a, line_b]
            )
        
        return None
    
    def _normalize_sentence(self, sentence: str) -> str:
        """Normalize sentence for comparison"""
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
        
        # Remove punctuation except essential ones
        normalized = re.sub(r'[^\w\s\-\'\".]', ' ', normalized)
        
        return normalized
    
    def _check_negation_patterns(self, sent_a: str, sent_b: str) -> Optional[Tuple[str, float]]:
        """Check for direct negation patterns"""
        
        for pos_pattern, neg_pattern in self.contradiction_patterns['negation']:
            pos_match = re.search(pos_pattern, sent_a)
            neg_match = re.search(neg_pattern, sent_b)
            
            if pos_match and neg_match:
                # Check if they refer to the same subject
                if pos_match.group(1).lower() == neg_match.group(1).lower():
                    return ("negation_match", self.confidence_weights['exact_negation'])
        
        return None
    
    def _check_boolean_patterns(self, sent_a: str, sent_b: str) -> Optional[Tuple[str, float]]:
        """Check for boolean contradictions"""
        
        for pos_pattern, neg_pattern in self.contradiction_patterns['boolean']:
            if re.search(pos_pattern, sent_a) and re.search(neg_pattern, sent_b):
                return ("boolean_match", self.confidence_weights['boolean_contradiction'])
        
        return None
    
    def _check_semantic_patterns(self, sent_a: str, sent_b: str) -> Optional[Tuple[str, float]]:
        """Check for semantic contradictions"""
        
        for word_a, word_b in self.contradiction_patterns['semantic']:
            if word_a in sent_a and word_b in sent_b:
                # Check if they're in similar contexts
                if self._similar_context(sent_a, sent_b, word_a, word_b):
                    return ("semantic_match", self.confidence_weights['semantic_opposition'])
        
        return None
    
    def _similar_context(self, sent_a: str, sent_b: str, word_a: str, word_b: str) -> bool:
        """Check if contradictory words appear in similar contexts"""
        
        # Extract words around the contradictory terms
        context_a = self._extract_context(sent_a, word_a)
        context_b = self._extract_context(sent_b, word_b)
        
        # Simple overlap check
        overlap = len(set(context_a) & set(context_b))
        return overlap >= 2
    
    def _extract_context(self, sentence: str, target_word: str) -> List[str]:
        """Extract context words around target word"""
        
        words = sentence.split()
        target_idx = -1
        
        for i, word in enumerate(words):
            if target_word in word:
                target_idx = i
                break
        
        if target_idx == -1:
            return []
        
        # Get 2 words before and after
        start = max(0, target_idx - 2)
        end = min(len(words), target_idx + 3)
        
        return words[start:end]
