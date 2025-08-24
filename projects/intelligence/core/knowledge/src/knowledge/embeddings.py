"""Vector embeddings for semantic similarity search."""

import os
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv('/home/vincent/Documents/Momo/.env')

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

try:
    import voyageai
    VOYAGE_AVAILABLE = True
except ImportError:
    VOYAGE_AVAILABLE = False

from .db_manager import ContextDB, Function, Pattern
from .dense_descriptions import DenseDescriptionGenerator


class EmbeddingManager:
    """Generate and manage vector embeddings for code elements."""
    
    def __init__(self, db: ContextDB, model_name: str = "auto"):
        self.db = db
        self.model_name = model_name
        self.dense_generator = DenseDescriptionGenerator()
        
        # Auto-select best available model
        if model_name == "auto":
            # Prefer voyage-3-large for best accuracy
            if VOYAGE_AVAILABLE and os.getenv("VOYAGE_API_KEY"):
                self.use_voyage = True
                self.voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
                self.model_name = "voyage-3-large"
                self.embedding_dim = 1024
                self.model = None
                self.use_mistral = False
            elif MISTRAL_AVAILABLE and os.getenv("MISTRAL_API_KEY"):
                self.use_mistral = True
                self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
                self.model_name = "codestral-embed"
                self.embedding_dim = 1536
                self.model = None
                self.use_voyage = False
            else:
                # Use jina-embeddings-v2-base-code for code-specific embeddings
                self.use_mistral = False
                self.use_voyage = False
                os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU to avoid DRCP CUDA conflicts
                self.model = SentenceTransformer("jinaai/jina-embeddings-v2-base-code", device='cpu', trust_remote_code=True)
                self.model_name = "jina-embeddings-v2-base-code"
                self.embedding_dim = 768
        elif model_name == "voyage-3-large":
            if not VOYAGE_AVAILABLE or not os.getenv("VOYAGE_API_KEY"):
                raise ValueError("Voyage AI not available or VOYAGE_API_KEY not set")
            self.use_voyage = True
            self.voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
            self.embedding_dim = 1024
            self.model = None
            self.use_mistral = False
        elif model_name == "codestral-embed":
            if not MISTRAL_AVAILABLE or not os.getenv("MISTRAL_API_KEY"):
                raise ValueError("Mistral API not available or MISTRAL_API_KEY not set")
            self.use_mistral = True
            self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
            self.embedding_dim = 1536
            self.model = None
            self.use_voyage = False
        else:
            self.use_mistral = False
            self.use_voyage = False
            os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU to avoid DRCP CUDA conflicts
            self.model = SentenceTransformer(model_name, device='cpu')
            self.embedding_dim = 384  # Default for most sentence-transformers
    
    def embed_function(self, func: Function, format_type: str = "hierarchical") -> np.ndarray:
        """Generate embedding for function using dense description."""
        # Generate dense semantic description with specified format
        dense_desc = self.dense_generator.generate_dense_function_description(func, format_type)
        
        # Combine original info with dense description
        text_parts = [func.name, dense_desc]
        
        # Add original docstring if available
        if func.docstring:
            text_parts.append(func.docstring)
        
        # Add parameter names
        if func.params:
            if isinstance(func.params, list):
                param_names = []
                for p in func.params:
                    if isinstance(p, dict):
                        param_names.append(p.get('name', ''))
                    else:
                        param_names.append(str(p))
                params = " ".join([name for name in param_names if name])
                if params:
                    text_parts.append(params)
        
        text = " ".join(text_parts)
        return self._encode_text(text)
    
    def embed_pattern(self, pattern: Pattern) -> np.ndarray:
        """Generate embedding for pattern using dense description."""
        # Generate dense semantic description
        dense_desc = self.dense_generator.generate_dense_pattern_description(pattern)
        
        # Combine original info with dense description
        text_parts = [pattern.name, pattern.pattern_type, dense_desc]
        
        # Add original usage context if available
        if pattern.usage_context:
            text_parts.append(pattern.usage_context)
        
        text = " ".join(text_parts)
        return self._encode_text(text)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for search query."""
        return self._encode_text(query)
    
    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text using the selected embedding model."""
        if self.use_voyage:
            # Use Voyage AI embeddings
            response = self.voyage_client.embed([text], model="voyage-3-large")
            embedding = np.array(response.embeddings[0], dtype=np.float32)
            return embedding
        elif self.use_mistral:
            # Use Mistral Codestral embeddings
            response = self.mistral_client.embeddings.create(
                model="codestral-embed",
                inputs=[text]
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        else:
            # Use sentence-transformers
            return self.model.encode(text).astype(np.float32)
    
    def find_similar_functions(self, query: str, limit: int = 5) -> List[Function]:
        """Find functions similar to query using vector search."""
        query_embedding = self.embed_query(query)
        
        # Manual similarity calculation (DuckDB type casting issues)
        sql = """
        SELECT id, name, language, file_path, line_number, params, return_type, docstring, body_hash, embedding
        FROM functions 
        WHERE embedding IS NOT NULL
        """
        
        all_results = self.db.conn.execute(sql).fetchall()
        
        # Calculate similarities manually
        similarities = []
        for row in all_results:
            stored_embedding = np.array(row[9], dtype=np.float32)
            similarity = np.dot(query_embedding, stored_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
            )
            similarities.append((row[:9], float(similarity)))
        
        # Sort and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [s[0] for s in similarities[:limit]]
        
        functions = []
        for row in results:
            func = Function(
                id=row[0], name=row[1], language=row[2], file_path=row[3],
                line_number=row[4], params=row[5], return_type=row[6],
                docstring=row[7], body_hash=row[8]
            )
            functions.append(func)
        
        return functions
    
    def find_similar_patterns(self, query: str, limit: int = 5) -> List[Pattern]:
        """Find patterns similar to query using vector search."""
        query_embedding = self.embed_query(query)
        
        sql = """
        SELECT id, name, language, pattern_type, code_snippet, usage_context, dependencies, success_count, embedding
        FROM patterns 
        WHERE embedding IS NOT NULL
        """
        
        all_results = self.db.conn.execute(sql).fetchall()
        
        # Calculate similarities manually
        similarities = []
        for row in all_results:
            if row[8]:  # Check embedding exists
                stored_embedding = np.array(row[8], dtype=np.float32)
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                similarities.append((row[:8], float(similarity)))
        
        # Sort and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [s[0] for s in similarities[:limit]]
        
        patterns = []
        for row in results:
            pattern = Pattern(
                id=row[0], name=row[1], language=row[2], pattern_type=row[3],
                code_snippet=row[4], usage_context=row[5], dependencies=row[6],
                success_count=row[7]
            )
            patterns.append(pattern)
        
        return patterns
    
    def update_function_embedding(self, func_id: int) -> None:
        """Update embedding for existing function."""
        func = self.db.get_function(func_id)
        if func:
            embedding = self.embed_function(func)
            self.db.conn.execute(
                "UPDATE functions SET embedding = ? WHERE id = ?",
                [embedding.tolist(), func_id]
            )
    
    def update_pattern_embedding(self, pattern_id: int) -> None:
        """Update embedding for existing pattern."""
        patterns = self.db.find_patterns()
        pattern = next((p for p in patterns if p.id == pattern_id), None)
        if pattern:
            embedding = self.embed_pattern(pattern)
            self.db.conn.execute(
                "UPDATE patterns SET embedding = ? WHERE id = ?",
                [embedding.tolist(), pattern_id]
            )
    
    def batch_update_embeddings(self) -> dict[str, int]:
        """Update embeddings for all functions and patterns missing them."""
        stats = {"functions": 0, "patterns": 0}
        
        # Update functions
        functions = self.db.find_functions()
        for func in functions:
            if func.id:
                embedding = self.embed_function(func)
                self.db.conn.execute(
                    "UPDATE functions SET embedding = ? WHERE id = ?",
                    [embedding.tolist(), func.id]
                )
                stats["functions"] += 1
        
        # Update patterns
        patterns = self.db.find_patterns()
        for pattern in patterns:
            if pattern.id:
                embedding = self.embed_pattern(pattern)
                self.db.conn.execute(
                    "UPDATE patterns SET embedding = ? WHERE id = ?",
                    [embedding.tolist(), pattern.id]
                )
                stats["patterns"] += 1
        
        return stats