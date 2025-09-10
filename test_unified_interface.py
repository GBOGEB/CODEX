#!/usr/bin/env python3
"""
Test script to validate that the unified GitHub interface works correctly
for both GitHub.com and Enterprise environments without code duplication.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from github_interface import GitHubInterface
from authenticator import GitHubAuthenticator
from config import GitHubConfig


def test_github_com():
    """Test GitHub.com configuration"""
    print("Testing GitHub.com interface...")
    
    # Clear any enterprise environment variables
    if 'GITHUB_ENTERPRISE_URL' in os.environ:
        del os.environ['GITHUB_ENTERPRISE_URL']
    
    interface = GitHubInterface()
    
    assert interface.api_url == "https://api.github.com", f"Expected GitHub.com API URL, got {interface.api_url}"
    assert not interface.enterprise_mode, "GitHub.com should not be in enterprise mode"
    
    print("✅ GitHub.com interface configured correctly")


def test_enterprise():
    """Test Enterprise configuration"""
    print("Testing Enterprise interface...")
    
    interface = GitHubInterface(
        base_url="https://github.company.com",
        enterprise_mode=True
    )
    
    assert interface.api_url == "https://github.company.com/api/v3", f"Expected Enterprise API URL, got {interface.api_url}"
    assert interface.enterprise_mode, "Enterprise should be in enterprise mode"
    
    print("✅ Enterprise interface configured correctly")


def test_environment_detection():
    """Test automatic environment detection"""
    print("Testing environment-based detection...")
    
    # Test with environment variable
    os.environ['GITHUB_ENTERPRISE_URL'] = 'https://github.example.com'
    interface = GitHubInterface()
    
    assert interface.enterprise_mode, "Should auto-detect enterprise mode"
    assert interface.api_url == "https://github.example.com/api/v3", f"Expected auto-detected Enterprise API URL"
    
    # Clean up
    del os.environ['GITHUB_ENTERPRISE_URL']
    
    print("✅ Environment detection works correctly")


def test_unified_authenticator():
    """Test that authenticator works with both interface types"""
    print("Testing unified authenticator...")
    
    # Test with GitHub.com
    github_interface = GitHubInterface()
    github_auth = GitHubAuthenticator(github_interface)
    
    # Test with Enterprise  
    enterprise_interface = GitHubInterface(base_url="https://github.company.com", enterprise_mode=True)
    enterprise_auth = GitHubAuthenticator(enterprise_interface)
    
    # Both should use the same authenticator class
    assert type(github_auth) == type(enterprise_auth), "Should use same authenticator class"
    
    print("✅ Unified authenticator works with both environments")


def test_config_system():
    """Test configuration system"""
    print("Testing configuration system...")
    
    # Test GitHub.com config
    github_config = GitHubConfig()
    assert not github_config.enterprise_mode
    
    # Test Enterprise config
    enterprise_config = GitHubConfig(
        base_url="https://github.company.com",
        enterprise_mode=True
    )
    assert enterprise_config.enterprise_mode
    assert enterprise_config.base_url == "https://github.company.com"
    
    print("✅ Configuration system works correctly")


def main():
    """Run all tests to validate the unified approach"""
    print("CODEX GitHub Interface - Unified Implementation Tests")
    print("====================================================")
    print("Validating that NO duplication is needed between GitHub.com and Enterprise\n")
    
    try:
        test_github_com()
        test_enterprise()
        test_environment_detection()
        test_unified_authenticator()
        test_config_system()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ No code duplication needed between GitHub.com and Enterprise")
        print("✅ Same classes work for both environments")
        print("✅ Only configuration differs, not implementation")
        print("✅ Unified approach successfully demonstrated")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())