"""
Configuration Management for CODEX GitHub Interface

This module handles configuration for both GitHub.com and GitHub Enterprise environments
without requiring code duplication. All differences are handled through configuration.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GitHubConfig:
    """
    Configuration class for GitHub interface.
    
    Supports both GitHub.com and Enterprise configurations through the same interface.
    """
    base_url: Optional[str] = None
    enterprise_mode: bool = False
    api_version: str = "2022-11-28"
    timeout: int = 10
    max_retries: int = 3
    
    # Authentication settings
    auth_method: str = "token"  # "token", "app", "oauth"
    token: Optional[str] = None
    app_id: Optional[str] = None
    private_key: Optional[str] = None
    installation_id: Optional[str] = None
    
    # Enterprise-specific settings (automatically ignored for GitHub.com)
    enterprise_ssl_verify: bool = True
    enterprise_ca_bundle: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'GitHubConfig':
        """
        Create configuration from environment variables.
        
        Environment variables supported:
        - GITHUB_ENTERPRISE_URL: Enterprise GitHub URL
        - GITHUB_TOKEN: Personal access token
        - GITHUB_APP_ID: GitHub App ID
        - GITHUB_PRIVATE_KEY: GitHub App private key
        - GITHUB_INSTALLATION_ID: GitHub App installation ID
        - GITHUB_API_VERSION: API version to use
        - GITHUB_TIMEOUT: Request timeout in seconds
        - GITHUB_SSL_VERIFY: SSL verification for enterprise (true/false)
        - GITHUB_CA_BUNDLE: Path to CA bundle for enterprise
        """
        base_url = os.getenv('GITHUB_ENTERPRISE_URL')
        enterprise_mode = base_url is not None
        
        # Determine auth method based on available environment variables
        auth_method = "token"
        if os.getenv('GITHUB_APP_ID') and os.getenv('GITHUB_PRIVATE_KEY'):
            auth_method = "app"
        
        config = cls(
            base_url=base_url,
            enterprise_mode=enterprise_mode,
            api_version=os.getenv('GITHUB_API_VERSION', '2022-11-28'),
            timeout=int(os.getenv('GITHUB_TIMEOUT', '10')),
            max_retries=int(os.getenv('GITHUB_MAX_RETRIES', '3')),
            
            auth_method=auth_method,
            token=os.getenv('GITHUB_TOKEN'),
            app_id=os.getenv('GITHUB_APP_ID'),
            private_key=os.getenv('GITHUB_PRIVATE_KEY'),
            installation_id=os.getenv('GITHUB_INSTALLATION_ID'),
            
            enterprise_ssl_verify=os.getenv('GITHUB_SSL_VERIFY', 'true').lower() == 'true',
            enterprise_ca_bundle=os.getenv('GITHUB_CA_BUNDLE')
        )
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'GitHubConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            GitHubConfig instance
        """
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Auto-detect enterprise mode if base_url is provided
        enterprise_mode = config_data.get('base_url') is not None and \
                         not config_data.get('base_url', '').endswith('github.com')
        
        config_data['enterprise_mode'] = enterprise_mode
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'base_url': self.base_url,
            'enterprise_mode': self.enterprise_mode,
            'api_version': self.api_version,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'auth_method': self.auth_method,
            'enterprise_ssl_verify': self.enterprise_ssl_verify,
            'enterprise_ca_bundle': self.enterprise_ca_bundle
        }
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Note: Sensitive data like tokens and private keys are not saved.
        """
        safe_config = self.to_dict()
        
        with open(config_path, 'w') as f:
            json.dump(safe_config, f, indent=2)
    
    def is_enterprise(self) -> bool:
        """Check if this is an enterprise configuration."""
        return self.enterprise_mode
    
    def get_display_name(self) -> str:
        """Get a human-readable name for this configuration."""
        if self.is_enterprise():
            return f"GitHub Enterprise ({self.base_url})"
        else:
            return "GitHub.com"


class ConfigManager:
    """
    Manages multiple GitHub configurations.
    
    This allows switching between GitHub.com and enterprise configurations
    without code duplication.
    """
    
    def __init__(self):
        self.configs = {}
        self.current_config_name = None
    
    def add_config(self, name: str, config: GitHubConfig) -> None:
        """Add a named configuration."""
        self.configs[name] = config
        
        # Set as current if it's the first config
        if not self.current_config_name:
            self.current_config_name = name
    
    def set_current(self, name: str) -> bool:
        """
        Set the current configuration by name.
        
        Args:
            name: Configuration name
            
        Returns:
            True if successful, False if config not found
        """
        if name in self.configs:
            self.current_config_name = name
            return True
        return False
    
    def get_current(self) -> Optional[GitHubConfig]:
        """Get the current configuration."""
        if self.current_config_name and self.current_config_name in self.configs:
            return self.configs[self.current_config_name]
        return None
    
    def get_config(self, name: str) -> Optional[GitHubConfig]:
        """Get a configuration by name."""
        return self.configs.get(name)
    
    def list_configs(self) -> Dict[str, str]:
        """
        List all configurations with their display names.
        
        Returns:
            Dictionary mapping config names to display names
        """
        return {
            name: config.get_display_name() 
            for name, config in self.configs.items()
        }
    
    def load_from_directory(self, config_dir: str) -> None:
        """
        Load all configuration files from a directory.
        
        Args:
            config_dir: Directory containing JSON configuration files
        """
        if not os.path.exists(config_dir):
            return
        
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                config_name = filename[:-5]  # Remove .json extension
                config_path = os.path.join(config_dir, filename)
                
                try:
                    config = GitHubConfig.from_file(config_path)
                    self.add_config(config_name, config)
                except Exception as e:
                    print(f"Warning: Failed to load config {config_name}: {e}")