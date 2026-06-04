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
