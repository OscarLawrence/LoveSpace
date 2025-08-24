"""Token efficiency optimization for request clarity and cost reduction"""

import re
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    original_request: str
    optimized_request: str
    estimated_token_savings: int
    clarity_improvements: List[str]
    batch_suggestions: List[str]


class TokenEfficiencyOptimizer:
    """Optimizes requests for token efficiency and clarity"""
    
    def __init__(self):
        self.redundancy_patterns = [
            (r'\b(please|could you|would you|can you)\b', ''),
            (r'\b(also|additionally|furthermore|moreover)\b', ''),
            (r'\b(the file called|the file named|file named)\b', ''),
            (r'\b(make sure to|be sure to|ensure that)\b', ''),
        ]
        
        self.clarity_patterns = {
            'ambiguous_pronouns': r'\b(it|this|that|they|them)\b',
            'vague_quantifiers': r'\b(some|many|several|a few|lots of)\b',
            'unclear_references': r'\b(the above|mentioned earlier|as discussed)\b'
        }
        
        self.batch_keywords = [
            'create', 'delete', 'update', 'install', 'configure', 'test', 'run'
        ]
    
    def optimize_request_clarity(self, request: str) -> OptimizationResult:
        """Reduce ambiguity and redundancy in requests"""
        
        original = request
        optimized = request
        improvements = []
        
        # Remove redundant phrases
        for pattern, replacement in self.redundancy_patterns:
            before = optimized
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
            if before != optimized:
                improvements.append(f"Removed redundant phrase: {pattern}")
        
        # Clean up extra whitespace
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        
        # Detect ambiguity issues
        ambiguity_issues = self._detect_ambiguity(optimized)
        improvements.extend(ambiguity_issues)
        
        # Suggest more specific phrasing
        specificity_suggestions = self._suggest_specificity(optimized)
        improvements.extend(specificity_suggestions)
        
        # Estimate token savings
        token_savings = self._estimate_token_difference(original, optimized)
        
        # Generate batch suggestions
        batch_suggestions = self.suggest_batch_operations(optimized)
        
        return OptimizationResult(
            original_request=original,
            optimized_request=optimized,
            estimated_token_savings=token_savings,
            clarity_improvements=improvements,
            batch_suggestions=batch_suggestions
        )
    
    def estimate_token_cost(self, request: str) -> Dict[str, Any]:
        """Estimate token cost for request processing"""
        
        # Simple token estimation (4 chars per token average)
        estimated_tokens = len(request) // 4
        
        # Factor in complexity
        complexity_multiplier = 1.0
        
        if len(re.findall(r'\b(?:create|delete|modify|update)\b', request, re.IGNORECASE)) > 3:
            complexity_multiplier += 0.5
            
        if len(re.findall(r'\b(?:file|directory|folder)\b', request, re.IGNORECASE)) > 5:
            complexity_multiplier += 0.3
            
        if len(request.split()) > 100:
            complexity_multiplier += 0.2
        
        final_estimate = int(estimated_tokens * complexity_multiplier)
        
        return {
            'base_tokens': estimated_tokens,
            'complexity_factor': complexity_multiplier,
            'estimated_total': final_estimate,
            'cost_category': self._categorize_cost(final_estimate)
        }
    
    def suggest_batch_operations(self, request: str) -> List[str]:
        """Group related operations for efficiency"""
        
        suggestions = []
        
        # Find file operations
        file_ops = re.findall(r'(create|delete|update|modify)\s+(?:file\s+)?([^\s,]+)', 
                             request, re.IGNORECASE)
        
        if len(file_ops) > 2:
            suggestions.append(f"Batch {len(file_ops)} file operations together")
        
        # Find package operations
        package_ops = re.findall(r'(install|add|remove)\s+(?:package\s+)?([^\s,]+)', 
                                request, re.IGNORECASE)
        
        if len(package_ops) > 1:
            packages = [op[1] for op in package_ops]
            suggestions.append(f"Batch install packages: {', '.join(packages[:3])}")
        
        # Find test operations
        if request.count('test') > 2:
            suggestions.append("Consider running all tests in a single command")
        
        # Find configuration operations
        config_ops = re.findall(r'configure?\s+([^\s,]+)', request, re.IGNORECASE)
        if len(config_ops) > 1:
            suggestions.append(f"Batch configure: {', '.join(config_ops[:3])}")
        
        return suggestions
    
    def _detect_ambiguity(self, request: str) -> List[str]:
        """Detect ambiguous language in request"""
        
        issues = []
        
        for issue_type, pattern in self.clarity_patterns.items():
            matches = re.findall(pattern, request, re.IGNORECASE)
            if matches:
                issues.append(f"Ambiguous {issue_type}: {', '.join(list(set(matches))[:3])}")
        
        return issues
    
    def _suggest_specificity(self, request: str) -> List[str]:
        """Suggest more specific phrasing"""
        
        suggestions = []
        
        # Suggest specific file paths
        if re.search(r'\bfiles?\b', request, re.IGNORECASE) and not re.search(r'/\w+', request):
            suggestions.append("Consider specifying full file paths")
        
        # Suggest specific versions
        if re.search(r'\blatest\b', request, re.IGNORECASE):
            suggestions.append("Consider specifying exact version numbers instead of 'latest'")
        
        # Suggest specific quantities
        if re.search(r'\ball\b', request, re.IGNORECASE):
            suggestions.append("Consider specifying exact count instead of 'all'")
        
        return suggestions
    
    def _estimate_token_difference(self, original: str, optimized: str) -> int:
        """Estimate token savings from optimization"""
        
        original_tokens = len(original) // 4
        optimized_tokens = len(optimized) // 4
        
        return max(0, original_tokens - optimized_tokens)
    
    def _categorize_cost(self, estimated_tokens: int) -> str:
        """Categorize request cost level"""
        
        if estimated_tokens < 50:
            return "low"
        elif estimated_tokens < 200:
            return "medium"
        elif estimated_tokens < 500:
            return "high"
        else:
            return "very_high"
    
    def generate_optimization_report(self, results: List[OptimizationResult]) -> Dict:
        """Generate summary report of optimization results"""
        
        total_savings = sum(r.estimated_token_savings for r in results)
        total_improvements = sum(len(r.clarity_improvements) for r in results)
        
        return {
            'total_requests_optimized': len(results),
            'total_token_savings': total_savings,
            'total_clarity_improvements': total_improvements,
            'average_savings_per_request': total_savings / len(results) if results else 0,
            'top_optimization_types': self._get_top_improvement_types(results)
        }
    
    def _get_top_improvement_types(self, results: List[OptimizationResult]) -> Dict[str, int]:
        """Get most common improvement types"""
        
        improvement_counts = {}
        
        for result in results:
            for improvement in result.clarity_improvements:
                improvement_type = improvement.split(':')[0]
                improvement_counts[improvement_type] = improvement_counts.get(improvement_type, 0) + 1
        
        return dict(sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def analyze_request_patterns(self, requests: List[str]) -> Dict[str, Any]:
        """Analyze patterns across multiple requests for batch optimization"""
        
        patterns = {
            'repeated_operations': {},
            'common_file_types': {},
            'frequent_commands': {},
            'batch_opportunities': []
        }
        
        # Track repeated operations
        operations = []
        for request in requests:
            words = request.lower().split()
            for keyword in self.batch_keywords:
                if keyword in words:
                    operations.append(keyword)
        
        for op in operations:
            patterns['repeated_operations'][op] = patterns['repeated_operations'].get(op, 0) + 1
        
        # Identify file type patterns
        file_extensions = re.findall(r'\.(\w+)', ' '.join(requests))
        for ext in file_extensions:
            patterns['common_file_types'][ext] = patterns['common_file_types'].get(ext, 0) + 1
        
        # Find batch opportunities
        if patterns['repeated_operations']:
            most_common = max(patterns['repeated_operations'].items(), key=lambda x: x[1])
            if most_common[1] > 2:
                patterns['batch_opportunities'].append(
                    f"Consider batching {most_common[1]} {most_common[0]} operations"
                )
        
        return patterns
    
    def optimize_for_context_efficiency(self, request: str, available_context: Dict) -> str:
        """Optimize request based on available context to reduce redundancy"""
        
        optimized = request
        
        # Remove redundant file path specifications if context has workspace info
        if 'workspace_root' in available_context:
            workspace_root = available_context['workspace_root']
            optimized = optimized.replace(workspace_root + '/', '')
        
        # Remove redundant environment specifications if context has env info
        if 'python_env' in available_context:
            env_name = available_context['python_env']
            optimized = re.sub(rf'\b{env_name}\s+environment\b', '', optimized, flags=re.IGNORECASE)
        
        # Remove redundant project specifications
        if 'project_name' in available_context:
            project_name = available_context['project_name']
            optimized = re.sub(rf'\b{project_name}\s+project\b', '', optimized, flags=re.IGNORECASE)
        
        return optimized.strip()
    
    def suggest_request_batching(self, requests: List[str]) -> List[Dict]:
        """Suggest how to batch multiple requests for efficiency"""
        
        batch_suggestions = []
        
        # Group by operation type
        operation_groups = {}
        for i, request in enumerate(requests):
            for keyword in self.batch_keywords:
                if keyword in request.lower():
                    if keyword not in operation_groups:
                        operation_groups[keyword] = []
                    operation_groups[keyword].append((i, request))
        
        # Generate batch suggestions
        for operation, request_list in operation_groups.items():
            if len(request_list) > 1:
                batch_suggestions.append({
                    'operation': operation,
                    'request_indices': [idx for idx, _ in request_list],
                    'suggestion': f"Batch {len(request_list)} {operation} operations into single request",
                    'estimated_savings': len(request_list) * 20  # Rough estimate
                })
        
        return batch_suggestions
    
    def calculate_complexity_score(self, request: str) -> float:
        """Calculate complexity score for request prioritization"""
        
        complexity_factors = {
            'file_operations': len(re.findall(r'\b(create|delete|move|copy)\b', request, re.IGNORECASE)),
            'code_analysis': len(re.findall(r'\b(parse|analyze|inspect|validate)\b', request, re.IGNORECASE)),
            'installations': len(re.findall(r'\b(install|add|remove)\b', request, re.IGNORECASE)),
            'configurations': len(re.findall(r'\b(configure|setup|initialize)\b', request, re.IGNORECASE)),
            'dependencies': len(re.findall(r'\b(import|require|dependency)\b', request, re.IGNORECASE))
        }
        
        # Weight different factors
        weights = {
            'file_operations': 1.0,
            'code_analysis': 2.0,
            'installations': 1.5,
            'configurations': 1.8,
            'dependencies': 1.2
        }
        
        complexity_score = sum(
            complexity_factors[factor] * weights[factor] 
            for factor in complexity_factors
        )
        
        # Normalize to 0-1 scale
        max_possible_score = sum(weights.values()) * 10  # Assume max 10 of each factor
        normalized_score = min(complexity_score / max_possible_score, 1.0)
        
        return normalized_score
    
    def generate_efficiency_metrics(self, original_request: str, optimized_request: str) -> Dict:
        """Generate detailed efficiency metrics for optimization"""
        
        original_length = len(original_request)
        optimized_length = len(optimized_request)
        
        # Calculate various metrics
        character_reduction = original_length - optimized_length
        reduction_percentage = (character_reduction / original_length * 100) if original_length > 0 else 0
        
        # Estimate token counts (rough approximation)
        original_tokens = len(original_request.split())
        optimized_tokens = len(optimized_request.split())
        token_savings = original_tokens - optimized_tokens
        
        # Calculate clarity metrics
        clarity_score = self._calculate_clarity_score(optimized_request)
        
        return {
            'character_reduction': character_reduction,
            'reduction_percentage': round(reduction_percentage, 2),
            'token_savings': token_savings,
            'clarity_score': clarity_score,
            'original_complexity': self.calculate_complexity_score(original_request),
            'optimized_complexity': self.calculate_complexity_score(optimized_request),
            'efficiency_rating': self._get_efficiency_rating(reduction_percentage, clarity_score)
        }
    
    def _calculate_clarity_score(self, text: str) -> float:
        """Calculate clarity score based on various factors"""
        
        # Factors that improve clarity
        has_specific_paths = bool(re.search(r'/[\w/]+\.\w+', text))
        has_concrete_numbers = bool(re.search(r'\b\d+\b', text))
        has_specific_commands = bool(re.search(r'\b(uv|pip|npm|git)\s+\w+', text))
        
        # Factors that reduce clarity
        has_ambiguous_pronouns = bool(re.search(self.clarity_patterns['ambiguous_pronouns'], text))
        has_vague_quantifiers = bool(re.search(self.clarity_patterns['vague_quantifiers'], text))
        
        clarity_score = 0.5  # Base score
        
        if has_specific_paths:
            clarity_score += 0.15
        if has_concrete_numbers:
            clarity_score += 0.15
        if has_specific_commands:
            clarity_score += 0.15
        if has_ambiguous_pronouns:
            clarity_score -= 0.1
        if has_vague_quantifiers:
            clarity_score -= 0.1
        
        return max(0.0, min(1.0, clarity_score))
    
    def _get_efficiency_rating(self, reduction_percentage: float, clarity_score: float) -> str:
        """Get overall efficiency rating"""
        
        efficiency_score = (reduction_percentage / 100 * 0.6) + (clarity_score * 0.4)
        
        if efficiency_score >= 0.8:
            return "excellent"
        elif efficiency_score >= 0.6:
            return "good"
        elif efficiency_score >= 0.4:
            return "fair"
        else:
            return "poor"
