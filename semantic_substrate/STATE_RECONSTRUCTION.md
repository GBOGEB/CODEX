# STATE RECONSTRUCTION

## Purpose

This document defines the minimum viable reconstruction sequence for restoring CODEX semantic state after a cold start.

## Reconstruction Sequence

1. Load `semantic_substrate/overlay_ssot.yaml`
2. Validate `semantic_substrate/invariants.yaml`
3. Load active branch topology from `semantic_substrate/branch_dag.yaml`
4. Load semantic evolution from `semantic_substrate/semantic_delta_ledger.yaml`
5. Load return-of-experience data from `semantic_substrate/roe_log.yaml`
6. Determine current active state
7. Resume highest-priority unresolved branch

## Required Runtime Assumptions

- Semantic lineage must remain acyclic
- No governed artifact is orphaned
- Invariants override convenience
- Repeated failures must feed back into governance

## Current Active Focus

- semantic governance bootstrap
- invariant-first CI
- reconstructable semantic runtime
- future tuple replay engine

## Recovery Success Criteria

A recovery is considered successful if:

- active branches are known
- unresolved semantic debt is visible
- next actions are derivable
- lineage continuity is preserved
- validator passes cleanly
