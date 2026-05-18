# Phase-3 Hardening Checklist: Reconstructable Semantic Execution Substrate

## Objective
Convert the Phase-2 substrate into a deterministic, testable, and CI-gated semantic runtime foundation.

## Scope
This checklist defines acceptance criteria for schema stability, replay determinism, invariant enforcement, debt governance, and branch-graph consistency.

## Maturity Gates

### Gate 1 — Schema Governance
- [ ] Tuple schema is versioned (`schema_version`) and immutable per published version.
- [ ] Backward/forward compatibility rules are documented.
- [ ] Migration notes exist for every schema-breaking change.
- [ ] CI validates tuple documents against canonical JSON/YAML schema.

**Acceptance criteria**
- New tuple artifacts fail CI if required fields are missing.
- A schema bump requires an explicit migration entry and changelog item.

### Gate 2 — Deterministic Reconstruction
- [ ] A cold-start reconstruction command exists (from clean checkout).
- [ ] Reconstruction produces deterministic state hash/checksum for same inputs.
- [ ] Replay ordering policy is explicit (topological + timestamp + tie-breaker).
- [ ] Failed reconstruction emits actionable diagnostics.

**Acceptance criteria**
- Two independent runs from the same commit generate identical state digest.
- Drift against manifest snapshot is reported with field-level diffs.

### Gate 3 — Invariant Enforcement
- [ ] Invariant ledger entries include owner, confidence, and validation method.
- [ ] Invariants are tagged as hard/soft constraints.
- [ ] CI blocks merge on hard-invariant violations.
- [ ] Soft-invariant regressions produce warnings + debt entries.

**Acceptance criteria**
- At least one automated validator exists per hard invariant family.
- Invariant history is retained as append-only records.

### Gate 4 — Semantic Debt Governance
- [ ] Debt entries have severity, owner, created_at, due_by, and linked tuples.
- [ ] Debt backlog is queryable by branch and subsystem.
- [ ] Replay quality score includes debt pressure penalty.
- [ ] Weekly debt burn-down trend is generated automatically.

**Acceptance criteria**
- No merge without explicit classification for newly introduced debt.
- Dashboard/report includes debt aging and critical debt count.

### Gate 5 — Branch DAG Integrity
- [ ] Branch DAG is canonicalized as machine-readable artifact.
- [ ] Merge ancestry and semantic conflict markers are encoded.
- [ ] Orphaned/abandoned branches are explicitly marked.
- [ ] Graph validation checks for cycles and broken parent links.

**Acceptance criteria**
- DAG validator passes for every PR touching tuple or manifest state.
- Graph evolution changelog is generated from DAG deltas.

### Gate 6 — CI/CD Operationalization
- [ ] `semantic validate` pipeline stage exists (schema + DAG + invariants).
- [ ] `semantic replay` pipeline stage exists (determinism and drift checks).
- [ ] Quality gate thresholds are codified (fail/warn).
- [ ] Artifact publication includes tuple registry, manifest, and replay report.

**Acceptance criteria**
- Required status checks must pass before merge.
- Build artifacts preserve reconstruction evidence for audit.

## Suggested Command Contract (Implementation Target)
- `make semantic-validate`
- `make semantic-replay`
- `make semantic-report`

## Scorecard (Phase-3 Exit)
Target exit criteria for Phase-3 completion:
- Deterministic reconstruction pass rate: **100%** on protected branches.
- Hard invariant violation escape rate: **0**.
- Critical semantic debt SLA breach: **0**.
- Replay/runtime drift incidents per release: **0**.
- Schema migration completeness: **100%**.

## Recommended Initial Work Packages
1. **Schema & Validator Pack**
   - Canonical schema files
   - Validator CLI + CI integration
2. **Replay Determinism Pack**
   - Reconstruction runner
   - State hashing and diff reporter
3. **Invariant Runtime Pack**
   - Invariant registry normalization
   - Hard/soft enforcement hooks
4. **Graph Integrity Pack**
   - DAG canonical format
   - Cycle/link/conflict validators
5. **Reporting Pack**
   - Replay report artifact
   - Debt + invariant trend metrics

## Definition of Done (Phase-3)
Phase-3 is complete when a cold-start agent can reconstruct, validate, and continue work with deterministic outputs and CI-verifiable semantic guarantees, without relying on implicit narrative interpretation.
