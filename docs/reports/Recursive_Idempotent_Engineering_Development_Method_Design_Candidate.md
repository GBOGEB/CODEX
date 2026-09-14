# Recursive & Idempotent Engineering Development Method — Design Candidate

**Status:** historical methodology/design candidate; reconcile against current governance before adoption.  
**Raw provenance:** `19_05_Recursive Idempotent Method.txt`  
**Raw SHA256:** `e0c364bde9cfc716867de8a96393b27c6b88333c086380c1867f87d1be73c404`

## Objective

The source asks what is still missing from a strong operational continuation framework before it becomes a genuinely recursive, idempotent and engineering-governed development system.

Its central conclusion is that the target is **not merely a dashboard**. The intended architecture is a recursive development system combining AI governance, RTM/traceability and a controlled execution orchestrator. fileciteturn632file0L9-L20

## Proposed control architecture

### 1. Authority / source-of-truth hierarchy

The source proposes explicit levels separating immutable references, locked engineering baselines, runtime implementation, visual/UI surfaces and experimental work. The intent is to prevent visual or experimental changes from silently overriding validated engineering meaning. fileciteturn630file0L35-L91

### 2. Formal change classification

Each iteration should declare its change type before work begins, distinguishing engineering calculations, numerical methods, material-property sources, visual/UX changes, export-only work, tests and documentation. Engineering changes require regression/baseline review; visual changes must not mutate numerical logic; test-only work must not alter production output. fileciteturn630file0L95-L133

### 3. Recursive artifact pipeline

The source proposes an explicit loop:

`raw tuples → parser → structured requirements → RTM → task queue → scoped implementation → regression validation → handover → new recursive state`.

The useful idea is not any specific filename; it is that session evidence becomes machine-readable work state rather than requiring repeated human reconstruction. fileciteturn630file0L137-L176

### 4. Golden outputs and regression contracts

Validated engineering outputs should be frozen as golden references and every relevant iteration compared against them. Machine-readable build contracts define what each module may change, what it must not change, and what validation is mandatory. fileciteturn630file0L180-L264

### 5. Explicit execution modes

The source separates THINKING, IMPLEMENTATION and VALIDATION modes so analytical work cannot silently become broad refactoring and validation cannot introduce features. fileciteturn630file0L268-L333

### 6. Release + session continuity

Release artifacts should bind manifests, regression summaries and validated outputs. Session continuity should use a structured state object carrying baseline commit, locked modules, next focus and known limits. fileciteturn630file0L337-L400

## Governing anti-corruption rule

The strongest rule in the source is to **forbid bundling multiple conceptual, visual, equation, export and refactor changes into one iteration**, because mixed-change transactions destroy causal traceability and make recursion unstable. fileciteturn632file0L24-L44

## Current interpretation

Many of these concepts now resemble existing GBOGEB controls—bounded transactions, first-red recursion, source authority, evidence receipts, lossless handover and non-compensating gates. Therefore this source should be treated as **method lineage and a gap checklist**, not as a mandate to create duplicate frameworks or file trees.

## Re-entry / next gate

Before adopting any proposed artifact or schema:

1. map it to current CODEX/QPS governance equivalents;
2. mark `REUSE / MERGE / SUPERSEDE / DROP`;
3. create a new object only for a demonstrated structural gap;
4. preserve the one-bounded-change / one-causal-proof rule.

## Provenance and authority boundary

This document is an editorial rewrite. The original layer order and examples were reorganized into a coherent method architecture; no current repository implementation or authority is inferred from the historical proposal.
