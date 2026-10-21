# MYCELIUM Continuity v0.7 — standalone source-owned CODEX adapter

This is a self-contained Python 3.11 read-only adapter **inside the canonical CODEX MYCELIUM owner**. It does not create a new governance SSOT, a new canonical BD root registry or a second mutating scheduler. Its HTML is an *optional materialised review surface*, not a replacement for the canonical six-view `docs/missioncontrol_mycelium.html`.

## Entrypoint and design authority

- Canonical CODEX UI/governance: `mission_control/mycelium/control_manifest.yaml`
- Canonical CODEX gateway: `mission_control/mycelium/execution_gateway_contract.yaml` (default DENY)
- Mission Control Golden Thread: `GBOGEB/pipeline-automation-hub/mission-control/golden-thread/golden_thread.py`
- Mission Control SIPOC instance scheduler: `GBOGEB/pipeline-automation-hub/mission-control/gogreen/sipoc_instances.py`
- ABACUS root ledger: `GBOGEB/ABACUS#1929`; QPS child canonical release remains QPS-owned.

### Standalone replay

Supply the *owner's original N1 ZIP* and a **new, exact-source, current** connector readback JSON without embedding credentials or private source in this repository:

```sh
export PYTHONPATH=mission_control/mycelium/continuity
python -m mycelium_continuity.cli build \
  --n1 /path/to/CODE_PURPLE_MYCELIUM_CONVERGENCE_N1.zip \
  --readback /path/to/current_source_readback.json \
  --out /tmp/code-purple-mycelium-n7 \
  --native /path/to/verified-exact-head-native-artifact.zip
python -m mycelium_continuity.cli verify --out /tmp/code-purple-mycelium-n7
```

`--native` is optional, but **no** output is allowed to claim locally byte-verified receipt evidence if it is absent or its expected SHA-256 differs. The N1 ZIP must supply the exact six original entries; a synthetic input is accepted only with explicitly synthetic provenance.

## Evidence levels and no-false-closure

`DECLARED`, `HISTORICAL`, `OBSERVED`, `RECEIPT_BOUND`, `ACCEPTED` are distinct. An `ACCEPTED` edge requires a separate owner/reviewer decision; this adapter currently emits none. The universal reference graph may contain feedback cycles; the executable SIPOC projection must be a DAG. There is no GitHub write adapter, arbitrary command executor, client secret, runner dispatch, waiver or branch-policy mutation.

## Tests / coverage

```sh
export PYTHONPATH=mission_control/mycelium/continuity
python -m unittest discover -s mission_control/mycelium/continuity/tests -p 'test_portable.py' -v
```

Public-safe **synthetic** tests probe 8+10+22 lineage retention, 85/115 typed graph invariants, cycles, false proof, missing owners, bitemporal hash replay, malicious script content, and bundle hash parity. They cannot claim native ABACUS root closure, coverage on a different repository or independent statistical inference. Do not commit the user's original N1 ZIP or downloaded native artifact to the public CODEX repository; the portable continuation ZIP is distributed separately by the owner.

### N10 terminal reconciliation

`N10_TERMINAL_RECONCILIATION_20261021.json` re-reads the four N9 PR-head runs and both owner branches. `mycelium_continuity.terminal_reconciliation` binds it to the N9 snapshot by SHA-256 (N9 is never rewritten), requires the same case and owner population, only allows non-terminal → terminal moves, and only lets a terminal outcome change through a recorded re-run (`run_attempt>1`). Observed: the two CODEX runs that were `queued` at N9 resolved to `failure` after their PRs merged. Admission stays HOLD; effective required status and CPQ-016 remain owner/admin evidence.

```sh
python -m unittest discover -s mission_control/mycelium/continuity/tests -p 'test_terminal_reconciliation_public.py' -v
```

## Three recursive pulses

1. **P1 — Intent and original-lineage freeze:** confirm N1 input 8 SIPOC/10 dependency/22 historical PR records, owner crosswalk, 20 feature decisions (GROW, HOLD, PRESERVE, PRUNE_CANDIDATE_ONLY).
2. **P2 — Type-safe topology / Golden Thread bridge:** preserve original process graph and add a typed federation and evidence graph. Edges and candidate roots remain source-scoped.
3. **P3 — Exact-head testflight and visual reproducibility:** verify all metadata, fail-closed cases, local/statistical scope, responsive six panels, bundle/manifest and source drift. GitHub exact-head workflow success is separate from accepted owner CONTROL.

## Security and owner policies

`authority_transfer=false`, `P0_ADMISSION=HOLD`, `merge_authorized=false`, `remote_mutation_enabled=false`, `security_waiver=false`, `accepted_causal_root_closures=null`.

No source PR should be merged while required checks are pending/red. CODEX branch protection and independent review remain separate controls.