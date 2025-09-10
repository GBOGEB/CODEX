"""
GitHub Interface Management Module

This module provides a unified interface for both GitHub.com and GitHub Enterprise Server,
eliminating the need for code duplication between standard and enterprise environments.
"""

import os
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class GitHubInterface:
    """
    Unified GitHub interface that works with both GitHub.com and GitHub Enterprise.
    
    This design eliminates the need to duplicate code for enterprise environments
    by using configuration-based environment detection and URL construction.
    """
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 enterprise_mode: bool = False,
                 api_version: str = "2022-11-28"):
        """
        Initialize GitHub interface.
        
        Args:
            base_url: Base URL for GitHub instance (None for GitHub.com)
            enterprise_mode: Whether this is a GitHub Enterprise instance
            api_version: GitHub API version to use
        """
        self.enterprise_mode = enterprise_mode
        self.api_version = api_version
        
        # Auto-detect environment or use provided configuration
        self.base_url = self._determine_base_url(base_url)
        self.api_url = self._construct_api_url()
        
    def _determine_base_url(self, provided_url: Optional[str]) -> str:
        """Determine the base URL for the GitHub instance."""
        if provided_url:
            return provided_url.rstrip('/')
        
        # Check for enterprise URL in environment
        enterprise_url = os.getenv('GITHUB_ENTERPRISE_URL')
        if enterprise_url:
            self.enterprise_mode = True
            return enterprise_url.rstrip('/')
            
        # Default to GitHub.com
        return "https://github.com"
    
    def _construct_api_url(self) -> str:
        """Construct the appropriate API URL for the GitHub instance."""
        if self.enterprise_mode and not self.base_url.endswith('github.com'):
            # GitHub Enterprise Server API endpoint
            return f"{self.base_url}/api/v3"
        else:
            # GitHub.com API endpoint
            return "https://api.github.com"
    
    def get_api_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """
        Get standard API headers for requests.
        
        Args:
            token: GitHub token for authentication
            
        Returns:
            Dictionary of headers for API requests
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": self.api_version,
            "User-Agent": "CODEX-GitHub-Interface/1.0"
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        return headers
    
    def test_connection(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to the GitHub instance.
        
        Args:
            token: Optional GitHub token for authenticated requests
            
        Returns:
            Dictionary containing connection test results
        """
        try:
            headers = self.get_api_headers(token)
            response = requests.get(f"{self.api_url}/user", headers=headers, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "api_url": self.api_url,
                "enterprise_mode": self.enterprise_mode,
                "authenticated": token is not None and response.status_code == 200
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "api_url": self.api_url,
                "enterprise_mode": self.enterprise_mode
            }
    
    def get_repository_info(self, owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get repository information from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name  
            token: Optional GitHub token
            
        Returns:
            Repository information dictionary
        """
        try:
            headers = self.get_api_headers(token)
            url = f"{self.api_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text
                }
        except requests.RequestException as e:
            return {"error": str(e)}