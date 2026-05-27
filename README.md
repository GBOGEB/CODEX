# CODEX GitHub Interface Package

CODEX provides GitHub interface and authentication utilities for both GitHub.com and GitHub Enterprise Server without duplicating implementation logic. The Wave W000 federation/runtime/telemetry files in this repository are bootstrap scaffolding for broader repository governance, but the published Python package remains the GitHub interface package described below.

## Install

```bash
python -m pip install -e '.[dev]'
```

## Quick start

```python
from src import GitHubAuthenticator, GitHubInterface

interface = GitHubInterface()
authenticator = GitHubAuthenticator(interface)

print(interface.api_url)
print(interface.test_connection())
```

## Enterprise configuration

```python
from src import GitHubInterface

interface = GitHubInterface(
    base_url="https://github.company.com",
    enterprise_mode=True,
)

print(interface.api_url)
```

## Examples

```bash
cd examples
python usage_example.py
```

## Validation

```bash
python -m pytest -q tests/test_drift_monitor.py
python scripts/check_manifest.py
python scripts/check_globs.py
python scripts/check_stale.py
python scripts/check_links.py
```

## Repository scaffolding note

- `federation/`, `runtime/`, `governance/`, `agents/`, and `telemetry/` contain early Wave W000 orchestration assets.
- `telemetry/pca/drift_monitor.py` can now compare baseline and current metric JSON files when both inputs are supplied.
