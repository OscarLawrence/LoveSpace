"""Dense description generator for functions and code patterns."""

import ast
import re
from typing import Dict, List, Set, Optional
from .db_manager import Function, Pattern


class DenseDescriptionGenerator:
    """Generate dense, semantic descriptions for better embeddings."""
    
    def __init__(self):
        # Action verbs commonly found in function names
        self.action_verbs = {
            'parse', 'extract', 'find', 'search', 'get', 'fetch', 'load', 'read',
            'create', 'make', 'build', 'generate', 'write', 'save', 'store',
            'update', 'modify', 'edit', 'change', 'set', 'add', 'remove', 'delete',
            'check', 'validate', 'verify', 'test', 'assert', 'ensure',
            'handle', 'process', 'transform', 'convert', 'format', 'encode', 'decode',
            'send', 'receive', 'connect', 'disconnect', 'open', 'close',
            'start', 'stop', 'run', 'execute', 'call', 'invoke'
        }
        
        # Domain keywords
        self.domains = {
            'cli': ['command', 'click', 'arg', 'option', 'cli', 'terminal'],
            'ast': ['ast', 'parse', 'node', 'tree', 'syntax'],
            'db': ['database', 'query', 'sql', 'table', 'record', 'conn'],
            'file': ['file', 'path', 'dir', 'folder', 'io', 'read', 'write'],
            'web': ['http', 'api', 'request', 'response', 'url', 'endpoint'],
            'auth': ['auth', 'login', 'token', 'jwt', 'session', 'user'],
            'config': ['config', 'setting', 'env', 'param', 'option'],
            'test': ['test', 'mock', 'assert', 'verify', 'check'],
            'docs': ['doc', 'documentation', 'help', 'guide', 'manual'],
            'search': ['search', 'find', 'query', 'match', 'filter'],
            'embed': ['embed', 'vector', 'similarity', 'semantic'],
            'workspace': ['workspace', 'project', 'repo', 'monorepo']
        }
        
        # Pattern keywords
        self.patterns = {
            'error_handling': ['try', 'except', 'catch', 'error', 'exception'],
            'async': ['async', 'await', 'asyncio', 'concurrent'],
            'validation': ['validate', 'check', 'verify', 'assert', 'ensure'],
            'caching': ['cache', 'memoize', 'store', 'temp'],
            'logging': ['log', 'debug', 'info', 'warn', 'error'],
            'iteration': ['for', 'while', 'loop', 'iterate', 'each'],
            'conditional': ['if', 'else', 'elif', 'condition', 'branch'],
            'recursion': ['recursive', 'recurse', 'self'],
            'factory': ['create', 'make', 'build', 'factory'],
            'singleton': ['singleton', 'instance', 'global'],
            'decorator': ['decorator', 'wrap', '@'],
            'context_manager': ['with', 'context', 'manager', '__enter__', '__exit__']
        }
    
    def generate_dense_function_description(self, func: Function, format_type: str = "hierarchical") -> str:
        """Generate dense description for a function with improved structure."""
        if format_type == "natural":
            return self._generate_natural_description(func)
        elif format_type == "hierarchical":
            return self._generate_hierarchical_description(func)
        else:  # legacy format
            return self._generate_legacy_description(func)
    
    def _generate_hierarchical_description(self, func: Function) -> str:
        """Generate hierarchical dense description with semantic grouping."""
        groups = []
        
        # Primary action and domain
        action = self._extract_action(func.name)
        domain = self._infer_domain(func)
        if action and domain:
            groups.append(f"action:{action}|domain:{domain}")
        elif action:
            groups.append(f"action:{action}")
        elif domain:
            groups.append(f"domain:{domain}")
        
        # I/O specification
        io_desc = self._extract_io_description(func)
        if io_desc:
            groups.append(f"io:{io_desc}")
        
        # Programming patterns
        patterns = self._extract_patterns(func)
        if patterns:
            # Sort patterns by importance
            primary_patterns = [p for p in patterns if p in ['async', 'error_handling', 'validation']]
            secondary_patterns = [p for p in patterns if p not in primary_patterns]
            
            if primary_patterns:
                groups.append(f"patterns:{','.join(primary_patterns)}")
            if secondary_patterns:
                groups.append(f"meta:{','.join(secondary_patterns)}")
        
        # Function identifier
        groups.append(f"name:{func.name}")
        
        return "|".join(groups)
    
    def _generate_natural_description(self, func: Function) -> str:
        """Generate natural language description."""
        parts = []
        
        action = self._extract_action(func.name)
        domain = self._infer_domain(func)
        patterns = self._extract_patterns(func)
        
        if action and domain:
            parts.append(f"Function to {action} {domain} data")
        elif action:
            parts.append(f"Function to {action}")
        
        if patterns:
            important_patterns = [p for p in patterns if p in ['async', 'error_handling', 'validation']]
            if important_patterns:
                parts.append(f"with {', '.join(important_patterns.replace('_', ' '))}")
        
        if func.params:
            param_count = len(func.params) if isinstance(func.params, list) else 0
            if param_count > 0:
                parts.append(f"taking {param_count} parameters")
        
        return ". ".join(parts) if parts else f"Function {func.name}"
    
    def _generate_legacy_description(self, func: Function) -> str:
        """Generate legacy colon-separated description."""
        components = []
        
        action = self._extract_action(func.name)
        if action:
            components.append(action)
        
        domain = self._infer_domain(func)
        if domain:
            components.append(domain)
        
        patterns = self._extract_patterns(func)
        if patterns:
            components.extend(patterns)
        
        io_desc = self._extract_io_description(func)
        if io_desc:
            components.append(io_desc)
        
        components.append(f"name:{func.name}")
        
        return ":".join(components)
    
    def generate_dense_pattern_description(self, pattern: Pattern) -> str:
        """Generate dense description for a code pattern."""
        components = []
        
        # Pattern type
        components.append(f"pattern:{pattern.pattern_type}")
        
        # Extract semantic info from code snippet
        if pattern.code_snippet:
            semantic_info = self._analyze_code_snippet(pattern.code_snippet)
            components.extend(semantic_info)
        
        # Usage context
        if pattern.usage_context:
            context_tokens = self._extract_context_tokens(pattern.usage_context)
            if context_tokens:
                components.append(f"context:{','.join(context_tokens)}")
        
        # Success metric
        if pattern.success_count > 0:
            components.append(f"success:{pattern.success_count}")
        
        return ":".join(components)
    
    def _extract_action(self, func_name: str) -> Optional[str]:
        """Extract action verb from function name."""
        # Convert camelCase/snake_case to words
        words = re.findall(r'[a-z]+|[A-Z][a-z]*', func_name.replace('_', ' '))
        words = [w.lower() for w in words]
        
        # Find first action verb
        for word in words:
            if word in self.action_verbs:
                return word
        
        # Check for common prefixes
        if func_name.startswith('is_') or func_name.startswith('has_'):
            return 'check'
        if func_name.startswith('get_') or func_name.startswith('fetch_'):
            return 'get'
        if func_name.startswith('set_') or func_name.startswith('update_'):
            return 'set'
        
        return None
    
    def _infer_domain(self, func: Function) -> Optional[str]:
        """Infer domain from function name, params, and context."""
        text_to_analyze = f"{func.name} {func.file_path}"
        
        # Add parameter names
        if func.params:
            param_names = []
            for p in func.params:
                if isinstance(p, dict):
                    param_names.append(p.get('name', ''))
                else:
                    param_names.append(str(p))
            text_to_analyze += " " + " ".join(param_names)
        
        # Add docstring
        if func.docstring:
            text_to_analyze += " " + func.docstring
        
        text_lower = text_to_analyze.lower()
        
        # Score each domain
        domain_scores = {}
        for domain, keywords in self.domains.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        # Return highest scoring domain
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _extract_patterns(self, func: Function) -> List[str]:
        """Extract programming patterns from function."""
        patterns_found = []
        
        # Analyze function name and docstring
        text_to_analyze = f"{func.name} {func.docstring or ''}"
        
        # Add file path context
        if func.file_path:
            text_to_analyze += " " + func.file_path
        
        text_lower = text_to_analyze.lower()
        
        # Check for pattern keywords
        for pattern, keywords in self.patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                patterns_found.append(pattern)
        
        # Infer patterns from function characteristics
        if func.params:
            # Check for common parameter patterns
            param_text = str(func.params).lower()
            if 'self' in param_text:
                patterns_found.append('method')
            if 'cls' in param_text:
                patterns_found.append('classmethod')
            if '*args' in param_text or '**kwargs' in param_text:
                patterns_found.append('variadic')
        
        # Check for async pattern
        if 'async' in func.name.lower():
            patterns_found.append('async')
        
        return list(set(patterns_found))  # Remove duplicates
    
    def _extract_io_description(self, func: Function) -> Optional[str]:
        """Extract input/output type information."""
        components = []
        
        # Input types from parameters
        if func.params:
            input_types = []
            for p in func.params:
                if isinstance(p, dict):
                    param_type = p.get('type', '')
                    if param_type:
                        input_types.append(param_type)
                    else:
                        # Infer from name
                        param_name = p.get('name', '').lower()
                        if 'file' in param_name or 'path' in param_name:
                            input_types.append('path')
                        elif 'str' in param_name or 'text' in param_name:
                            input_types.append('str')
                        elif 'id' in param_name or 'num' in param_name:
                            input_types.append('int')
            
            if input_types:
                components.append(f"in:{','.join(set(input_types))}")
        
        # Output type from return type
        if func.return_type:
            components.append(f"out:{func.return_type}")
        else:
            # Infer from function name
            if 'get_' in func.name or 'find_' in func.name:
                components.append("out:data")
            elif 'is_' in func.name or 'has_' in func.name:
                components.append("out:bool")
            elif 'create_' in func.name or 'make_' in func.name:
                components.append("out:object")
        
        return "→".join(components) if components else None
    
    def _analyze_code_snippet(self, code: str) -> List[str]:
        """Analyze code snippet for semantic patterns."""
        patterns = []
        code_lower = code.lower()
        
        # Check for common code patterns
        if 'try:' in code or 'except' in code:
            patterns.append('error_handling')
        if 'async def' in code or 'await' in code:
            patterns.append('async')
        if 'for ' in code or 'while ' in code:
            patterns.append('iteration')
        if 'if ' in code:
            patterns.append('conditional')
        if 'class ' in code:
            patterns.append('class_def')
        if 'def ' in code:
            patterns.append('function_def')
        if 'import ' in code:
            patterns.append('imports')
        if '@' in code:
            patterns.append('decorator')
        if 'with ' in code:
            patterns.append('context_manager')
        
        return patterns
    
    def _extract_context_tokens(self, context: str) -> List[str]:
        """Extract meaningful tokens from usage context."""
        if not context:
            return []
        
        # Simple tokenization and filtering
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', context.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        meaningful_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        return meaningful_tokens[:5]  # Limit to 5 most relevant tokens


def enhance_function_with_dense_description(func: Function) -> Function:
    """Enhance a function with dense description for better embeddings."""
    generator = DenseDescriptionGenerator()
    dense_desc = generator.generate_dense_function_description(func)
    
    # Combine original docstring with dense description
    enhanced_docstring = func.docstring or ""
    if enhanced_docstring:
        enhanced_docstring += " | "
    enhanced_docstring += dense_desc
    
    # Create new function object with enhanced description
    return Function(
        id=func.id,
        name=func.name,
        language=func.language,
        file_path=func.file_path,
        line_number=func.line_number,
        params=func.params,
        return_type=func.return_type,
        docstring=enhanced_docstring,
        body_hash=func.body_hash
    )


def enhance_pattern_with_dense_description(pattern: Pattern) -> Pattern:
    """Enhance a pattern with dense description for better embeddings."""
    generator = DenseDescriptionGenerator()
    dense_desc = generator.generate_dense_pattern_description(pattern)
    
    # Combine original context with dense description
    enhanced_context = pattern.usage_context or ""
    if enhanced_context:
        enhanced_context += " | "
    enhanced_context += dense_desc
    
    # Create new pattern object with enhanced description
    return Pattern(
        id=pattern.id,
        name=pattern.name,
        language=pattern.language,
        pattern_type=pattern.pattern_type,
        code_snippet=pattern.code_snippet,
        usage_context=enhanced_context,
        dependencies=pattern.dependencies,
        success_count=pattern.success_count
    )