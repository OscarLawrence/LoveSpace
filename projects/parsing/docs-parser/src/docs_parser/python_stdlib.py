"""Python stdlib documentation parser for docs.python.org."""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from pathlib import Path
import json
import time

try:
    from knowledge.db_manager import ContextDB
    KNOWLEDGE_DB_AVAILABLE = True
except ImportError:
    KNOWLEDGE_DB_AVAILABLE = False


class PythonStdlibParser:
    """Parse Python stdlib documentation from docs.python.org."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.base_url = "https://docs.python.org/3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MomoAI-DocsParser/0.1.0'
        })
        
        # Use knowledge DB if available, fallback to file cache
        if KNOWLEDGE_DB_AVAILABLE:
            self.db = ContextDB()
            self.use_db_cache = True
        else:
            self.cache_dir = cache_dir or Path.home() / ".cache" / "momo-docs"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.use_db_cache = False
    
    def get_function_docs(self, module_name: str, function_name: str) -> Optional[str]:
        """Get documentation for a specific function."""
        cache_key = f"{module_name}.{function_name}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Try to fetch from docs.python.org
        doc_url = f"{self.base_url}/library/{module_name}.html"
        try:
            response = self.session.get(doc_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            dense_doc = self._extract_function_info(soup, function_name)
            
            if dense_doc:
                self._cache_result(cache_key, dense_doc)
                return dense_doc
                
        except Exception as e:
            # Fallback to introspection if web parsing fails
            return self._introspect_function(module_name, function_name)
        
        return None
    
    def _extract_function_info(self, soup: BeautifulSoup, function_name: str) -> Optional[str]:
        """Extract function information from HTML documentation."""
        func_pattern = rf'\b{re.escape(function_name)}\s*\('
        
        signature = None
        description = None
        params = {}
        exceptions = []
        examples = []
        
        # Find function signature and documentation
        for dt in soup.find_all('dt', class_='sig'):
            if re.search(func_pattern, dt.get_text()):
                signature = self._clean_signature(dt.get_text())
                dd = dt.find_next_sibling('dd')
                if dd:
                    description = self._extract_description(dd)
                    params = self._extract_parameters(dd)
                    exceptions = self._extract_exceptions(dd)
                    examples = self._extract_examples(dd)
                break
        
        # Fallback search
        if not signature:
            for code in soup.find_all('code'):
                text = code.get_text()
                if re.search(func_pattern, text) and '(' in text and ')' in text:
                    signature = self._clean_signature(text)
                    parent = code.find_parent(['p', 'div', 'section'])
                    if parent:
                        description = self._extract_description(parent)
                    break
        
        if signature:
            return self._format_enhanced_docs(signature, description, params, exceptions, examples)
        
        return None
    
    def _clean_signature(self, raw_sig: str) -> str:
        """Clean and normalize function signature."""
        # Remove extra whitespace and newlines
        sig = ' '.join(raw_sig.split())
        
        # Extract just the function call part
        match = re.search(r'(\w+\([^)]*\)(?:\s*->\s*\w+)?)', sig)
        if match:
            return match.group(1)
        
        return sig
    
    def _extract_description(self, element) -> str:
        """Extract and clean description text."""
        # Get text content, removing HTML tags
        text = element.get_text()
        
        # Clean up the text
        text = ' '.join(text.split())
        
        # Extract key information (first sentence or two)
        sentences = text.split('.')
        if sentences:
            # Take first sentence and maybe second if first is very short
            desc = sentences[0].strip()
            if len(desc) < 30 and len(sentences) > 1:
                desc += '. ' + sentences[1].strip()
            return desc
        
        return text[:100] + '...' if len(text) > 100 else text
    
    def _format_dense_docs(self, signature: str, description: Optional[str]) -> str:
        """Format documentation in dense AI-friendly format."""
        # Clean up signature to match target format
        cleaned_sig = self._normalize_signature(signature)
        
        if description:
            # Compress description to key terms
            desc_words = description.lower().split()
            key_terms = [w for w in desc_words if len(w) > 3 and w.isalpha()][:3]
            compressed_desc = '_'.join(key_terms) if key_terms else 'function'
            return f"{cleaned_sig} {compressed_desc}"
        else:
            return cleaned_sig
    
    def _normalize_signature(self, signature: str) -> str:
        """Normalize signature to dense format with types."""
        # Extract function name and parameters
        match = re.match(r'(\w+)\s*\((.*?)\)(?:\s*->\s*(.+))?', signature)
        if not match:
            return signature
            
        func_name, params, return_type = match.groups()
        
        # Simplify parameters - remove defaults and complex annotations
        if params:
            param_parts = []
            for param in params.split(','):
                param = param.strip()
                # Remove default values
                if '=' in param:
                    param = param.split('=')[0].strip()
                # Simplify type annotations
                if ':' in param:
                    name, type_hint = param.split(':', 1)
                    type_hint = type_hint.strip()
                    # Simplify common types
                    if 'str' in type_hint.lower():
                        type_hint = 'str'
                    elif 'int' in type_hint.lower():
                        type_hint = 'int'
                    elif 'bool' in type_hint.lower():
                        type_hint = 'bool'
                    param = f"{name.strip()}:{type_hint}"
                param_parts.append(param)
            params_str = ','.join(param_parts)
        else:
            params_str = ''
        
        # Format return type
        if return_type:
            return_type = return_type.strip()
            if 'AST' in return_type:
                return_type = 'AST'
            elif 'None' in return_type:
                return_type = 'None'
        
        # Build normalized signature
        result = f"{func_name}({params_str})"
        if return_type:
            result += f"->{return_type}"
            
        return result
    
    def _extract_parameters(self, element) -> Dict[str, str]:
        """Extract parameter descriptions."""
        params = {}
        text = element.get_text()
        
        # Look for parameter patterns
        param_patterns = [
            r'(\w+)\s*\([^)]*\)\s*[–-]\s*([^.]+)',
            r'(\w+):\s*([^.]+)',
            r'Parameters?\s*:?\s*(\w+)\s*[–-]\s*([^.]+)'
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for name, desc in matches:
                if len(name) < 20 and len(desc) < 100:
                    params[name] = desc.strip()[:30]
        
        return params
    
    def _extract_exceptions(self, element) -> list:
        """Extract exception information."""
        exceptions = []
        text = element.get_text()
        
        # Look for exception patterns
        exc_patterns = [
            r'Raises?\s*:?\s*(\w*Error\w*)[^.]*?([^.]+)',
            r'(\w*Error\w*)\s*[–-]\s*([^.]+)',
            r'(\w*Exception\w*)\s*[–-]\s*([^.]+)'
        ]
        
        for pattern in exc_patterns:
            matches = re.findall(pattern, text)
            for exc_type, desc in matches:
                if exc_type and len(desc) < 50:
                    exceptions.append(f"{exc_type}_{desc.strip()[:20].replace(' ', '_')}")
        
        return exceptions[:3]
    
    def _extract_examples(self, element) -> list:
        """Extract code examples."""
        examples = []
        
        # Look for code blocks
        for code in element.find_all(['code', 'pre']):
            text = code.get_text().strip()
            if len(text) < 100 and ('>>>' in text or '(' in text):
                # Clean up example
                clean_example = ' '.join(text.split())
                if '->' in clean_example or '>>>' in clean_example:
                    examples.append(clean_example[:50])
        
        return examples[:2]
    
    def _format_enhanced_docs(self, signature: str, description: Optional[str], 
                            params: Dict[str, str], exceptions: list, examples: list) -> str:
        """Format enhanced documentation in dense format."""
        parts = [self._normalize_signature(signature)]
        
        if description:
            desc_words = description.lower().split()
            key_terms = [w for w in desc_words if len(w) > 3 and w.isalpha()][:3]
            if key_terms:
                parts.append('_'.join(key_terms))
        
        if params:
            param_strs = [f"{k}={v[:15].replace(' ', '_')}" for k, v in list(params.items())[:3]]
            parts.append(f"params:{','.join(param_strs)}")
        
        if exceptions:
            parts.append(f"raises:{','.join(exceptions)}")
        
        if examples:
            parts.append(f"example:{examples[0]}")
        
        return ' '.join(parts)
    
    def _introspect_function(self, module_name: str, function_name: str) -> Optional[str]:
        """Fallback: use Python introspection to get basic info."""
        try:
            import importlib
            import inspect
            
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                sig = inspect.signature(func)
                
                # Get basic docstring
                doc = inspect.getdoc(func)
                desc = ""
                if doc:
                    # Extract first line of docstring
                    first_line = doc.split('\n')[0].strip()
                    words = first_line.lower().split()[:5]
                    desc = '_'.join(w for w in words if w.isalpha())
                
                return f"{function_name}{sig} {desc}" if desc else f"{function_name}{sig}"
                
        except Exception:
            pass
        
        return None
    
    def _get_cached(self, key: str) -> Optional[str]:
        """Get cached documentation."""
        if self.use_db_cache:
            try:
                result = self.db.conn.execute(
                    "SELECT content FROM external_docs WHERE source = 'python_stdlib' AND entity_id = ? AND cached_at > datetime('now', '-7 days')",
                    [key]
                ).fetchone()
                return result[0] if result else None
            except Exception:
                return None
        else:
            # Fallback to file cache
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        data = json.load(f)
                    if time.time() - data['timestamp'] < 86400:
                        return data['content']
                except Exception:
                    pass
            return None
    
    def _cache_result(self, key: str, content: str) -> None:
        """Cache documentation result."""
        if self.use_db_cache:
            try:
                # Update access count for LRU
                self.db.conn.execute(
                    "INSERT OR REPLACE INTO external_docs (source, entity_id, content, metadata) VALUES ('python_stdlib', ?, ?, json_object('access_count', COALESCE((SELECT json_extract(metadata, '$.access_count') FROM external_docs WHERE source = 'python_stdlib' AND entity_id = ?), 0) + 1))",
                    [key, content, key]
                )
                # Clean old entries (keep 1000 most accessed)
                self.db.conn.execute("""
                    DELETE FROM external_docs 
                    WHERE source = 'python_stdlib' 
                    AND id NOT IN (
                        SELECT id FROM external_docs 
                        WHERE source = 'python_stdlib' 
                        ORDER BY json_extract(metadata, '$.access_count') DESC, cached_at DESC 
                        LIMIT 1000
                    )
                """)
            except Exception:
                pass
        else:
            # Fallback to file cache
            cache_file = self.cache_dir / f"{key}.json"
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'content': content,
                        'timestamp': time.time()
                    }, f)
            except Exception:
                pass