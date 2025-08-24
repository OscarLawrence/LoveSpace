"""Token usage analysis and optimization - 200 LOC max"""

import re
from typing import Dict, List, Optional, Tuple
from .models import TokenAnalysis, ValidationResult, ValidationStatus


class TokenAnalyzer:
    """Analyzes and optimizes token usage"""
    
    def __init__(self):
        self.token_costs = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-3.5': {'input': 0.001, 'output': 0.002},
            'claude': {'input': 0.008, 'output': 0.024}
        }
        
        self.optimization_patterns = {
            'redundant_whitespace': r'\s{2,}',
            'verbose_comments': r'#\s*[A-Za-z\s]{50,}',
            'repeated_imports': r'(import\s+\w+\n){2,}',
            'empty_lines': r'\n\s*\n\s*\n',
            'verbose_docstrings': r'""".{200,}"""'
        }
        
        # Approximate tokens per character for different content types
        self.token_ratios = {
            'code': 0.25,      # Code is more token-dense
            'text': 0.20,      # Natural text
            'comments': 0.18,  # Comments are less dense
            'whitespace': 0.05 # Mostly whitespace
        }
    
    def analyze_token_usage(self, content: str, content_type: str = 'mixed') -> TokenAnalysis:
        """Analyze token usage for given content"""
        
        total_tokens = self._estimate_tokens(content, content_type)
        optimizations = self._identify_optimizations(content)
        optimized_content = self._apply_optimizations(content, optimizations)
        optimized_tokens = self._estimate_tokens(optimized_content, content_type)
        
        efficiency_score = optimized_tokens / total_tokens if total_tokens > 0 else 1.0
        
        return TokenAnalysis(
            total_tokens=total_tokens,
            estimated_tokens=optimized_tokens,
            efficiency_score=efficiency_score,
            optimization_suggestions=optimizations,
            cost_estimate=self._calculate_cost(total_tokens)
        )
    
    def validate_token_limits(self, content: str, max_tokens: int = 100000) -> ValidationResult:
        """Validate content doesn't exceed token limits"""
        
        analysis = self.analyze_token_usage(content)
        
        if analysis.total_tokens <= max_tokens:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"Token usage within limits ({analysis.total_tokens}/{max_tokens})",
                score=1.0 - (analysis.total_tokens / max_tokens)
            )
        else:
            excess = analysis.total_tokens - max_tokens
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Token limit exceeded by {excess} tokens",
                score=0.0,
                recommendations=analysis.optimization_suggestions[:3]
            )
    
    def optimize_for_tokens(self, content: str) -> Tuple[str, TokenAnalysis]:
        """Optimize content for minimal token usage"""
        
        optimizations = self._identify_optimizations(content)
        optimized_content = self._apply_optimizations(content, optimizations)
        analysis = self.analyze_token_usage(optimized_content)
        
        return optimized_content, analysis
    
    def _estimate_tokens(self, content: str, content_type: str = 'mixed') -> int:
        """Estimate token count for content"""
        
        if content_type == 'mixed':
            # Analyze content composition
            code_chars = len(re.findall(r'[{}()\[\];]', content))
            comment_chars = len(re.findall(r'#.*', content))
            whitespace_chars = len(re.findall(r'\s', content))
            text_chars = len(content) - code_chars - comment_chars - whitespace_chars
            
            estimated_tokens = (
                code_chars * self.token_ratios['code'] +
                comment_chars * self.token_ratios['comments'] +
                whitespace_chars * self.token_ratios['whitespace'] +
                text_chars * self.token_ratios['text']
            )
        else:
            ratio = self.token_ratios.get(content_type, 0.20)
            estimated_tokens = len(content) * ratio
        
        return int(estimated_tokens)
    
    def _identify_optimizations(self, content: str) -> List[str]:
        """Identify potential optimizations"""
        
        suggestions = []
        
        # Check for redundant whitespace
        if re.search(self.optimization_patterns['redundant_whitespace'], content):
            suggestions.append("Remove redundant whitespace")
        
        # Check for verbose comments
        if re.search(self.optimization_patterns['verbose_comments'], content):
            suggestions.append("Shorten verbose comments")
        
        # Check for repeated imports
        if re.search(self.optimization_patterns['repeated_imports'], content):
            suggestions.append("Consolidate repeated imports")
        
        # Check for excessive empty lines
        if re.search(self.optimization_patterns['empty_lines'], content):
            suggestions.append("Reduce excessive empty lines")
        
        # Check for verbose docstrings
        if re.search(self.optimization_patterns['verbose_docstrings'], content):
            suggestions.append("Shorten verbose docstrings")
        
        # Check line length
        long_lines = [line for line in content.split('\n') if len(line) > 120]
        if long_lines:
            suggestions.append(f"Break {len(long_lines)} long lines")
        
        # Check for repetitive patterns
        if self._has_repetitive_patterns(content):
            suggestions.append("Reduce repetitive code patterns")
        
        return suggestions
    
    def _apply_optimizations(self, content: str, optimizations: List[str]) -> str:
        """Apply basic optimizations to content"""
        
        optimized = content
        
        if "Remove redundant whitespace" in optimizations:
            optimized = re.sub(self.optimization_patterns['redundant_whitespace'], ' ', optimized)
        
        if "Reduce excessive empty lines" in optimizations:
            optimized = re.sub(self.optimization_patterns['empty_lines'], '\n\n', optimized)
        
        if "Consolidate repeated imports" in optimizations:
            # Simple deduplication of import lines
            lines = optimized.split('\n')
            import_lines = []
            other_lines = []
            
            for line in lines:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    if line not in import_lines:
                        import_lines.append(line)
                else:
                    other_lines.append(line)
            
            optimized = '\n'.join(import_lines + [''] + other_lines)
        
        return optimized
    
    def _has_repetitive_patterns(self, content: str) -> bool:
        """Check for repetitive code patterns"""
        
        lines = content.split('\n')
        line_counts = {}
        
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10:  # Only check substantial lines
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        # If any line appears more than 3 times, consider it repetitive
        return any(count > 3 for count in line_counts.values())
    
    def _calculate_cost(self, tokens: int, model: str = 'gpt-4') -> float:
        """Calculate estimated cost for token usage"""
        
        if model not in self.token_costs:
            return 0.0
        
        # Assume roughly equal input/output split
        input_tokens = tokens * 0.7
        output_tokens = tokens * 0.3
        
        costs = self.token_costs[model]
        total_cost = (
            (input_tokens / 1000) * costs['input'] +
            (output_tokens / 1000) * costs['output']
        )
        
        return round(total_cost, 4)
    
    def get_efficiency_recommendations(self, analysis: TokenAnalysis) -> List[str]:
        """Get specific recommendations for improving efficiency"""
        
        recommendations = []
        
        if analysis.efficiency_score < 0.7:
            recommendations.append("Consider significant content restructuring")
        elif analysis.efficiency_score < 0.8:
            recommendations.append("Apply suggested optimizations")
        elif analysis.efficiency_score < 0.9:
            recommendations.append("Minor optimizations available")
        
        if analysis.total_tokens > 50000:
            recommendations.append("Consider splitting into smaller modules")
        
        if analysis.cost_estimate > 1.0:
            recommendations.append("High cost - prioritize optimization")
        
        return recommendations
    
    def batch_analyze(self, contents: Dict[str, str]) -> Dict[str, TokenAnalysis]:
        """Analyze multiple content pieces"""
        
        results = {}
        for name, content in contents.items():
            results[name] = self.analyze_token_usage(content)
        
        return results
