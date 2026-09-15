# OCD — CODEX repository operating concept

**ID:** TRIAGE-OCD-CODEX-001

## Authority boundary
QPS engineering authority is external to CODEX and is owned by `GBOGEB/cryoplant-project`.

Canonical child ADR/OCD authority registry:

`ocd-adr/20_canonical/control/QPS_GLOBAL_ADR_OCD_SSOT_v1.json`

CODEX may own and evolve repo-local semantic/provenance/runtime governance, but any QPS engineering content it carries is a non-authoritative projection. Engineering promotion is forbidden; return requires child re-entry/disposition.

## Mission
Receive typed governed payloads, verify schema/semantics/provenance/immutable identity, route authorized payloads through federation and runtime operations, normalize parent returns and return them without taking child engineering authority.

## Operating sequence
`RECEIVE -> SCHEMA -> SEMANTICS -> PROVENANCE/HASH -> RECEIPT -> DISPATCH -> MONITOR/MCP -> NORMALIZE_RETURN -> CHILD`

## Modes
- semantic validation
- provenance certification
- bridge/federation dispatch
- MCP sweep and runtime governance
- return normalization
- release/build verification

## Failure policy
Fail closed on digest mismatch, undocumented semantic mutation, missing source identity, invalid schema or unauthorized QPS engineering promotion.
