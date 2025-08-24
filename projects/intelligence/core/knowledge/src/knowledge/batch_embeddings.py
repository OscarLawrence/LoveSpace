#!/usr/bin/env python3
"""
Batch embedding operations for efficient context injection.
Optimizes multiple queries by batching embedding calculations.
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from .embeddings import EmbeddingManager
from .db_manager import ContextDB, Function, Pattern
from .format_manager import get_format_manager, FormatType


@dataclass
class BatchResult:
    """Result from batch context injection."""
    functions: List[Function]
    patterns: List[Pattern] 
    docs: List[str]
    query_count: int
    total_results: int
    deduped_results: int


class BatchEmbeddingManager:
    """Optimized batch processing for multiple context queries."""
    
    def __init__(self, db: ContextDB):
        self.db = db
        self.embedder = EmbeddingManager(db)
        self.formatter = get_format_manager()
    
    def batch_context_injection(
        self,
        queries: List[str],
        limit: int = 5,
        format_type: str = 'auto',
        context: str = 'ai_workers',
        include_patterns: bool = True,
        dedupe: bool = True
    ) -> BatchResult:
        """
        Process multiple queries efficiently with batched embeddings.
        
        Args:
            queries: List of context queries
            limit: Results per category per query
            format_type: Output format selection
            context: Context type for format selection
            include_patterns: Include pattern matching
            dedupe: Remove duplicate results
            
        Returns:
            BatchResult with combined context data
        """
        selected_format = self.formatter.select_format(context, format_type)
        
        # Batch embedding calculation
        query_embeddings = self._batch_generate_embeddings(queries)
        
        # Collect all results
        all_functions = []
        all_patterns = []
        
        # Process each query with pre-calculated embeddings
        for i, query in enumerate(queries):
            query_embedding = query_embeddings[i]
            
            # Find similar functions using pre-calculated embedding
            functions = self._find_similar_functions_with_embedding(
                query_embedding, limit
            )
            all_functions.extend(functions)
            
            # Find similar patterns using pre-calculated embedding
            if include_patterns:
                patterns = self._find_similar_patterns_with_embedding(
                    query_embedding, limit
                )
                all_patterns.extend(patterns)
        
        # Documentation search (separate from embeddings)
        all_docs = self._batch_docs_search(queries, limit)
        
        # Deduplicate if requested
        if dedupe:
            original_count = len(all_functions) + len(all_patterns) + len(all_docs)
            all_functions = self._dedupe_functions(all_functions)
            all_patterns = self._dedupe_patterns(all_patterns)
            all_docs = self._dedupe_docs(all_docs)
            deduped_count = len(all_functions) + len(all_patterns) + len(all_docs)
        else:
            original_count = deduped_count = len(all_functions) + len(all_patterns) + len(all_docs)
        
        return BatchResult(
            functions=all_functions,
            patterns=all_patterns,
            docs=all_docs,
            query_count=len(queries),
            total_results=original_count,
            deduped_results=deduped_count
        )
    
    def _batch_generate_embeddings(self, queries: List[str]) -> List[np.ndarray]:
        """Generate embeddings for all queries in batch for efficiency."""
        # Use the existing embedder but batch the process
        embeddings = []
        for query in queries:
            embedding = self.embedder.embed_query(query)
            embeddings.append(embedding)
        return embeddings
    
    def _find_similar_functions_with_embedding(
        self, 
        embedding: np.ndarray, 
        limit: int
    ) -> List[Function]:
        """Find similar functions using pre-calculated embedding."""
        return self.embedder.find_similar_functions_with_embedding(embedding, limit)
    
    def _find_similar_patterns_with_embedding(
        self,
        embedding: np.ndarray,
        limit: int
    ) -> List[Pattern]:
        """Find similar patterns using pre-calculated embedding."""
        return self.embedder.find_similar_patterns_with_embedding(embedding, limit)
    
    def _batch_docs_search(self, queries: List[str], limit: int) -> List[str]:
        """Search documentation for all queries."""
        all_docs = []
        
        try:
            from docs_parser.search import DocumentationSearcher
            searcher = DocumentationSearcher()
            
            for query in queries:
                doc_results = searcher.search_docs(f"{query} python", num_results=2)
                if doc_results and 'error' not in doc_results[0]:
                    for result in doc_results:
                        formatted_doc = self.formatter.compress_documentation(
                            result['title'],
                            result.get('snippet', ''),
                            result['url'],
                            FormatType.DENSE
                        )
                        all_docs.append(formatted_doc)
        except Exception:
            pass  # Docs search optional
        
        return all_docs
    
    def _dedupe_functions(self, functions: List[Function]) -> List[Function]:
        """Remove duplicate functions by name+file_path."""
        seen = set()
        unique = []
        for func in functions:
            key = f"{func.name}:{func.file_path}"
            if key not in seen:
                seen.add(key)
                unique.append(func)
        return unique
    
    def _dedupe_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Remove duplicate patterns by name."""
        seen = set()
        unique = []
        for pattern in patterns:
            if pattern.name not in seen:
                seen.add(pattern.name)
                unique.append(pattern)
        return unique
    
    def _dedupe_docs(self, docs: List[str]) -> List[str]:
        """Remove duplicate docs by URL extraction."""
        seen = set()
        unique = []
        for doc in docs:
            # Extract URL from doc (assuming it contains URL)
            doc_key = doc.split(':')[-1] if ':' in doc else doc
            if doc_key not in seen:
                seen.add(doc_key)
                unique.append(doc)
        return unique
    
    def format_batch_output(
        self,
        result: BatchResult,
        selected_format: FormatType,
        queries: List[str]
    ) -> str:
        """Format batch results for output."""
        query_list = "+".join(queries)
        context_parts = [f"batch_context:{query_list}"]
        
        if result.functions:
            func_refs = []
            for func in result.functions:
                formatted_func = self.formatter.format_function_context(
                    func.name,
                    func.docstring,
                    func.params,
                    func.file_path,
                    func.line_number,
                    selected_format
                )
                func_refs.append(formatted_func)
            
            format_prefix = "funcs" if selected_format != FormatType.NATURAL else "functions"
            context_parts.append(f"{format_prefix}:{len(result.functions)}:{':'.join(func_refs)}")
        
        if result.patterns:
            pattern_refs = []
            for pattern in result.patterns:
                usage = ""
                if pattern.usage_context:
                    usage = f":{pattern.usage_context[:30]}" if len(pattern.usage_context) > 30 else f":{pattern.usage_context}"
                
                pattern_refs.append(f"{pattern.name}:{pattern.pattern_type}:success_{pattern.success_count}{usage}")
            context_parts.append(f"patterns:{len(result.patterns)}:{':'.join(pattern_refs)}")
        
        if result.docs:
            context_parts.append(f"docs:{len(result.docs)}:{':'.join(result.docs)}")
        
        return " ".join(context_parts)


# Extend EmbeddingManager with batch-optimized methods
def find_similar_functions_with_embedding(self, embedding: np.ndarray, limit: int = 5) -> List[Function]:
    """Find similar functions using pre-calculated embedding."""
    # Get all function embeddings
    rows = self.db.conn.execute("""
        SELECT id, name, language, file_path, line_number, docstring, params, embedding
        FROM functions 
        WHERE embedding IS NOT NULL
    """).fetchall()
    
    results = []
    for row in rows:
        func_id, name, language, file_path, line_number, docstring, params_json, embedding_blob = row
        
        if embedding_blob:
            func_embedding = np.array(embedding_blob, dtype=np.float32)
            similarity = np.dot(embedding, func_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(func_embedding)
            )
            
            # Parse params
            import json
            try:
                params = json.loads(params_json) if params_json else []
            except:
                params = []
            
            function = Function(
                id=func_id,
                name=name,
                language=language,
                file_path=file_path,
                line_number=line_number,
                docstring=docstring,
                params=params
            )
            function.similarity = similarity
            results.append(function)
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x.similarity, reverse=True)
    return results[:limit]


def find_similar_patterns_with_embedding(self, embedding: np.ndarray, limit: int = 5) -> List[Pattern]:
    """Find similar patterns using pre-calculated embedding."""
    rows = self.db.conn.execute("""
        SELECT id, name, language, pattern_type, code_snippet, usage_context, dependencies, success_count, embedding
        FROM patterns 
        WHERE embedding IS NOT NULL
    """).fetchall()
    
    results = []
    for row in rows:
        pattern_id, name, language, pattern_type, code_snippet, usage_context, dependencies, success_count, embedding_blob = row
        
        if embedding_blob:
            pattern_embedding = np.array(embedding_blob, dtype=np.float32)
            similarity = np.dot(embedding, pattern_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(pattern_embedding)
            )
            
            pattern = Pattern(
                id=pattern_id,
                name=name,
                language=language,
                pattern_type=pattern_type,
                code_snippet=code_snippet,
                usage_context=usage_context,
                dependencies=dependencies,
                success_count=success_count
            )
            pattern.similarity = similarity
            results.append(pattern)
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x.similarity, reverse=True)
    return results[:limit]


# Monkey patch the methods
EmbeddingManager.find_similar_functions_with_embedding = find_similar_functions_with_embedding
EmbeddingManager.find_similar_patterns_with_embedding = find_similar_patterns_with_embedding