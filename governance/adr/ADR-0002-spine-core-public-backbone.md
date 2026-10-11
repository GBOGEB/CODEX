# ADR-0002 — SPINE-core: a gated public backbone extracted from CODEX

- **Status:** Proposed
- **Date:** 2026-10-11
- **Supersedes:** none · **Relates to:** ADR-0001 (mechanism ladder), COV-01 (Coverity credential pre-analysis)

## Context

The federation's reusable mechanism (generic numerics, the federation runtime
parse→normalize→render→validate chain, the TypeScript orchestration layer,
drift telemetry, governance schemas) currently lives inside repositories that
also hold contract data, plant parameters and project authority.

Two consequences:

1. **Static analysis is unevenly available.** Coverity Scan is free only for
   public open-source projects. The private repositories can't use it, and the
   public ones mix mechanism with project material.
2. **"Known working" is asserted, not proven.** Nothing shows that the
   mechanism runs without the private material around it.

## Decision

Publish the domain-neutral mechanism as a separate public repository,
**GBOGEB/SPINE-core**. Its content is defined only by
`spine/SPINE_MANIFEST.yaml` and admitted only through an executable gate.

### Admission pipeline (all receipts hashed)

| Step | Tool | Proves | Fails when |
|---|---|---|---|
| 1. Resolve | `tools/spine/spine_gate.py` | the admitted set = include − exclude (+ sanitized overlays) | an include pattern matches nothing |
| 2. Scan | same | no private organisation/project/system terms, no secrets or e-mail addresses | any unallowlisted hit |
| 3. Import closure | same | every repo-local Python import resolves inside the admitted set | backbone imports private code |
| 4. Stage | `tools/spine/spine_stage.py` | the staged tree is byte-identical to the receipt | any sha256 drift |
| 5. Smoke | `spine_stage.py --smoke` | the backbone **executes** with nothing else present (tests, runtime pipeline, fail-closed governance check) | any case misses its expected outcome, or zero cases |

`.github/workflows/spine-gate.yml` runs all five steps and also fails if the
committed `receipts/spine/SPINE_GATE_RECEIPT.json` is stale. Per CODEX rules,
the receipt is regenerated in the same PR that changes the admitted tree.

### v0 admitted set (gate PASS on 2026-10-11, 68 files)

- `pca_engine/**`: generic PCA/NLPCA numerics (README replaced by a sanitized overlay)
- `federation_runtime/engines/{parser,normalize,html_renderer,build_manifest,validator,governance_parser}.py`, `schema/**`, `telemetry/**`
- `orchestration_ts/**`: Express server, routes, tests
- `telemetry/**`: drift monitor
- 7 generic governance schemas

**Held back by the gate on first run** (redact, then re-admit in a later wave):
`federation_runtime/engines/phase0_orchestration.py` (bound to a corporate
document system), `pca_engine/README.md` and
`pca_engine/docs/EMPIRICAL_CONTROL_PROVIDER.md` (project-authority references).

**Never admitted:** contract ingestion, corporate integrations, project
authority schemas, contracts, governance/handover state.

### Consumption

Following the ADR-0001 ladder, the consumers (CODEX, ABACUS, cryoplant-project)
take SPINE-core as a **DEP**: a pinned released package or tag, not a copy. The
code is the same; only the authoritative location moves.

### Static analysis on SPINE-core

- **CodeQL**: default setup, every PR. This is the primary engine.
- **Coverity Scan**: weekly plus manual dispatch, via the COV-01 reusable
  workflow (`build_language: other`, buildless capture). This is the secondary
  engine; its value is interprocedural analysis of the TypeScript server and
  the Python runtime.
- A run without credentials reports **WITHHELD**, never PASS.

## Extraction procedure (owner-executed)

```bash
python tools/spine/spine_gate.py                        # must print SPINE_GATE PASS
python tools/spine/spine_stage.py --out ../spine-stage --smoke   # must print SPINE_SMOKE PASS
# history-preserving variant (provenance): limit history to admitted paths
jq -r '.files[] | select(.overlay_source|not) | .path' receipts/spine/SPINE_GATE_RECEIPT.json > /tmp/spine_paths.txt
git clone --no-local . ../spine-history && cd ../spine-history
git filter-repo --paths-from-file /tmp/spine_paths.txt
gitleaks detect --log-opts="--all"                      # history must also be clean
# then copy overlays from the staged tree, push to GBOGEB/SPINE-core
```

The history scan is mandatory. The gate checks the *current* tree only, and a
secret removed from HEAD can still be present in earlier commits.

## Consequences

- **+** Coverity and CodeQL coverage for the shared mechanism, with no
  exposure of private material.
- **+** "Known working" becomes a receipt (tree digest plus smoke verdicts)
  rather than a claim.
- **+** The deny-list is a reviewable SSOT. Widening scope requires editing
  the manifest, which goes through a PR.
- **−** There are two locations until consumers switch to DEP. The gate's
  drift check keeps them byte-identical in the meantime.
- **−** The deny-list catches names, not semantics. Review of the admitted
  set remains a human gate.

## Non-compensation

SPINE-core status (gate, smoke, scans) never compensates, reorders or
substitutes #923, W248, GT_BDQ_0..9, or any QPS release gate.
