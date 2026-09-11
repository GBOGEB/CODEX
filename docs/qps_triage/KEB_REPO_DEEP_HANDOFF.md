# KEB repo-deep handoff — QPS / TRIAGE chat-to-GitHub bridge

Status: implementation candidate
Date: 2026-09-11
Repository: `GBOGEB/CODEX`
Role: semantic provenance, contract validation, executable tooling, exact-SHA receipt production.
Authority ceiling: CODEX cannot mutate QPS engineering, compliance, negotiation or release truth.

## 1. Reused current CODEX surfaces

This implementation deliberately extends existing repository-native controls instead of creating another framework island.

- `docs/qps_triage_prompt_sequence.md` — merged by PR #603; canonical prompt/check sequence for QPS + TRIAGE pickup.
- `governance/federation/FEDERATION_ACTIVITY.yaml` — current federation activity projection.
- `PIPELINE/GLOSSARY.yaml` — semantic vocabulary authority used by semantic-runtime/W003 checks.
- `governance/qps_triage/KEB_CONTRACT_v1.json` — repo-specific machine-readable KEB contract added by this wave.
- `tests/test_qps_triage_keb_contract.py` — fail-closed contract regression test.

Recent reusable precedent:

- #587 — QPS glossary semantic validation;
- #591 — floating KEB coverage census;
- #597/#600 — LLDB-DAP + Swift + Docker/runners/MCP runtime-health receipt producer;
- #602 — first-red W103 source-identity gate with bounded metadata/semantic repair.

## 2. KEB object boundary

CODEX receives the minimum redacted/source-bound child contract required to test semantics and provenance. Private bidder/commercial/source evidence remains in the child authority repo or controlled external evidence store.

The KEB lane owns these object families:

```text
KEB_CONTRACT
KEB_SEMANTIC_TERM
KEB_PROVENANCE_EDGE
KEB_VALIDATOR
KEB_RUNTIME_PROBE
KEB_EXACT_SHA_RECEIPT
KEB_DEFERRED_SOURCE_GAP
```

A KEB receipt is incomplete unless it carries producer repo/PR/head SHA, source object identity, contract version, validator/workflow, executed-step count, PASS|FAIL|DEFER, digest, downstream DOW target and child re-entry target.

## 3. Repo-deep pickup sequence

### QTG-00 — recover before changing

Check main, same-day open/draft PRs, merged predecessors, exact-head receipts, existing semantic terms and current first red. Reuse an existing active PR where it already owns the requested surface.

### QTG-01 — bind contract and vocabulary

Map incoming QPS/TRIAGE objects to `KEB_CONTRACT_v1.json`. Reuse `PIPELINE/GLOSSARY.yaml` for new vocabulary. Never establish a parallel semantic dictionary merely because a chat used a new term.

### QTG-02 — execute smallest proof

Prefer an existing validator, W003/semantic-runtime path, unit test, replay, or runtime-health probe. Structural presence is not execution. PASS on executable work requires `executed_steps > 0` and exact producer SHA.

### QTG-03 — recurse on first red

Classify the first observed blocking predicate as metadata, semantic vocabulary, schema, runtime, dependency, provenance or source missing. Repair only that invariant and rerun the same gate. A source gap becomes an explicit DEFER, not a synthetic PASS.

Observed QTG first red on PR #605, head `9a0ee7d1f75efdadce68a9c04f2f5506c049e1bf`:

- W003 run `34554036514` reached GitHub hosted runner `1000236655`;
- setup, checkout, Python setup and dependency installation all PASSed;
- first failing step was `Run governance parser on PR metadata`;
- the PR body used a non-native QTG classification instead of the exact mandatory eight-field governance schema;
- repair: PR #605 body now uses `PR-ID: PR-605`, `WAVE: W108`, `SPRINT: S5-P9`, exact domain, `TYPE: GOVERNANCE`, `CRITICALITY: HIGH`, `TOPOLOGY IMPACT: NO`, and `SCHEMA MUTATION: CONTROLLED`.

This commit intentionally triggers a fresh exact-head execution after that metadata-only repair. W69 zero-delta remains a separately tracked pre-existing execution lane unless evidence demonstrates a causal QTG regression.

### QTG-04 — dispatch to DOW

ABACUS receives only the immutable KEB receipt tuple needed for independent consumption/challenge. Narrative claims without exact producer identity do not qualify for promotion.

### QTG-05 — child re-entry

`GBOGEB/cryoplant-project` remains final QPS disposition authority. KEB PASS is evidence, not final engineering acceptance.

## 4. Transfer contract

Child -> KEB:

```yaml
child_contract:
  repo: GBOGEB/cryoplant-project
  pr: <number>
  head_sha: <sha>
  object_ids: []
  source_authority_state: SOURCE_BOUND|PARTIAL|MISSING
  requested_keb_checks: []
```

KEB -> DOW:

```yaml
keb_receipt:
  producer_repo: GBOGEB/CODEX
  producer_pr: <number>
  producer_head_sha: <sha>
  source_object_ids: []
  contract_version: qps-triage-keb-contract/1.0.0
  workflow_or_validator: <name>
  executed_steps: <integer>
  result: PASS|FAIL|DEFER
  receipt_sha256: <digest>
  downstream_consumer: GBOGEB/ABACUS
  child_reentry_target: GBOGEB/cryoplant-project
```

## 5. FIFO plus adjacency rule

The oldest actionable blocking gate remains primary. While touching the same CODEX surface, low-cost adjacent repairs are allowed only when they reduce known debt without widening the blocking surface. Examples include adding a missing semantic term, tightening a schema assertion, or adding a small regression fixture. A broad refactor is deferred unless it is itself the first red.

## 6. MIP mapping inside CODEX

**Modernize**: repair stale semantic contracts, duplicate runtime ownership, fail-open dependency handling, outdated API patterns and missing tests.

**Innovate**: introduce a bounded alternate edge only with current path, candidate path, hypothesis and target metric.

**Perpetuate**: retain only after observed repeat execution, exact-SHA receipts and no regression threshold violation. `MERGED != PERPETUATED`.

## 7. Definition of done

The CODEX leg is complete for one QPS/TRIAGE item only when the contract is valid, vocabulary is governed, executable work really ran where applicable, the exact-SHA receipt is digest-bound, DOW can consume it without private-source leakage, and child re-entry remains explicit. No KEB-only event changes QPS formal engineering or negotiation score.
