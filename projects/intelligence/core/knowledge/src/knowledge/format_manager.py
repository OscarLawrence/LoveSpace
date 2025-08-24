#!/usr/bin/env python3
"""
Format Manager for Documentation and Context Compression
Handles dense/natural/verbose formatting with smart defaults and fallbacks.
"""

import os
import re
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class FormatType(Enum):
    """Available format types for documentation and context."""
    DENSE = "dense"
    NATURAL = "natural"
    VERBOSE = "verbose"
    AUTO = "auto"


@dataclass
class FormatConfig:
    """Configuration for format selection."""
    default_format: FormatType = FormatType.DENSE
    fallback_format: FormatType = FormatType.NATURAL
    max_dense_tokens: int = 50
    max_natural_tokens: int = 200
    enable_auto_detection: bool = True


class FormatManager:
    """Manages format selection and compression for different contexts."""
    
    def __init__(self, config: Optional[FormatConfig] = None):
        self.config = config or FormatConfig()
        
        # Context-specific format preferences
        self.context_formats = {
            'ai_workers': FormatType.DENSE,
            'human_chat': FormatType.NATURAL,
            'debugging': FormatType.VERBOSE,
            'legacy_agents': FormatType.NATURAL,
            'api_docs': FormatType.DENSE,
            'error_context': FormatType.VERBOSE
        }
        
        # Load global format override from environment
        self.global_override = self._load_global_format()
    
    def _load_global_format(self) -> Optional[FormatType]:
        """Load global format override from environment variable."""
        env_format = os.getenv('MOMO_DOC_FORMAT', '').lower()
        try:
            return FormatType(env_format) if env_format else None
        except ValueError:
            return None
    
    def select_format(self, 
                     context: str = 'default',
                     requested_format: Optional[str] = None,
                     agent_type: Optional[str] = None) -> FormatType:
        """Select the best format based on context, request, and agent type."""
        
        # 1. Global override takes precedence
        if self.global_override:
            return self.global_override
        
        # 2. Explicit request format
        if requested_format:
            try:
                return FormatType(requested_format.lower())
            except ValueError:
                pass
        
        # 3. Agent-specific preferences
        if agent_type and agent_type in self.context_formats:
            return self.context_formats[agent_type]
        
        # 4. Context-specific preferences
        if context in self.context_formats:
            return self.context_formats[context]
        
        # 5. Default format
        return self.config.default_format
    
    def compress_documentation(self, 
                              title: str,
                              content: str,
                              url: Optional[str] = None,
                              format_type: FormatType = FormatType.DENSE) -> str:
        """Compress documentation into specified format."""
        
        if format_type == FormatType.VERBOSE:
            return self._format_verbose(title, content, url)
        elif format_type == FormatType.NATURAL:
            return self._format_natural(title, content, url)
        elif format_type == FormatType.DENSE:
            return self._format_dense(title, content, url)
        else:  # AUTO
            return self._format_auto(title, content, url)
    
    def _format_verbose(self, title: str, content: str, url: Optional[str]) -> str:
        """Full verbose format with all information."""
        parts = [f"Title: {title}"]
        if content:
            parts.append(f"Content: {content[:500]}{'...' if len(content) > 500 else ''}")
        if url:
            parts.append(f"URL: {url}")
        return " | ".join(parts)
    
    def _format_natural(self, title: str, content: str, url: Optional[str]) -> str:
        """Natural language format optimized for human readability."""
        # Extract key concepts from title
        clean_title = self._clean_title(title)
        
        # Extract key points from content
        key_points = self._extract_key_points(content)
        
        if key_points:
            return f"{clean_title}: {key_points}"
        else:
            return clean_title
    
    def _format_dense(self, title: str, content: str, url: Optional[str]) -> str:
        """Dense format optimized for AI consumption."""
        # Extract domain/topic from title and content
        domain = self._extract_domain(title, content)
        concepts = self._extract_concepts(title, content)
        action = self._extract_action(title, content)
        
        # Build dense representation
        parts = []
        if action:
            parts.append(f"action:{action}")
        if domain:
            parts.append(f"domain:{domain}")
        if concepts:
            parts.extend([f"concept:{c}" for c in concepts[:3]])  # Limit to top 3
        
        return "|".join(parts) if parts else self._fallback_dense(title)
    
    def _format_auto(self, title: str, content: str, url: Optional[str]) -> str:
        """Auto-detect best format based on content complexity."""
        # Simple heuristic: use dense for short content, natural for complex
        if len(content) < 100 and not any(char in content for char in ['\n', '```', 'example']):
            return self._format_dense(title, content, url)
        else:
            return self._format_natural(title, content, url)
    
    def _clean_title(self, title: str) -> str:
        """Clean title for better readability."""
        # Remove common prefixes and suffixes
        title = re.sub(r'^(Chapter \d+\.|Section \d+\.|§\d+\.)', '', title)
        title = re.sub(r' — Python .+$', '', title)
        title = re.sub(r' \| .+$', '', title)
        return title.strip()
    
    def _extract_key_points(self, content: str) -> str:
        """Extract key points from content."""
        if not content:
            return ""
        
        # Look for first sentence or paragraph
        sentences = content.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 150:
                return first_sentence
        
        # Fallback to first 100 characters
        return content[:100].strip() + "..." if len(content) > 100 else content.strip()
    
    def _extract_domain(self, title: str, content: str) -> str:
        """Extract technical domain from title/content."""
        text = f"{title} {content}".lower()
        
        domains = {
            'web': ['http', 'html', 'css', 'javascript', 'react', 'vue', 'express'],
            'api': ['rest', 'api', 'endpoint', 'route', 'fastapi', 'flask'],
            'auth': ['authentication', 'login', 'jwt', 'oauth', 'session'],
            'db': ['database', 'sql', 'postgresql', 'mysql', 'mongodb'],
            'ui': ['component', 'button', 'modal', 'form', 'interface'],
            'python': ['python', 'import', 'def ', 'class ', 'pip'],
            'error': ['error', 'exception', 'debug', 'traceback']
        }
        
        for domain, keywords in domains.items():
            if any(keyword in text for keyword in keywords):
                return domain
        
        return 'general'
    
    def _extract_concepts(self, title: str, content: str) -> List[str]:
        """Extract key concepts from title/content."""
        text = f"{title} {content}".lower()
        
        # Extract technical terms
        concepts = []
        
        # Common patterns
        patterns = [
            r'\b(jwt|oauth|cors|csrf|ssl|tls)\b',
            r'\b(api|rest|graphql|websocket)\b',
            r'\b(react|vue|angular|svelte)\b',
            r'\b(express|fastapi|django|flask)\b',
            r'\b(postgres|mysql|mongodb|redis)\b',
            r'\b(auth|login|signup|session)\b',
            r'\b(component|button|modal|form)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            concepts.extend(matches)
        
        # Remove duplicates and limit
        return list(dict.fromkeys(concepts))[:5]
    
    def _extract_action(self, title: str, content: str) -> str:
        """Extract action/intent from title/content."""
        text = f"{title} {content}".lower()
        
        actions = {
            'create': ['create', 'add', 'build', 'implement', 'setup'],
            'configure': ['configure', 'setup', 'install', 'enable'],
            'handle': ['handle', 'manage', 'process', 'deal'],
            'validate': ['validate', 'check', 'verify', 'test'],
            'secure': ['secure', 'protect', 'encrypt', 'auth'],
            'connect': ['connect', 'integrate', 'link', 'bind']
        }
        
        for action, keywords in actions.items():
            if any(keyword in text for keyword in keywords):
                return action
        
        return 'use'
    
    def _fallback_dense(self, title: str) -> str:
        """Fallback dense format when extraction fails."""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', title.lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return "|".join(keywords[:4])  # Max 4 keywords
    
    def format_function_context(self, 
                               func_name: str,
                               docstring: Optional[str],
                               params: Optional[List[Dict]],
                               file_path: str,
                               line_number: int,
                               format_type: FormatType = FormatType.DENSE) -> str:
        """Format function context information."""
        
        if format_type == FormatType.VERBOSE:
            parts = [f"Function: {func_name}"]
            if docstring:
                parts.append(f"Description: {docstring}")
            if params:
                param_str = ", ".join([p.get('name', '') for p in params])
                parts.append(f"Parameters: {param_str}")
            parts.append(f"Location: {file_path}:{line_number}")
            return " | ".join(parts)
        
        elif format_type == FormatType.NATURAL:
            desc = docstring.split('|')[0] if docstring else 'No description'
            return f"{func_name} - {desc} ({file_path}:{line_number})"
        
        else:  # DENSE or AUTO
            if docstring and '|' in docstring:
                dense_part = docstring.split('|')[-1].strip()
                return f"{dense_part}@{file_path}:{line_number}"
            else:
                params_str = ""
                if params:
                    param_names = [p.get('name', '') for p in params if p.get('name')]
                    params_str = f"({','.join(param_names)})" if param_names else ""
                return f"{func_name}{params_str}:{file_path}:{line_number}"


# Global format manager instance
format_manager = FormatManager()


def get_format_manager() -> FormatManager:
    """Get the global format manager instance."""
    return format_manager


def compress_doc(title: str, 
                content: str = "",
                url: Optional[str] = None,
                format_type: str = "auto",
                context: str = "default") -> str:
    """Convenience function for document compression."""
    fmt = FormatType(format_type.lower()) if format_type != "auto" else format_manager.select_format(context)
    return format_manager.compress_documentation(title, content, url, fmt)