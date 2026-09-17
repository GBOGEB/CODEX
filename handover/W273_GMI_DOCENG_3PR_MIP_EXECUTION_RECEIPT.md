# W273 GMI DOCENG 3PR + MIP execution receipt

## Bound scope

This CODEX branch is the implementation leg of the GMI-DOCENG cross-agent bridge.
It provides a fail-closed local package guard and tests only materialization/source-binding predicates.

## Exact external bindings

- Google Drive package: `GMI-DOCENG-001`
- Bound `cli.py` SHA-256: `07ee6369982bcb473b293782fa0e76f56cae3dfc8eb45d41323f694fbe138893`
- CODEX PR: `#760`
- ABACUS receiver PR: `#1261`
- QPS child-authority PR: `#1442`

## Guard semantics

- `REJECT`: required core file absent or `cli.py` digest mismatch.
- `DEFER_SOURCE_BINDING`: core bridge materialized but no authoritative `Master.md` or `Master.docx` is bound.
- `ACCEPT_MATERIALIZED_CORE`: core bridge and authoritative source are present; this is still not QPS global CONTROL.

## Non-compensating protection

ABACUS receiver success carries zero engineering credit. CODEX implementation success does not grant QPS acceptance. QPS remains the sole child acceptance/re-entry authority. Missing authoritative source, replay, round-trip, Alexandria runtime, or production predicates remain independently WITHHELD.

## First-red repair note

Initial W003 admission failed because PR #760 lacked the repository-mandatory `## PR CLASSIFICATION` metadata block. The PR metadata was repaired to the governed schema before this synchronization commit. This commit exists partly to force an exact-head hosted re-entry against that corrected metadata.
