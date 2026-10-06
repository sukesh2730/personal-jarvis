"""
Web Search Integration for JARVIS - Phase 4
DuckDuckGo search integration for current information access.
"""
from dataclasses import dataclass
from typing import List, Optional
import time


@dataclass
class SearchResult:
    """Data class for search results."""
    title: str
    url: str
    snippet: str


def search_web(query: str, max_results: int = 5, timeout: int = 10) -> List[SearchResult]:
    """
    Search DuckDuckGo and return formatted results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        timeout: Network timeout in seconds (default: 10)
        
    Returns:
        List of SearchResult objects with title, url, snippet
    """
    if not query or not query.strip():
        return []
    
    try:
        from duckduckgo_search import DDGS
        
        results = []
        
        # Use DDGS for search with timeout
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                results.append(SearchResult(
                    title=result.get('title', 'No title'),
                    url=result.get('href', ''),
                    snippet=result.get('body', 'No description available')
                ))
                
                if len(results) >= max_results:
                    break
        
        return results
    
    except ImportError:
        # duckduckgo_search not installed
        return []
    except Exception as e:
        # Network error or other issue
        return []


def format_search_results(results: List[SearchResult]) -> str:
    """
    Format search results for console display.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Formatted string
    """
    if not results:
        return "No results found, sir."
    
    lines = []
    lines.append("=" * 70)
    lines.append("SEARCH RESULTS")
    lines.append("=" * 70)
    lines.append("")
    
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result.title}")
        lines.append(f"   {result.url}")
        lines.append(f"   {result.snippet}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def is_online() -> bool:
    """
    Check if internet connection is available.
    
    Returns:
        True if online, False otherwise
    """
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
