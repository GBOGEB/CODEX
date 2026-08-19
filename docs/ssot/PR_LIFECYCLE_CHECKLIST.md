# PR Lifecycle Checklist SSOT

This file is the single source of truth for the drop-in Universal Lifecycle Checklist used by PRs, batches, waves, and child work units. It is intentionally generic and review-first: agents may complete evidence-backed execution items, but must not tick human-only merge-gate items.

```text
# === PR TODO :: UNIVERSAL LIFECYCLE CHECKLIST (drop-in, generic) ===
# Work top-to-bottom. Do NOT skip a phase. Do NOT merge.
# Symbols:  [ ] todo   [~] in-progress   [x] done   [!] blocked   [-] N/A
# States:   PASS | FAIL | PARTIAL | N/A   •   limitations are NEVER silent

## PHASE 0 — FRAME  (before any change)
[ ] Write INTENT (one sentence: why this PR exists)
[ ] Write GOAL (measurable, falsifiable end-state)
[ ] Define SCOPE: IN-SCOPE / OUT-OF-SCOPE / BOUNDARY rule
[ ] Set RISK_CLASS: {REVERSIBLE | IRREVERSIBLE | SECRET-SENSITIVE | EXTERNAL-EFFECT}
[ ] Map IDENTITY: WORK_ID, LEVEL (PROGRAMME→…→SUBTASK), PARENT_ID, DEPENDS_ON, BLOCKS
[ ] Declare TRACK_TYPE per task: [SEQ] serialized | [PAR] parallel
[ ] Emit FEEDFORWARD to first/child unit: intent + constraints + victory criteria

## PHASE 1 — DEFINE VICTORY  (the gate that must exist before coding)
[ ] List V1..Vn as falsifiable pass/fail criteria (NOT a task list)
[ ] Include at minimum:
    [ ] Vx: working tree clean; single coherent commit on stated base
    [ ] Vx: secret-clean (scan for keys/tokens/credentials) → no hits
    [ ] Vx: every intentional shim/exception DOCUMENTED
    [ ] Vx: legacy/ignored inputs WARNED-and-ignored, never silently dropped
    [ ] Vx: build/compile passes; smoke-run passes
    [ ] Vx: input validation / path-safety enforced (reject abs paths, traversal)
    [ ] Vx: audit/log path is append-only AND EXERCISED (not just implemented)
    [ ] Vx: all declared strategies/branches reachable AND exercised
    [ ] Vx: every skipped check labeled ENVIRONMENT-LIMITATION
[ ] Define WORK-UNTIL stop condition (= Victory met OR boundary/blocker hit)

## PHASE 2 — EXECUTE  (stay in scope)
[ ] Implement minimal change to satisfy Victory; no scope creep
[ ] Tag each task [SEQ]/[PAR]; reconcile [PAR] tracks at milestone
[ ] On any out-of-scope need → STOP, emit FEEDBACK, do not expand
[ ] Record PATCH_TYPE: {FEATURE | FIX | HARDENING | VALIDATION | NO-OP}

## PHASE 3 — VERIFY  (evidence, not assertion)
[ ] Run testing ledger; mark each ✅ PASS / ⚠️ ENV-LIMITATION / ❌ FAIL
[ ] Move every claim from IMPLEMENTED → EXERCISED → VERIFIED with evidence
[ ] Exercise audit/log write path with ONE synthetic, reversible input; then restore
[ ] Confirm reversibility: clean tree before AND after; no stray artifacts committed
[ ] Re-run any FEEDBACK-driven fixes and re-verify (close the FB loop)

## PHASE 4 — REPORT  (use Universal Work Report schema)
[ ] Fill §0 Identity/Mapping … §11 Audit/Data
[ ] Victory: tally OVERALL n/total → MET | NOT MET
[ ] Separate OPEN BLOCKERS (in-scope) from ENVIRONMENT-LIMITATIONS (never conflate)
[ ] List ARTIFACTS: runtime-only vs committed vs persistent-verified
[ ] Emit machine-readable twin (§0/§4/§11 as YAML/JSON for rollup)

## PHASE 5 — MILESTONE vs HOLD-POINT
[ ] Soft MILESTONE (tracks continue) reached? set STATUS string
[ ] Hard HOLD-POINT active? (REQUIRED if RISK_CLASS ∈ {IRREVERSIBLE, SECRET-SENSITIVE})
[ ] Confirm NO merge / NO irreversible action performed by agent

## PHASE 6 — DURABLE ANCHOR & MERGE GATE  (human-only release)
[ ] Capture content identity: tree_sha (durable), container_head_sha (ephemeral)
[ ] Flag base_ref_stable: false if commit SHA can re-hash across sessions
[ ] Rule: pin_container_sha=false; pin_remote_sha=true; merge_requires_human_go=true
[ ] HUMAN GO CHECKLIST (agent cannot tick these):
    [ ] push branch to authoritative remote
    [ ] pin remote SHA:  git rev-parse <remote>/<branch>
    [ ] verify tree:     git rev-parse <remote>/<branch>^{tree} == <tree_sha>
    [ ] tree_match == true ? → issue GO   |   differs ? → STOP
[ ] On GO, append closure record:
    merge_gate: {released_by, approved_remote_sha, verified_tree_sha, tree_match, go_issued_at}

## FINAL STATUS (one line)
status: "<PR READY FOR HUMAN REVIEW — REVIEW-FIRST ONLY | MERGED @ <remote_sha>>"

# RULES (always on)
# - No auto-merge. No scope expansion. No silent skips. No secrets committed.
# - FF/FB loops apply ONLY at PROGRAMME→WAVE→SUB-WAVE→PHASE→SPRINT→TASK→SUBTASK.
# - A unit may not START without FF input, nor CLOSE without FB output.
# - Approve durable content (tree_sha), never an ephemeral commit SHA.
# === END PR TODO ===
```

## Operational rules

- Use this checklist at the top of PR bodies and as the entrance gate for CODEX batches.
- Mark limitations explicitly as `ENVIRONMENT-LIMITATION`; never merge them into blockers.
- Treat Phase 6 as human-only unless an explicit follow-on PR implements and approves release automation.
