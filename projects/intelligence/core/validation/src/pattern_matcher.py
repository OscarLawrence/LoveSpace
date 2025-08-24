"""Pattern recognition for validation - 200 LOC max"""

import re
from typing import Dict, List, Set, Optional, Tuple
from .models import PatternMatch, ValidationResult, ValidationStatus


class PatternMatcher:
    """Recognizes patterns for validation"""
    
    def __init__(self):
        self.validation_patterns = {
            'file_size_violation': {
                'pattern': r'(\d+)\s*lines',
                'threshold': 200,
                'type': 'numeric'
            },
            'logical_operators': {
                'pattern': r'\b(and|or|not|if|then|else)\b',
                'type': 'logical'
            },
            'contradiction_indicators': {
                'pattern': r'\b(always|never|all|none|must|cannot)\b',
                'type': 'absolute'
            },
            'uncertainty_markers': {
                'pattern': r'\b(maybe|perhaps|might|could|possibly)\b',
                'type': 'uncertainty'
            },
            'requirement_patterns': {
                'pattern': r'\b(required|mandatory|essential|critical)\b',
                'type': 'requirement'
            }
        }
        
        self.code_patterns = {
            'import_statements': r'^(import|from)\s+\w+',
            'function_definitions': r'^def\s+\w+\(',
            'class_definitions': r'^class\s+\w+',
            'comments': r'#.*$',
            'docstrings': r'""".*?"""'
        }
        
        self.anti_patterns = {
            'long_lines': r'.{120,}',
            'deep_nesting': r'^\s{20,}',
            'magic_numbers': r'\b\d{3,}\b',
            'repetitive_code': r'(.{20,})\n.*\1'
        }
    
    def find_patterns(self, text: str, pattern_types: Optional[List[str]] = None) -> List[PatternMatch]:
        """Find all patterns in text"""
        
        matches = []
        patterns_to_check = pattern_types or list(self.validation_patterns.keys())
        
        for pattern_id in patterns_to_check:
            if pattern_id in self.validation_patterns:
                pattern_info = self.validation_patterns[pattern_id]
                pattern_matches = self._find_pattern_matches(text, pattern_id, pattern_info)
                matches.extend(pattern_matches)
        
        return matches
    
    def validate_pattern_compliance(self, text: str, required_patterns: List[str],
                                  forbidden_patterns: List[str]) -> ValidationResult:
        """Validate text complies with pattern requirements"""
        
        issues = []
        
        # Check required patterns are present
        for required in required_patterns:
            if required in self.validation_patterns:
                pattern_info = self.validation_patterns[required]
                matches = self._find_pattern_matches(text, required, pattern_info)
                if not matches:
                    issues.append(f"Missing required pattern: {required}")
        
        # Check forbidden patterns are absent
        for forbidden in forbidden_patterns:
            if forbidden in self.validation_patterns:
                pattern_info = self.validation_patterns[forbidden]
                matches = self._find_pattern_matches(text, forbidden, pattern_info)
                if matches:
                    issues.append(f"Forbidden pattern found: {forbidden} ({len(matches)} occurrences)")
        
        if issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Pattern compliance issues: {len(issues)}",
                score=0.0,
                details={'issues': issues}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="All pattern compliance checks passed",
            score=1.0
        )
    
    def analyze_code_structure(self, code: str) -> Dict[str, int]:
        """Analyze code structure using patterns"""
        
        structure_counts = {}
        
        for pattern_name, pattern in self.code_patterns.items():
            matches = re.findall(pattern, code, re.MULTILINE)
            structure_counts[pattern_name] = len(matches)
        
        return structure_counts
    
    def detect_anti_patterns(self, code: str) -> List[PatternMatch]:
        """Detect anti-patterns in code"""
        
        anti_pattern_matches = []
        
        for pattern_name, pattern in self.anti_patterns.items():
            matches = re.finditer(pattern, code, re.MULTILINE)
            
            for match in matches:
                anti_pattern_matches.append(PatternMatch(
                    pattern_id=pattern_name,
                    match_confidence=0.8,
                    matched_text=match.group(),
                    context_span=self._get_context_span(code, match.start(), match.end()),
                    metadata={'line_number': code[:match.start()].count('\n') + 1}
                ))
        
        return anti_pattern_matches
    
    def _find_pattern_matches(self, text: str, pattern_id: str, 
                             pattern_info: Dict) -> List[PatternMatch]:
        """Find matches for specific pattern"""
        
        matches = []
        pattern = pattern_info['pattern']
        pattern_type = pattern_info['type']
        
        regex_matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in regex_matches:
            confidence = self._calculate_match_confidence(match, pattern_type, pattern_info)
            context_span = self._get_context_span(text, match.start(), match.end())
            
            matches.append(PatternMatch(
                pattern_id=pattern_id,
                match_confidence=confidence,
                matched_text=match.group(),
                context_span=context_span,
                metadata={
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'line_number': text[:match.start()].count('\n') + 1
                }
            ))
        
        return matches
    
    def _calculate_match_confidence(self, match, pattern_type: str, 
                                   pattern_info: Dict) -> float:
        """Calculate confidence score for pattern match"""
        
        base_confidence = 0.7
        
        if pattern_type == 'numeric':
            # For numeric patterns, check against threshold
            matched_num = re.search(r'\d+', match.group())
            if matched_num:
                num_value = int(matched_num.group())
                threshold = pattern_info.get('threshold', 0)
                if num_value > threshold:
                    base_confidence = 0.9
        
        elif pattern_type == 'logical':
            # Logical patterns are high confidence
            base_confidence = 0.85
        
        elif pattern_type == 'absolute':
            # Absolute statements are medium-high confidence
            base_confidence = 0.8
        
        elif pattern_type == 'uncertainty':
            # Uncertainty markers are medium confidence
            base_confidence = 0.6
        
        elif pattern_type == 'requirement':
            # Requirements are high confidence
            base_confidence = 0.9
        
        return base_confidence
    
    def _get_context_span(self, text: str, start: int, end: int, 
                         context_chars: int = 50) -> str:
        """Get context around matched pattern"""
        
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)
        
        context = text[context_start:context_end]
        
        # Clean up context for readability
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context
    
    def suggest_pattern_improvements(self, matches: List[PatternMatch]) -> List[str]:
        """Suggest improvements based on pattern matches"""
        
        suggestions = []
        
        # Group matches by pattern type
        pattern_groups = {}
        for match in matches:
            pattern_id = match.pattern_id
            if pattern_id not in pattern_groups:
                pattern_groups[pattern_id] = []
            pattern_groups[pattern_id].append(match)
        
        # Generate suggestions based on patterns found
        for pattern_id, pattern_matches in pattern_groups.items():
            count = len(pattern_matches)
            
            if pattern_id == 'file_size_violation' and count > 0:
                suggestions.append(f"Split file into smaller modules ({count} size violations)")
            
            elif pattern_id == 'contradiction_indicators' and count > 3:
                suggestions.append("Review absolute statements for potential contradictions")
            
            elif pattern_id == 'uncertainty_markers' and count > 5:
                suggestions.append("Clarify uncertain statements")
            
            elif pattern_id == 'long_lines' and count > 0:
                suggestions.append(f"Break {count} long lines for readability")
            
            elif pattern_id == 'deep_nesting' and count > 0:
                suggestions.append(f"Reduce deep nesting in {count} locations")
        
        return suggestions
    
    def calculate_pattern_score(self, matches: List[PatternMatch]) -> float:
        """Calculate overall pattern quality score"""
        
        if not matches:
            return 1.0
        
        # Weight different pattern types
        pattern_weights = {
            'file_size_violation': -0.3,
            'long_lines': -0.1,
            'deep_nesting': -0.2,
            'magic_numbers': -0.1,
            'repetitive_code': -0.2,
            'logical_operators': 0.1,
            'requirement_patterns': 0.05
        }
        
        total_score = 1.0
        
        for match in matches:
            weight = pattern_weights.get(match.pattern_id, 0)
            confidence_adjusted_weight = weight * match.match_confidence
            total_score += confidence_adjusted_weight
        
        return max(0.0, min(1.0, total_score))
