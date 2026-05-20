# DELTA_1 SDLC Compliance Matrix

## Purpose

Define the baseline compliance and governance expectations for recursive GitHub-centered SDLC execution.

---

# Compliance matrix

| Capability | Required | Repository Owner |
|---|---|---|
| Protected main branch | YES | CODEX |
| PR review governance | YES | CODEX |
| CI validation | YES | ABACUS |
| Dependency review | YES | ABACUS |
| Security scanning | YES | ABACUS |
| Release lineage | YES | CODEX |
| Deployment governance | YES | ABACUS |
| Rollback strategy | YES | CODEX + ABACUS |
| Audit evidence | YES | CODEX |
| Runtime ownership | YES | CODEX + ABACUS |

---

# Release gate requirements

## Before merge

- PR review complete
- CI validation successful
- governance review complete
- lineage traceability preserved

## Before release

- release evidence complete
- SemVer tag defined
- deployment strategy confirmed
- rollback strategy documented

## Before production deployment

- protected environment approval
- release candidate validated
- audit lineage complete
- operational ownership confirmed

---

# DELTA_1 governance objective

Compliance exists to ensure:

- deterministic SDLC execution,
- recursive auditability,
- governed delivery evolution,
- reproducible release operations.
