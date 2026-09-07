# OCD — CODEX repository operating concept

**ID:** TRIAGE-OCD-CODEX-001

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
Fail closed on digest mismatch, undocumented semantic mutation, missing source identity, invalid schema or unauthorized promotion.