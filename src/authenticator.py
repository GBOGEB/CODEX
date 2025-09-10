"""
GitHub Authenticator Module

This module provides authentication capabilities for both GitHub.com and GitHub Enterprise Server.
It uses a unified approach that eliminates the need for separate enterprise authentication logic.
"""

import os
import base64
import json
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta


class GitHubAuthenticator:
    """
    Unified GitHub authenticator for both standard and enterprise environments.
    
    Supports multiple authentication methods:
    - Personal Access Tokens
    - GitHub App authentication  
    - OAuth tokens
    
    No separate implementation needed for enterprise - uses the same logic with different endpoints.
    """
    
    def __init__(self, github_interface=None):
        """
        Initialize authenticator.
        
        Args:
            github_interface: GitHubInterface instance to use for API calls
        """
        self.github_interface = github_interface
        self._token_cache = {}
    
    def authenticate_with_token(self, token: str) -> Dict[str, Any]:
        """
        Authenticate using a personal access token or OAuth token.
        
        Args:
            token: GitHub personal access token or OAuth token
            
        Returns:
            Authentication result dictionary
        """
        if not self.github_interface:
            return {"success": False, "error": "No GitHub interface configured"}
        
        # Test the token by making an authenticated request
        result = self.github_interface.test_connection(token)
        
        if result.get("success"):
            # Cache the token for reuse
            self._token_cache["current"] = {
                "token": token,
                "expires_at": None,  # PATs don't expire automatically
                "type": "personal_access_token"
            }
            
        return result
    
    def authenticate_with_app(self, app_id: str, private_key: str, installation_id: str) -> Dict[str, Any]:
        """
        Authenticate using GitHub App credentials.
        
        Args:
            app_id: GitHub App ID
            private_key: GitHub App private key (PEM format)
            installation_id: Installation ID for the app
            
        Returns:
            Authentication result with installation token
        """
        try:
            # Generate JWT for GitHub App authentication
            jwt_token = self._generate_app_jwt(app_id, private_key)
            
            # Get installation access token
            installation_token = self._get_installation_token(jwt_token, installation_id)
            
            if installation_token:
                # Cache the installation token
                self._token_cache["current"] = {
                    "token": installation_token["token"],
                    "expires_at": installation_token["expires_at"],
                    "type": "app_installation"
                }
                
                return {
                    "success": True,
                    "token": installation_token["token"],
                    "expires_at": installation_token["expires_at"],
                    "type": "app_installation"
                }
            else:
                return {"success": False, "error": "Failed to get installation token"}
                
        except Exception as e:
            return {"success": False, "error": f"App authentication failed: {str(e)}"}
    
    def get_current_token(self) -> Optional[str]:
        """
        Get the current cached authentication token.
        
        Returns:
            Current token string or None if no valid token cached
        """
        cached = self._token_cache.get("current")
        if not cached:
            return None
            
        # Check if token is expired (for app tokens)
        if cached.get("expires_at"):
            expires_at = datetime.fromisoformat(cached["expires_at"].replace('Z', '+00:00'))
            if datetime.now().replace(tzinfo=expires_at.tzinfo) >= expires_at:
                # Token expired, remove from cache
                del self._token_cache["current"]
                return None
                
        return cached.get("token")
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with a valid token."""
        return self.get_current_token() is not None
    
    def authenticate_from_environment(self) -> Dict[str, Any]:
        """
        Attempt to authenticate using environment variables.
        
        Supports:
        - GITHUB_TOKEN: Personal access token
        - GITHUB_APP_ID + GITHUB_PRIVATE_KEY + GITHUB_INSTALLATION_ID: App auth
        
        Returns:
            Authentication result dictionary
        """
        # Try personal access token first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return self.authenticate_with_token(token)
        
        # Try GitHub App authentication
        app_id = os.getenv('GITHUB_APP_ID')
        private_key = os.getenv('GITHUB_PRIVATE_KEY')
        installation_id = os.getenv('GITHUB_INSTALLATION_ID')
        
        if app_id and private_key and installation_id:
            return self.authenticate_with_app(app_id, private_key, installation_id)
        
        return {"success": False, "error": "No authentication credentials found in environment"}
    
    def _generate_app_jwt(self, app_id: str, private_key: str) -> str:
        """
        Generate JWT for GitHub App authentication.
        
        Note: This is a simplified implementation. In production, use a proper JWT library.
        """
        # This would normally use PyJWT or similar library
        # For this example, we'll return a placeholder
        return f"jwt.token.for.app.{app_id}"
    
    def _get_installation_token(self, jwt_token: str, installation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get installation access token using JWT.
        
        Args:
            jwt_token: JWT token for the GitHub App
            installation_id: Installation ID
            
        Returns:
            Installation token info or None if failed
        """
        if not self.github_interface:
            return None
            
        try:
            # Make request to get installation token
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            url = f"{self.github_interface.api_url}/app/installations/{installation_id}/access_tokens"
            
            # This would make an actual API request in a real implementation
            # For this example, return a mock token
            expires_at = (datetime.now() + timedelta(hours=1)).isoformat() + "Z"
            
            return {
                "token": f"ghs_mock_installation_token_{installation_id}",
                "expires_at": expires_at
            }
            
        except Exception:
            return None