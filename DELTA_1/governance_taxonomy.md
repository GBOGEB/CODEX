# DELTA_1 Governance Taxonomy

## Purpose

Define the canonical governance taxonomy for GitHub-centered recursive SDLC execution.

---

# Repository Roles

| Repository | Role |
|---|---|
| GBOGEB/CODEX | Governance, SDLC control, release lineage, orchestration |
| GBOGEB/ABACUS | Execution runtime, CI/CD, DevSecOps, deployment orchestration |

---

# Branch taxonomy

| Type | Pattern |
|---|---|
| Feature | feature/<issue>-<slug> |
| Fix | fix/<issue>-<slug> |
| Chore | chore/<issue>-<slug> |
| Hotfix | hotfix/<issue>-<slug> |
| DELTA program | delta-<program>-<scope> |

---

# PR taxonomy

| Type | Example |
|---|---|
| Governance | DELTA_1_PR_0001 |
| Delivery | DELTA_1_PR_0010 |
| Security | DELTA_1_PR_0020 |
| Release | DELTA_1_PR_0030 |

---

# SDLC lineage layers

1. Specification
2. Governance
3. Planning
4. Branch execution
5. Pull request review
6. CI/CD validation
7. Release lineage
8. Deployment lineage
9. Runtime operations
10. Handoff and audit

---

# Review model

DELTA_1 adopts a recursive GitHub roundtrip model:

Specification -> branch -> commit -> PR -> CI/CD -> review -> refinement -> merge -> release lineage.
