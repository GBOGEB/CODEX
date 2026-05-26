# ABACUS / CODEX / FEDERATION Runtime Governance Scaffold

This repository is bootstrapped for **W000** runtime governance.

## Responsibility split

- **ABACUS**: runtime governance, orchestration, telemetry.
- **CODEX**: execution workers, agents, patches, pull requests.
- **FEDERATION**: capability mesh, Office/diagram adapters, binaries, APIs.

## W000 scaffold

- `_config.yml`
- `governance/runtime_governance.yml`
- `governance/agent_registry.yml`
- `governance/federation_registry.yml`
- `docs/index.md`
- `docs/runtime_map.md`
- `scripts/validate_yaml.py`
- `scripts/build_manifest.py`

## Quickstart

```bash
python3 scripts/validate_yaml.py
python3 scripts/build_manifest.py
```
