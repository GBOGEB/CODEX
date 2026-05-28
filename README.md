# CODEX GitHub Interface Package

CODEX provides GitHub interface and authentication utilities for both GitHub.com and GitHub Enterprise Server without duplicating implementation logic. This repository also carries Wave W000 federation/runtime/telemetry bootstrap assets, but the published Python package remains the GitHub interface package described below.

## W000 build-out status

The W000 assets are a mix of scaffolding and real executable code:

- **Executable build-out:** `telemetry/pca/drift_monitor.py` now accepts `--baseline` and `--current` JSON metric inputs and emits a structured drift report.
- **Contract scaffolding:** `federation/semantic_index/schema.yaml` defines the dual-render tuple contract and example prefixes.
- **Process guidance:** `agents/codex/MCP_INSTRUCTION.md` and `agents/abacus/FEDERATION_PROTOCOL.md` document the federation metadata, lineage, and drift conventions.
- **Documentation freshness:** repository checks keep documentation and published paths non-stale via manifest, glob, stale, and link validation.

### Drift monitor inputs, outputs, and process

- **Inputs:** two JSON files supplied through `--baseline` and `--current`
- **Output:** a JSON report containing per-dimension deltas, aggregate `drift_variance`, and a bounded drift snapshot/state
- **Process tracking:** covered by `tests/test_drift_monitor.py` and validated with the existing repository governance checks

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
