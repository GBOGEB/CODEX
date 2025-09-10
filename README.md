# CODEX GitHub Interface Management

CODEX provides unified GitHub interface management and authentication that works seamlessly with both GitHub.com and GitHub Enterprise Server.

## Key Principle: No Duplication Needed

**Answer to the question: "Do I need to duplicate in enterprise as well?"**  
**NO** - This implementation eliminates the need for code duplication between standard GitHub and enterprise environments.

## Features

- ✅ **Unified Interface**: Same code works with GitHub.com and GitHub Enterprise Server
- ✅ **Automatic Detection**: Environment-based detection of GitHub vs Enterprise
- ✅ **Multiple Auth Methods**: Support for tokens, GitHub Apps, and OAuth
- ✅ **Configuration-Driven**: All differences handled through configuration
- ✅ **No Code Duplication**: Single implementation for both environments

## Quick Start

### Basic Usage (GitHub.com)
```python
from src import GitHubInterface, GitHubAuthenticator

# Auto-detects GitHub.com
interface = GitHubInterface()
authenticator = GitHubAuthenticator(interface)

# Test connection
result = interface.test_connection()
print(f"Connected to: {interface.api_url}")
```

### Enterprise Usage
```python
# Method 1: Environment variable
import os
os.environ['GITHUB_ENTERPRISE_URL'] = 'https://github.company.com'
interface = GitHubInterface()  # Auto-detects enterprise

# Method 2: Direct configuration
interface = GitHubInterface(
    base_url="https://github.company.com",
    enterprise_mode=True
)

print(f"Enterprise API: {interface.api_url}")
# Output: Enterprise API: https://github.company.com/api/v3
```

## Architecture

The unified architecture prevents duplication through:

1. **Single Interface Class**: `GitHubInterface` handles both environments
2. **Configuration-Based URLs**: API endpoints constructed based on environment
3. **Unified Authentication**: Same `GitHubAuthenticator` for both environments
4. **Environment Detection**: Automatic detection of GitHub vs Enterprise setup

## Directory Structure

```
CODEX/
├── src/
│   ├── __init__.py              # Main package interface
│   ├── github_interface.py      # Unified GitHub interface
│   ├── authenticator.py         # Unified authentication
│   └── config.py                # Configuration management
├── examples/
│   ├── usage_example.py         # Usage examples
│   ├── github_com_config.json   # GitHub.com configuration
│   └── enterprise_config.json   # Enterprise configuration
└── README.md
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_ENTERPRISE_URL` | Enterprise GitHub base URL | `https://github.company.com` |
| `GITHUB_TOKEN` | Personal access token | `ghp_xxx` |
| `GITHUB_APP_ID` | GitHub App ID | `123456` |
| `GITHUB_PRIVATE_KEY` | GitHub App private key | `-----BEGIN PRIVATE KEY-----` |
| `GITHUB_INSTALLATION_ID` | GitHub App installation ID | `789012` |

## Configuration Examples

### GitHub.com Configuration
```json
{
  "base_url": null,
  "enterprise_mode": false,
  "api_version": "2022-11-28",
  "auth_method": "token"
}
```

### Enterprise Configuration
```json
{
  "base_url": "https://github.company.com",
  "enterprise_mode": true,
  "api_version": "2022-11-28",
  "auth_method": "token",
  "enterprise_ssl_verify": true
}
```

## API Differences Handled Automatically

| Environment | API Base URL | Handled By |
|-------------|-------------|------------|
| GitHub.com | `https://api.github.com` | Auto-detection |
| Enterprise | `https://your-domain.com/api/v3` | URL construction |

## Usage Patterns

### Pattern 1: Environment-Based Auto-Detection
```python
# Set environment variable for enterprise
os.environ['GITHUB_ENTERPRISE_URL'] = 'https://github.company.com'

# Same code works for both environments
interface = GitHubInterface()
authenticator = GitHubAuthenticator(interface)
```

### Pattern 2: Configuration-Based Setup
```python
from src import GitHubConfig

# Load configuration (works for both environments)
config = GitHubConfig.from_environment()
interface = GitHubInterface(
    base_url=config.base_url,
    enterprise_mode=config.enterprise_mode
)
```

### Pattern 3: Multiple Environment Management
```python
from src import ConfigManager

manager = ConfigManager()
manager.add_config("github", GitHubConfig())
manager.add_config("enterprise", GitHubConfig(
    base_url="https://github.company.com",
    enterprise_mode=True
))

# Switch between environments without code changes
manager.set_current("enterprise")
config = manager.get_current()
```

## Running Examples

```bash
cd examples
python usage_example.py
```

## Benefits of Unified Approach

1. **Maintenance**: Single codebase to maintain instead of duplicated code
2. **Consistency**: Same API and behavior across environments
3. **Testing**: Test once, works everywhere
4. **Configuration**: Only configuration differs, not implementation
5. **Deployment**: Same deployment process for both environments

## Answer to Original Question

**"Do I need to duplicate in enterprise as well?"**

**NO** - This implementation demonstrates that you can have a single, unified codebase that works with both GitHub.com and GitHub Enterprise Server through configuration-based differences rather than code duplication.

The same classes, methods, and logic work for both environments - only the URLs and configuration parameters change.
