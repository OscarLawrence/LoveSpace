"""Web search integration using Google Serper and Tavily APIs."""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langchain_google_community.utilities import GoogleSerperAPIWrapper
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


class DocumentationSearcher:
    """Search for documentation URLs using Tavily or Google Serper APIs."""
    
    def __init__(self, provider: str = "auto"):
        """Initialize searcher with auto-detection or specific provider.
        
        Args:
            provider: "auto", "tavily", or "serper"
        """
        self.provider = None
        self.search_client = None
        
        # Auto-detect available provider
        if provider == "auto":
            if TAVILY_AVAILABLE and os.getenv("TAVILY_API_KEY"):
                self.provider = "tavily"
            elif SERPER_AVAILABLE and os.getenv("SERPER_API_KEY"):
                self.provider = "serper"
            else:
                raise ValueError("No search provider available. Set TAVILY_API_KEY or SERPER_API_KEY")
        
        # Initialize specific provider
        if provider == "tavily" or self.provider == "tavily":
            if not TAVILY_AVAILABLE:
                raise ImportError("tavily-python not available")
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("TAVILY_API_KEY environment variable required")
            self.search_client = TavilyClient(api_key=api_key)
            self.provider = "tavily"
            
        elif provider == "serper" or self.provider == "serper":
            if not SERPER_AVAILABLE:
                raise ImportError("langchain-google-community not available")
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                raise ValueError("SERPER_API_KEY environment variable required")
            os.environ["SERPER_API_KEY"] = api_key
            self.search_client = GoogleSerperAPIWrapper()
            self.provider = "serper"
    
    def search_docs(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for documentation and return structured results.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of dicts with 'title', 'url', 'snippet' keys
        """
        # Add documentation-focused terms to query
        doc_query = f"{query} documentation docs tutorial guide"
        
        # Try primary provider first
        if self.provider == "tavily":
            try:
                return self._search_tavily(doc_query, num_results)
            except Exception as e:
                # Fallback to Serper if Tavily fails (quota, network, etc.)
                if SERPER_AVAILABLE and os.getenv("SERPER_API_KEY"):
                    try:
                        # Initialize Serper on-demand
                        os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
                        serper_client = GoogleSerperAPIWrapper()
                        return self._search_serper_with_client(serper_client, doc_query, num_results)
                    except Exception as serper_e:
                        return [{'error': f'tavily_failed:{e}, serper_failed:{serper_e}'}]
                else:
                    return [{'error': f'tavily_failed:{e}, no_serper_fallback'}]
        
        elif self.provider == "serper":
            try:
                return self._search_serper(doc_query, num_results)
            except Exception as e:
                return [{'error': f'serper_failed:{e}'}]
        
        else:
            return [{'error': 'No search provider configured'}]
    
    def _search_tavily(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Tavily API."""
        # Documentation domains to prioritize
        doc_domains = [
            "docs.python.org", "readthedocs.io", "github.com", 
            "docs.astral.sh", "fastapi.tiangolo.com", "docs.pydantic.dev"
        ]
        
        response = self.search_client.search(
            query=query,
            max_results=num_results * 2,  # Get extra to filter
            include_domains=doc_domains,
            search_depth="basic"
        )
        
        doc_results = []
        doc_patterns = [
            'docs.', '.readthedocs.', 'documentation', 'tutorial', 
            'guide', 'manual', 'reference', 'api', 'github.com'
        ]
        
        for result in response.get('results', []):
            url = result.get('url', '')
            title = result.get('title', '')
            content = result.get('content', '')
            
            # Check if it's likely documentation
            is_docs = any(pattern in url.lower() or pattern in title.lower() 
                         for pattern in doc_patterns)
            
            if is_docs and len(doc_results) < num_results:
                doc_results.append({
                    'title': title,
                    'url': url,
                    'snippet': content[:200] + '...' if len(content) > 200 else content
                })
        
        return doc_results
    
    def _search_serper(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Google Serper API."""
        return self._search_serper_with_client(self.search_client, query, num_results)
    
    def _search_serper_with_client(self, client, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Google Serper API with provided client."""
        results = client.results(query)
        
        # Extract organic results
        organic = results.get('organic', [])
        
        # Filter for documentation sites
        doc_results = []
        doc_patterns = [
            'docs.', '.readthedocs.', 'documentation', 'tutorial', 
            'guide', 'manual', 'reference', 'api', 'github.com'
        ]
        
        for result in organic[:num_results * 2]:  # Get extra to filter
            url = result.get('link', '')
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            # Check if it's likely documentation
            is_docs = any(pattern in url.lower() or pattern in title.lower() 
                         for pattern in doc_patterns)
            
            if is_docs and len(doc_results) < num_results:
                doc_results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
        
        return doc_results
    
    def search_simple(self, query: str) -> str:
        """Simple search that returns just URLs for CLI usage."""
        try:
            results = self.search_docs(query, num_results=3)
            if results and 'error' not in results[0]:
                urls = [r['url'] for r in results if 'url' in r]
                return ' '.join(urls)
            else:
                return f"error:search_failed:{results[0].get('error', 'unknown')}"
        except Exception as e:
            return f"error:search_exception:{e}"