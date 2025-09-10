#!/usr/bin/env python3
"""
CODEX GitHub Interface Usage Example

This example demonstrates how the unified interface works with both 
GitHub.com and GitHub Enterprise without code duplication.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from github_interface import GitHubInterface
from authenticator import GitHubAuthenticator
from config import GitHubConfig, ConfigManager


def example_github_com():
    """Example using GitHub.com"""
    print("=== GitHub.com Example ===")
    
    # Method 1: Direct instantiation (auto-detects GitHub.com)
    interface = GitHubInterface()
    authenticator = GitHubAuthenticator(interface)
    
    print(f"API URL: {interface.api_url}")
    print(f"Enterprise Mode: {interface.enterprise_mode}")
    
    # Test connection (will work without auth for public repos)
    result = interface.test_connection()
    print(f"Connection test: {result}")
    
    # If you have a token, authenticate
    # token = os.getenv('GITHUB_TOKEN')
    # if token:
    #     auth_result = authenticator.authenticate_with_token(token)
    #     print(f"Authentication: {auth_result}")


def example_enterprise():
    """Example using GitHub Enterprise"""
    print("\n=== GitHub Enterprise Example ===")
    
    # Method 1: Using environment variable
    os.environ['GITHUB_ENTERPRISE_URL'] = 'https://github.company.com'
    
    interface = GitHubInterface()
    authenticator = GitHubAuthenticator(interface)
    
    print(f"API URL: {interface.api_url}")
    print(f"Enterprise Mode: {interface.enterprise_mode}")
    
    # Method 2: Direct configuration
    enterprise_interface = GitHubInterface(
        base_url="https://github.company.com", 
        enterprise_mode=True
    )
    
    print(f"Direct config API URL: {enterprise_interface.api_url}")


def example_with_config():
    """Example using configuration files"""
    print("\n=== Configuration-Based Example ===")
    
    # Clear environment variable to demonstrate pure config-based approach
    if 'GITHUB_ENTERPRISE_URL' in os.environ:
        del os.environ['GITHUB_ENTERPRISE_URL']
    
    # Load GitHub.com config
    github_config = GitHubConfig.from_file('github_com_config.json')
    interface = GitHubInterface(
        base_url=github_config.base_url,
        enterprise_mode=github_config.enterprise_mode,
        api_version=github_config.api_version
    )
    
    print(f"Config-based GitHub.com: {interface.api_url}")
    
    # Load Enterprise config
    enterprise_config = GitHubConfig.from_file('enterprise_config.json')
    enterprise_interface = GitHubInterface(
        base_url=enterprise_config.base_url,
        enterprise_mode=enterprise_config.enterprise_mode,
        api_version=enterprise_config.api_version
    )
    
    print(f"Config-based Enterprise: {enterprise_interface.api_url}")


def example_config_manager():
    """Example using the configuration manager for multiple environments"""
    print("\n=== Multiple Environment Management ===")
    
    # Clear environment variable for clean example
    if 'GITHUB_ENTERPRISE_URL' in os.environ:
        del os.environ['GITHUB_ENTERPRISE_URL']
    
    manager = ConfigManager()
    
    # Add GitHub.com config
    github_config = GitHubConfig()
    manager.add_config("github", github_config)
    
    # Add Enterprise config
    enterprise_config = GitHubConfig(
        base_url="https://github.company.com",
        enterprise_mode=True
    )
    manager.add_config("enterprise", enterprise_config)
    
    # List all configurations
    print("Available configurations:")
    for name, display_name in manager.list_configs().items():
        print(f"  {name}: {display_name}")
    
    # Switch between environments
    for config_name in ["github", "enterprise"]:
        manager.set_current(config_name)
        current_config = manager.get_current()
        
        interface = GitHubInterface(
            base_url=current_config.base_url,
            enterprise_mode=current_config.enterprise_mode
        )
        
        print(f"\n{config_name} -> {interface.api_url}")


def main():
    """
    Main example function demonstrating that NO DUPLICATION is needed
    between GitHub.com and Enterprise implementations.
    
    The same code works for both environments!
    """
    print("CODEX GitHub Interface - Unified Implementation")
    print("==============================================")
    print("Demonstrating NO duplication needed between GitHub.com and Enterprise")
    
    example_github_com()
    example_enterprise()
    example_with_config()
    example_config_manager()
    
    print("\n=== Summary ===")
    print("✅ Same GitHubInterface class works for both environments")
    print("✅ Same GitHubAuthenticator class works for both environments")
    print("✅ Only configuration differs - no code duplication needed")
    print("✅ Automatic environment detection based on URLs and env vars")


if __name__ == "__main__":
    main()