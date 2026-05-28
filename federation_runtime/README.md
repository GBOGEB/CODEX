# Federation Runtime (W003)

This subrepo enclave stages ABACUS ↔ CODEX governed semantic federation runtime assets without mutating root topology.

## Scope
- Governance contracts and PR traceability.
- Schema and parser enforcement for PR-007.
- Deterministic runtime smoke artifacts and CI gates.

## Mandatory Governance
Governed PRs must supply the mandatory federation governance header described in:
- `federation_runtime/schema/governance_header.schema.json`
- `federation_runtime/.github/W003_PR_FOLLOW_UP.md`

## Validation Flow
- Input: the PR body when it contains the `## PR CLASSIFICATION` block, otherwise the PR must update `federation_runtime/.github/W003_PR_FOLLOW_UP.md`.
- Process: `federation_runtime/engines/governance_parser.py` validates the markdown block with `jsonschema`, rejects unknown keys, and blocks unauthorized schema drift outside `TYPE: GOVERNANCE`.
- Output: the CI gate exits non-zero on malformed metadata and emits a traceable pass/fail message for the validated source.
