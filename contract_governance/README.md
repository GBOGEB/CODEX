# ABACUS Contract Governance Workbench

This additive workspace contains the CODEX-owned bootstrap foundation for the ABACUS Contract Governance Digital Thread.

## Governance rules

- `MASTER_input/` remains the authoritative document-control location outside git.
- `00_ITT_RELEASE_BASELINE/` is a frozen contractual baseline and must not be mutated by CODEX tooling.
- YAML under `contract_governance/ssot/` is the source of truth.
- Excel, HTML, RTM JSON, and manifests under `snapshots/contract_governance/` are generated artifacts.
- Reproducibility gates compare canonical content hashes rather than `.xlsx` binary hashes.
- The builder creates separate `internal` and `bidder` output tiers; bidder outputs strip internal and evaluation sheets.
- Extraction bindings are recorded by header name and retain observed positions only as audit metadata.

## Commands

```bash
python -m codex.contract_governance.cli build --ssot contract_governance/ssot/abacus_contract_governance.yaml --out snapshots/contract_governance
python -m codex.contract_governance.cli validate --ssot contract_governance/ssot/abacus_contract_governance.yaml --out snapshots/contract_governance
```


## Runtime verification

Install the pinned verification stack before running the gate:

```bash
python -m pip install -r requirements/contract-governance.txt
python -m pip install --no-build-isolation --no-deps -e .
scripts/verify_contract_governance.sh
```

The verification script fails if required runtime dependencies and the `setuptools` build backend are absent, runs the contract governance test suite with `pytest-json-report` so skips/xfails/xpasses/zero collection are rejected from machine-readable results, then executes the generated snapshot build and validate commands. The package install uses `python -m pip install --no-build-isolation --no-deps -e .` after the pinned dependency install, so CI does not re-resolve the runtime stack and already has the build backend required by `pyproject.toml`. Pytest also sets `xfail_strict = true`; the JSON gate still checks xpasses explicitly rather than relying on `--strict-markers`, which only rejects unknown markers. In GitHub Actions, the script emits grouped log sections for the dependency check, pytest gate, CLI build, and CLI validate so merge status can be grounded in runner logs rather than local container networking.
