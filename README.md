# CODEX GitHub Interface Package

CODEX provides GitHub interface and authentication utilities for both GitHub.com and GitHub Enterprise Server without duplicating implementation logic. This repository also carries Wave W000 federation/runtime/telemetry bootstrap assets, but the published Python package remains the GitHub interface package described below.

> **Operating model:** CODEX is a governed federation-runtime repository where CI is the truth-verification gate, Pages is the human-facing portal, DMAIC is the iteration ledger, and bridge/federation outputs are the measurable integration layer. See [`GOVERNANCE.md`](GOVERNANCE.md) for repository identity, the workflow → lane map, and the CI-vs-CD contract.


## MASTER Contract Workbench SSOT

CODEX now includes the MASTER Contract Workbench framework under [`MASTER_input/`](MASTER_input/README.md). The framework treats YAML as the governing Single Source of Truth for pre-award, negotiation, award and execution lifecycle management, then generates synchronized Excel, HTML, trace report, dashboard and checkpoint artefacts as derivatives.

```bash
python scripts/generate_contract_workbench.py
python scripts/check_contract_workbench.py
```

The generated artefacts remain non-authoritative; all edits must be merged back through approved change requests in the YAML SSOT. Generated payloads under `MASTER_input/generated/` and runtime checkpoints under `MASTER_input/checkpoints/` are intentionally ignored so binary workbooks and other derivative files do not drift from the YAML source. The guard proves deterministic on-demand generation by comparing portable manifests and SHA-256 output hashes from two temporary generations, reuses existing manifest timestamps for workspace comparisons, and fails if existing generated workspace payloads no longer match regenerated hashes.

## W000 Federated Semantic Trace Bootstrap

This repository now includes a federation bootstrap wave (`W000-FEDERATED-SEMANTIC-TRACE`) to bridge ABACUS, CODEX, and daily chat interaction with dual-render governance:

- Human semantic readability first
- Machine-sequential telemetry for orchestration
- Prefix-driven traceability (`[TOPIC]`, `[TRACE]`, `[WAVE]`, `[DRIFT]`, etc.)
- Completion-vector oriented runtime scoring

Bootstrap artifacts are staged in:
- `.devcontainer/devcontainer.json`
- `federation/semantic_index/schema.yaml`
- `telemetry/pca/drift_monitor.py`
- `agents/codex/MCP_INSTRUCTION.md`
- `agents/abacus/FEDERATION_PROTOCOL.md`
- `.github/pull_request_template.md`
- `runtime/incubator/.gitkeep`

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
