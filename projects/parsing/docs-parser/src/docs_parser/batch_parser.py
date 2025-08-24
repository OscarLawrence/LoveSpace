"""Batch processing for popular Python stdlib functions."""

from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from .python_stdlib import PythonStdlibParser

# Popular stdlib functions to pre-cache
POPULAR_FUNCTIONS = [
    "ast.parse", "json.loads", "json.dumps", "os.path.join", "os.makedirs",
    "re.search", "re.match", "re.findall", "math.sqrt", "math.ceil",
    "datetime.datetime.now", "pathlib.Path", "collections.defaultdict",
    "itertools.chain", "functools.partial", "typing.List", "typing.Dict"
]

class BatchParser:
    """Batch process documentation for performance."""
    
    def __init__(self, parser: PythonStdlibParser):
        self.parser = parser
    
    def warm_cache(self, functions: List[str] = None) -> Dict[str, bool]:
        """Pre-cache popular functions."""
        functions = functions or POPULAR_FUNCTIONS
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for func_spec in functions:
                if '.' in func_spec:
                    module_name, function_name = func_spec.rsplit('.', 1)
                    future = executor.submit(self.parser.get_function_docs, module_name, function_name)
                    futures[func_spec] = future
            
            for func_spec, future in futures.items():
                try:
                    result = future.result(timeout=10)
                    results[func_spec] = bool(result)
                except Exception:
                    results[func_spec] = False
        
        return results
    
    def batch_parse(self, function_specs: List[str]) -> Dict[str, str]:
        """Parse multiple functions efficiently."""
        results = {}
        
        # Check cache first
        cached = {}
        uncached = []
        
        for spec in function_specs:
            if '.' in spec:
                module_name, function_name = spec.rsplit('.', 1)
                cache_key = f"{module_name}.{function_name}"
                cached_result = self.parser._get_cached(cache_key)
                if cached_result:
                    cached[spec] = cached_result
                else:
                    uncached.append(spec)
        
        # Parallel fetch uncached
        if uncached:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                for spec in uncached:
                    module_name, function_name = spec.rsplit('.', 1)
                    future = executor.submit(self.parser.get_function_docs, module_name, function_name)
                    futures[spec] = future
                
                for spec, future in futures.items():
                    try:
                        result = future.result(timeout=15)
                        if result:
                            results[spec] = result
                    except Exception:
                        pass
        
        # Combine results
        results.update(cached)
        return results