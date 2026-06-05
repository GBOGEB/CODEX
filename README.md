# CODEX GitHub Interface Package

CODEX provides GitHub interface and authentication utilities for both GitHub.com and GitHub Enterprise Server without duplicating implementation logic. This repository also carries Wave W000 federation/runtime/telemetry bootstrap assets, but the published Python package remains the GitHub interface package described below.

> **Operating model:** CODEX is a governed federation-runtime repository where CI is the truth-verification gate, Pages is the human-facing portal, DMAIC is the iteration ledger, and bridge/federation outputs are the measurable integration layer. See [`GOVERNANCE.md`](GOVERNANCE.md) for repository identity, the workflow → lane map, and the CI-vs-CD contract.

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

## MASTER Contract Governance Workbench

ABACUS owns contract data. CODEX owns automation. ARTSTYLE owns visualization.

The MASTER Contract Governance Workbench uses YAML SSOT as the authoritative
contract-follow-up record. Excel, HTML, dashboards, and reports are generated
outputs only, and any direct edits to those generated outputs must become change
requests back into SSOT.

### Lifecycle stages

- Selection complete
- Applicant notification complete
- ITT issued
- Clarification period active
- Applicant offers expected July 2026
- Negotiation Round 1
- Negotiation Round 2
- BAFO
- Award recommendation
- Contract award
- PO target 01-Jan-2027
- Execution: 34 calendar months, 6 phases

### Governance rules

1. `MASTER_input/00_ITT_RELEASE_BASELINE/` is locked baseline material.
2. Do not overwrite released ITT documents.
3. All updates must be additive.
4. YAML SSOT is authoritative.
5. Excel, HTML, dashboards and reports are generated outputs only.
6. Any Excel or HTML edits must become change requests back into SSOT.
7. Preserve lineage from source document → requirement → clarification → applicant response → evaluation → negotiation → BAFO → award → execution deliverable.
