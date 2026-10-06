"""
Agent-Reach Integration Module for JARVIS

This module provides integration with Agent-Reach CLI tool for multi-platform
internet access: web search, social media, GitHub, RSS feeds, and more.

Agent-Reach is a CLI wrapper that routes to the best backend for each platform.
"""

import subprocess
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class SearchResult:
    """Represents a search result."""
    title: str
    url: str
    snippet: str
    source: str


class AgentReachOps:
    """Agent-Reach CLI operations manager for JARVIS."""
    
    def __init__(self):
        """Initialize Agent-Reach operations."""
        self.available = self._check_installed()
    
    def _check_installed(self) -> bool:
        """Check if agent-reach CLI is installed."""
        try:
            result = subprocess.run(
                ["agent-reach", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Run an agent-reach command and return parsed output.
        
        Args:
            cmd: Command list to execute
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with success status and output/error
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    # ========== Health Check Operations ==========
    
    def doctor_check(self) -> Dict[str, Any]:
        """
        Run health check to see available backends and platforms.
        
        Returns:
            Dictionary with platform availability info
        """
        result = self._run_command(["agent-reach", "doctor", "--json"])
        if result['success']:
            try:
                return json.loads(result['output'])
            except json.JSONDecodeError:
                return {'error': 'Failed to parse doctor output'}
        return {'error': result['error']}
    
    # ========== Web Search Operations ==========
    
    def web_search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Search the web using Exa (via mcporter).
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        cmd = [
            "mcporter", "call", "exa.web_search_exa",
            f"query={query}",
            f"numResults={num_results}"
        ]
        
        result = self._run_command(cmd)
        if not result['success']:
            return []
        
        # Parse output - this is a simplified parser
        results = []
        try:
            # Agent-Reach returns YAML/JSON output
            # For now, return raw output wrapped
            lines = result['output'].strip().split('\n')
            for i, line in enumerate(lines[:num_results]):
                if line.strip():
                    results.append(SearchResult(
                        title=f"Result {i+1}",
                        url="",
                        snippet=line.strip(),
                        source="Exa"
                    ))
        except Exception:
            pass
        
        return results
    
    # ========== Social Media Operations ==========
    
    def twitter_search(self, query: str, limit: int = 10) -> str:
        """
        Search Twitter/X.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            Formatted search results
        """
        result = self._run_command([
            "twitter", "search", query, "-n", str(limit)
        ])
        
        if result['success']:
            return result['output']
        return f"Error: {result['error']}"
    
    def reddit_search(self, query: str, limit: int = 10) -> str:
        """
        Search Reddit.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            Formatted search results
        """
        # Try OpenCLI first
        result = self._run_command([
            "opencli", "reddit", "search", query, "-f", "yaml"
        ])
        
        if result['success']:
            return result['output']
        
        # Fallback to rdt-cli
        result = self._run_command([
            "rdt", "search", query, "--limit", str(limit)
        ])
        
        if result['success']:
            return result['output']
        
        return f"Error: {result['error']}"
    
    # ========== GitHub Operations ==========
    
    def github_search_repos(self, query: str, limit: int = 10) -> str:
        """
        Search GitHub repositories.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            Formatted search results
        """
        result = self._run_command([
            "gh", "search", "repos", query,
            "--sort", "stars",
            "--limit", str(limit)
        ])
        
        if result['success']:
            return result['output']
        return f"Error: {result['error']}"
    
    # ========== Web Page Reading ==========
    
    def read_webpage(self, url: str) -> str:
        """
        Read and extract clean content from a web page.
        
        Args:
            url: URL to read
            
        Returns:
            Extracted text content
        """
        result = self._run_command([
            "curl", "-s", f"https://r.jina.ai/{url}"
        ], timeout=60)
        
        if result['success']:
            return result['output']
        return f"Error: {result['error']}"
    
    # ========== YouTube Operations ==========
    
    def youtube_subtitles(self, url: str) -> str:
        """
        Download YouTube video subtitles.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Subtitle content or error message
        """
        result = self._run_command([
            "yt-dlp",
            "--write-sub",
            "--write-auto-sub",
            "--skip-download",
            "-o", "/tmp/%(id)s",
            url
        ], timeout=120)
        
        if result['success']:
            return result['output']
        return f"Error: {result['error']}"
    
    # ========== V2EX Operations ==========
    
    def v2ex_hot_topics(self) -> str:
        """
        Get V2EX hot topics.
        
        Returns:
            JSON formatted hot topics
        """
        result = self._run_command([
            "curl", "-s",
            "https://www.v2ex.com/api/topics/hot.json",
            "-H", "User-Agent: agent-reach/1.0"
        ])
        
        if result['success']:
            return result['output']
        return f"Error: {result['error']}"
    
    # ========== Update Check ==========
    
    def check_update(self) -> Dict[str, Any]:
        """
        Check for Agent-Reach updates.
        
        Returns:
            Dictionary with update info
        """
        result = self._run_command(["agent-reach", "check-update"])
        return {
            'success': result['success'],
            'message': result['output'] if result['success'] else result['error']
        }


def format_search_results_ar(results: List[SearchResult]) -> str:
    """
    Format Agent-Reach search results for display.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Formatted string
    """
    if not results:
        return "No results found, sir."
    
    lines = []
    for i, result in enumerate(results, 1):
        lines.append(f"[{i}] {result.title}")
        if result.url:
            lines.append(f"    {result.url}")
        lines.append(f"    {result.snippet}")
        lines.append(f"    Source: {result.source}")
        lines.append("")
    
    return "\n".join(lines)
