"""
CODEX GitHub Interface Package

This package provides unified GitHub interface management and authentication
that works seamlessly with both GitHub.com and GitHub Enterprise Server.

Key principle: NO DUPLICATION NEEDED between standard and enterprise setups.
All differences are handled through configuration and runtime detection.
"""

from .github_interface import GitHubInterface
from .authenticator import GitHubAuthenticator
from .config import GitHubConfig, ConfigManager

__version__ = "1.0.0"
__all__ = ["GitHubInterface", "GitHubAuthenticator", "GitHubConfig", "ConfigManager"]


def create_github_client(config: GitHubConfig = None) -> tuple:
    """
    Factory function to create a configured GitHub client.
    
    Args:
        config: GitHubConfig instance, or None to load from environment
        
    Returns:
        Tuple of (GitHubInterface, GitHubAuthenticator)
    """
    if config is None:
        config = GitHubConfig.from_environment()
    
    # Create interface
    interface = GitHubInterface(
        base_url=config.base_url,
        enterprise_mode=config.enterprise_mode,
        api_version=config.api_version
    )
    
    # Create authenticator
    authenticator = GitHubAuthenticator(interface)
    
    # Authenticate based on config
    if config.auth_method == "token" and config.token:
        authenticator.authenticate_with_token(config.token)
    elif config.auth_method == "app" and all([config.app_id, config.private_key, config.installation_id]):
        authenticator.authenticate_with_app(config.app_id, config.private_key, config.installation_id)
    else:
        # Try environment-based authentication
        authenticator.authenticate_from_environment()
    
    return interface, authenticator