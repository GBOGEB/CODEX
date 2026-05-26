# DELTA_1 Branch Protection Manifest

## Purpose

Define the canonical branch protection baseline for GitHub-centered recursive SDLC governance.

---

# Protected branch baseline

## Target branch

```text
main
```

---

# Required controls

| Control | Status |
|---|---|
| Pull request required before merge | REQUIRED |
| Required approvals | REQUIRED |
| Required status checks | REQUIRED |
| Conversation resolution | REQUIRED |
| Protected release lineage | REQUIRED |
| Auditability | REQUIRED |
| GitHub review roundtrip | REQUIRED |

---

# Recommended controls

| Control | Recommendation |
|---|---|
| Signed commits | ENABLE |
| Linear history | ENABLE |
| Merge queue | ENABLE WHEN SCALE REQUIRES |
| SHA-pinned actions | ENABLE |
| Environment-gated deployment | ENABLE |

---

# Merge strategy

## Canonical model

```text
short-lived branch -> PR -> review -> squash merge -> protected main
```

---

# DELTA_1 governance objective

Branch protection exists to:

- preserve release lineage,
- ensure recursive reviewability,
- prevent ungoverned execution drift,
- preserve audit evidence,
- enable deterministic SDLC execution.
