# ADR — CODEX 2.0 Authority Integrity

## Status

Proposed for CODEX 2.0 release foundation.

## Decision

CODEX is engineering-aware and engineering-non-authoritative by default.

CODEX may ingest, understand, normalize, validate semantics and provenance,
route, compare, challenge, index, render and return engineering information.
It must not silently mutate, promote or replace engineering truth owned by a
child/domain repository.

For QPS, `GBOGEB/cryoplant-project` remains the engineering authority. CODEX
owns its semantic, provenance, routing, normalization, policy and receipt
surfaces. ABACUS/DOW owns its governed execution/challenge receipts. Neither a
CODEX receipt nor a DOW result may automatically promote child engineering
state.

## Required source identity

Every remote-authority engineering payload admitted to canonical CODEX
processing must preserve:

- repository identity;
- exact commit SHA;
- Git blob SHA where applicable;
- payload SHA-256;
- logical authority ID.

## Allowed CODEX mutations

CODEX may add separately namespaced semantic, provenance, routing, policy,
quality and receipt annotations.

## Forbidden CODEX mutations

CODEX must fail closed on:

- remote engineering mutation;
- parent compliance promotion;
- mirrored reference becoming authority;
- receipt becoming engineering source;
- derived view becoming SSOT;
- DOW result automatically promoting child state;
- cross-domain or cross-bidder state copying without an explicit governed rule.

## Disposition

Engineering concerns detected by CODEX are emitted as findings/receipts and
returned to the engineering authority for ACCEPT, REJECT or DEFER disposition.

## Release consequence

Authority integrity is a CODEX 2.0 P0 release gate. A release candidate cannot
pass while duplicate authorities, unauthorized engineering mutations, orphan
authoritative nodes or unknown authority nodes remain unresolved.
