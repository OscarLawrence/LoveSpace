"""Universal documentation parser using docling for any HTML/PDF source."""

import re
from typing import Optional, Dict, List
from urllib.parse import urlparse

try:
    from langchain_docling import DoclingLoader
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    from knowledge.db_manager import ContextDB
    KNOWLEDGE_DB_AVAILABLE = True
except ImportError:
    KNOWLEDGE_DB_AVAILABLE = False


class UniversalParser:
    """Parse documentation from any source using docling."""
    
    def __init__(self):
        if not DOCLING_AVAILABLE:
            raise ImportError("langchain-docling required for universal parsing")
        
        if KNOWLEDGE_DB_AVAILABLE:
            self.db = ContextDB()
            self.use_db_cache = True
        else:
            self.use_db_cache = False
    
    def parse_url(self, url: str, function_name: str = None) -> Optional[str]:
        """Parse documentation from URL."""
        source_type = self._detect_source_type(url)
        cache_key = f"{source_type}:{url}"
        
        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            if function_name:
                return self._extract_function_from_content(cached, function_name)
            return cached
        
        # Parse with docling
        try:
            loader = DoclingLoader(file_path=url)
            docs = loader.load()
            
            # Combine all document content
            content = "\n\n".join(doc.page_content for doc in docs)
            
            # Cache full content
            self._cache_result(cache_key, content, source_type)
            
            # Extract specific function if requested
            if function_name:
                return self._extract_function_from_content(content, function_name)
            
            return content
            
        except Exception as e:
            return None
    
    def _detect_source_type(self, url: str) -> str:
        """Detect documentation source type from URL."""
        domain = urlparse(url).netloc.lower()
        
        if 'docs.python.org' in domain:
            return 'python_stdlib'
        elif 'readthedocs' in domain or 'sphinx' in url.lower():
            return 'sphinx'
        elif 'github.com' in domain:
            return 'github'
        else:
            return 'generic'
    
    def _extract_function_from_content(self, content: str, function_name: str) -> Optional[str]:
        """Extract specific function documentation from markdown content."""
        # Simple search for function name in content
        if function_name.lower() in content.lower():
            # Find the section containing the function
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if function_name.lower() in line.lower() and ('(' in line or 'function' in line.lower()):
                    # Extract context around the match
                    start = max(0, i - 3)
                    end = min(len(lines), i + 15)
                    context = '\n'.join(lines[start:end])
                    
                    # Convert to dense format
                    return self._markdown_to_dense(context, function_name)
        
        # Fallback: return first occurrence
        if function_name in content:
            return f"{function_name}() found_in_docs"
        
        return None
    
    def _markdown_to_dense(self, markdown: str, function_name: str) -> str:
        """Convert markdown documentation to dense format."""
        # Extract signature
        signature = self._extract_signature_from_markdown(markdown, function_name)
        
        # Extract description
        description = self._extract_description_from_markdown(markdown)
        
        # Extract parameters
        params = self._extract_params_from_markdown(markdown)
        
        # Extract exceptions
        exceptions = self._extract_exceptions_from_markdown(markdown)
        
        # Format dense
        parts = [signature] if signature else [function_name]
        
        if description:
            desc_words = description.lower().split()
            key_terms = [w for w in desc_words if len(w) > 3 and w.isalpha()][:3]
            if key_terms:
                parts.append('_'.join(key_terms))
        
        if params:
            param_strs = [f"{k}={v[:15].replace(' ', '_')}" for k, v in list(params.items())[:3]]
            parts.append(f"params:{','.join(param_strs)}")
        
        if exceptions:
            parts.append(f"raises:{','.join(exceptions[:3])}")
        
        return ' '.join(parts)
    
    def _extract_signature_from_markdown(self, markdown: str, function_name: str) -> Optional[str]:
        """Extract function signature from markdown."""
        # Look for code blocks with function signature
        code_pattern = rf'```[^`]*{re.escape(function_name)}\s*\([^`]*```'
        match = re.search(code_pattern, markdown, re.DOTALL)
        if match:
            code_block = match.group(0)
            # Extract just the function line
            for line in code_block.split('\n'):
                if function_name in line and '(' in line:
                    return line.strip('` ')
        
        # Look for inline code
        inline_pattern = rf'`{re.escape(function_name)}\([^`]*\)`'
        match = re.search(inline_pattern, markdown)
        if match:
            return match.group(0).strip('`')
        
        return None
    
    def _extract_description_from_markdown(self, markdown: str) -> str:
        """Extract description from markdown."""
        lines = markdown.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip headers, code blocks, empty lines
            if (line and not line.startswith('#') and 
                not line.startswith('```') and not line.startswith('`') and
                not line.startswith('*') and not line.startswith('-')):
                description_lines.append(line)
                if len(description_lines) >= 2:  # First 2 description lines
                    break
        
        return ' '.join(description_lines)[:100]
    
    def _extract_params_from_markdown(self, markdown: str) -> Dict[str, str]:
        """Extract parameters from markdown."""
        params = {}
        
        # Look for parameter lists
        param_patterns = [
            r'\*\*(\w+)\*\*[:\s]*([^*\n]+)',  # **param**: description
            r'- `(\w+)`[:\s]*([^\n]+)',        # - `param`: description
            r'(\w+)\s*\([^)]*\)[:\s]*([^\n]+)', # param (type): description
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, markdown)
            for name, desc in matches:
                if len(name) < 20 and len(desc) < 100:
                    params[name] = desc.strip()[:30]
        
        return params
    
    def _extract_exceptions_from_markdown(self, markdown: str) -> List[str]:
        """Extract exceptions from markdown."""
        exceptions = []
        
        # Look for exception patterns
        exc_patterns = [
            r'Raises?\s*:?\s*(\w*Error\w*)[^.]*?([^.\n]+)',
            r'(\w*Error\w*)[:\s]*([^\n]+)',
            r'(\w*Exception\w*)[:\s]*([^\n]+)'
        ]
        
        for pattern in exc_patterns:
            matches = re.findall(pattern, markdown, re.IGNORECASE)
            for exc_type, desc in matches:
                if exc_type and len(desc) < 50:
                    exceptions.append(f"{exc_type}_{desc.strip()[:20].replace(' ', '_')}")
        
        return exceptions
    
    def _get_cached(self, key: str) -> Optional[str]:
        """Get cached content."""
        if self.use_db_cache:
            try:
                result = self.db.conn.execute(
                    "SELECT content FROM external_docs WHERE source = 'universal' AND entity_id = ? AND cached_at > datetime('now', '-7 days')",
                    [key]
                ).fetchone()
                return result[0] if result else None
            except Exception:
                return None
        return None
    
    def _cache_result(self, key: str, content: str, source_type: str) -> None:
        """Cache parsed content."""
        if self.use_db_cache:
            try:
                self.db.conn.execute(
                    "INSERT OR REPLACE INTO external_docs (source, entity_id, content, metadata) VALUES ('universal', ?, ?, json_object('source_type', ?, 'access_count', 1))",
                    [key, content, source_type]
                )
            except Exception:
                pass