"""Logical coherence scoring algorithms - 200 LOC max"""

from typing import Dict, List, Tuple, Optional
from .models import CoherenceScore, ValidationResult, ValidationStatus


class CoherenceScorer:
    """Calculates logical coherence scores"""
    
    def __init__(self):
        self.scoring_weights = {
            'contradiction_penalty': 0.4,
            'completeness_bonus': 0.3,
            'pattern_consistency': 0.2,
            'confidence_adjustment': 0.1
        }
        
        self.penalty_scales = {
            'high_confidence_contradiction': 0.8,
            'medium_confidence_contradiction': 0.5,
            'low_confidence_contradiction': 0.2,
            'missing_critical_context': 0.6,
            'inconsistent_patterns': 0.3
        }
        
        self.bonus_scales = {
            'complete_context': 0.2,
            'consistent_patterns': 0.15,
            'high_confidence_validations': 0.1
        }
    
    def calculate_coherence_score(self, contradictions: List, completeness_score: float,
                                 pattern_matches: List, confidence_scores: List[float]) -> CoherenceScore:
        """Calculate overall coherence score"""
        
        # Start with perfect score
        base_score = 1.0
        
        # Calculate contradiction penalty
        contradiction_penalty = self._calculate_contradiction_penalty(contradictions)
        
        # Calculate completeness bonus
        completeness_bonus = self._calculate_completeness_bonus(completeness_score)
        
        # Calculate pattern consistency
        pattern_consistency = self._calculate_pattern_consistency(pattern_matches)
        
        # Calculate confidence adjustment
        confidence_level = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Apply weighted scoring
        final_score = (
            base_score - 
            (contradiction_penalty * self.scoring_weights['contradiction_penalty']) +
            (completeness_bonus * self.scoring_weights['completeness_bonus']) +
            (pattern_consistency * self.scoring_weights['pattern_consistency'])
        )
        
        # Confidence adjustment
        confidence_adjustment = (confidence_level - 0.5) * self.scoring_weights['confidence_adjustment']
        final_score += confidence_adjustment
        
        # Ensure score is in valid range
        final_score = max(0.0, min(1.0, final_score))
        
        return CoherenceScore(
            overall_score=final_score,
            contradiction_penalty=contradiction_penalty,
            completeness_bonus=completeness_bonus,
            pattern_consistency=pattern_consistency,
            confidence_level=confidence_level,
            breakdown={
                'base_score': base_score,
                'contradiction_impact': -contradiction_penalty * self.scoring_weights['contradiction_penalty'],
                'completeness_impact': completeness_bonus * self.scoring_weights['completeness_bonus'],
                'pattern_impact': pattern_consistency * self.scoring_weights['pattern_consistency'],
                'confidence_impact': confidence_adjustment
            }
        )
    
    def validate_coherence_threshold(self, coherence_score: CoherenceScore, 
                                   threshold: float = 0.7) -> ValidationResult:
        """Validate coherence meets threshold"""
        
        if coherence_score.overall_score >= threshold:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"Coherence score {coherence_score.overall_score:.2f} meets threshold {threshold}",
                score=coherence_score.overall_score
            )
        else:
            recommendations = self._generate_coherence_recommendations(coherence_score)
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Coherence score {coherence_score.overall_score:.2f} below threshold {threshold}",
                score=coherence_score.overall_score,
                recommendations=recommendations,
                details={'breakdown': coherence_score.breakdown}
            )
    
    def _calculate_contradiction_penalty(self, contradictions: List) -> float:
        """Calculate penalty for logical contradictions"""
        
        if not contradictions:
            return 0.0
        
        total_penalty = 0.0
        
        for contradiction in contradictions:
            confidence = getattr(contradiction, 'confidence', 0.5)
            
            if confidence >= 0.8:
                total_penalty += self.penalty_scales['high_confidence_contradiction']
            elif confidence >= 0.5:
                total_penalty += self.penalty_scales['medium_confidence_contradiction']
            else:
                total_penalty += self.penalty_scales['low_confidence_contradiction']
        
        # Normalize by number of contradictions (avoid over-penalizing)
        normalized_penalty = total_penalty / (1 + len(contradictions) * 0.5)
        
        return min(1.0, normalized_penalty)
    
    def _calculate_completeness_bonus(self, completeness_score: float) -> float:
        """Calculate bonus for context completeness"""
        
        if completeness_score >= 0.9:
            return self.bonus_scales['complete_context']
        elif completeness_score >= 0.7:
            return self.bonus_scales['complete_context'] * 0.7
        elif completeness_score >= 0.5:
            return self.bonus_scales['complete_context'] * 0.4
        else:
            return 0.0
    
    def _calculate_pattern_consistency(self, pattern_matches: List) -> float:
        """Calculate score for pattern consistency"""
        
        if not pattern_matches:
            return 0.5  # Neutral score when no patterns to evaluate
        
        # Calculate average confidence of pattern matches
        total_confidence = sum(getattr(match, 'match_confidence', 0.5) for match in pattern_matches)
        avg_confidence = total_confidence / len(pattern_matches)
        
        # Higher consistency = higher score
        if avg_confidence >= 0.8:
            return 1.0
        elif avg_confidence >= 0.6:
            return 0.7
        elif avg_confidence >= 0.4:
            return 0.5
        else:
            return 0.2
    
    def _generate_coherence_recommendations(self, coherence_score: CoherenceScore) -> List[str]:
        """Generate recommendations to improve coherence"""
        
        recommendations = []
        
        # Address highest impact issues first
        if coherence_score.contradiction_penalty > 0.3:
            recommendations.append("Resolve logical contradictions")
        
        if coherence_score.completeness_bonus < 0.1:
            recommendations.append("Provide more complete context")
        
        if coherence_score.pattern_consistency < 0.5:
            recommendations.append("Improve pattern consistency")
        
        if coherence_score.confidence_level < 0.6:
            recommendations.append("Increase validation confidence")
        
        # Specific breakdown-based recommendations
        breakdown = coherence_score.breakdown or {}
        if breakdown.get('contradiction_impact', 0) < -0.2:
            recommendations.append("Focus on contradiction resolution")
        
        if breakdown.get('completeness_impact', 0) < 0.1:
            recommendations.append("Add missing context elements")
        
        return recommendations
    
    def compare_coherence_scores(self, score_a: CoherenceScore, 
                                score_b: CoherenceScore) -> Dict[str, float]:
        """Compare two coherence scores"""
        
        return {
            'overall_difference': score_b.overall_score - score_a.overall_score,
            'contradiction_difference': score_a.contradiction_penalty - score_b.contradiction_penalty,
            'completeness_difference': score_b.completeness_bonus - score_a.completeness_bonus,
            'pattern_difference': score_b.pattern_consistency - score_a.pattern_consistency,
            'confidence_difference': score_b.confidence_level - score_a.confidence_level
        }
    
    def get_score_interpretation(self, score: float) -> str:
        """Get human-readable interpretation of score"""
        
        if score >= 0.9:
            return "Excellent coherence"
        elif score >= 0.8:
            return "Good coherence"
        elif score >= 0.7:
            return "Acceptable coherence"
        elif score >= 0.6:
            return "Marginal coherence"
        elif score >= 0.5:
            return "Poor coherence"
        else:
            return "Critical coherence issues"
    
    def analyze_score_trends(self, scores: List[CoherenceScore]) -> Dict[str, float]:
        """Analyze trends in coherence scores over time"""
        
        if len(scores) < 2:
            return {'trend': 0.0, 'stability': 1.0}
        
        # Calculate trend (improvement/decline)
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = sum(s.overall_score for s in first_half) / len(first_half)
        avg_second = sum(s.overall_score for s in second_half) / len(second_half)
        
        trend = avg_second - avg_first
        
        # Calculate stability (variance)
        all_scores = [s.overall_score for s in scores]
        mean_score = sum(all_scores) / len(all_scores)
        variance = sum((score - mean_score) ** 2 for score in all_scores) / len(all_scores)
        stability = 1.0 - min(1.0, variance)
        
        return {
            'trend': trend,
            'stability': stability,
            'mean_score': mean_score,
            'variance': variance
        }
