# Reusable Engineering Model Package Helper

Issue: #237

This is a domain-neutral package pattern for model, ARTSTYLE, ABACUS, or other engineering work products that need deterministic discovery and lightweight session continuity.

## Canonical package files

A package may contain domain-specific content, but these five control surfaces keep the same generic role:

| File | Role |
|---|---|
| `intent_manifest.md` | Why the package exists, scope, authority boundary, inputs, outputs, and explicit exclusions. |
| `session_manifest.md` | Current execution/restart state: exact source/ref, last completed unit, first red, and next bounded action. |
| `index.json` | Machine-generated deterministic file inventory with relative path, byte count, and SHA-256. |
| `glossary.yaml` | Package-local terms and aliases. Parent/global governance remains authoritative where applicable. |
| `progress_21_point.md` | Human-readable progress/checklist surface. It is status/reporting, not an evidence authority by itself. |

## Minimal topology

```text
package/
├── intent_manifest.md
├── session_manifest.md
├── index.json                 # generated
├── glossary.yaml
├── progress_21_point.md
└── <domain files and folders>
```

## Deterministic index refresh

From the CODEX repository:

```bash
python scripts/refresh_model_package_index.py path/to/package
```

The helper recursively records regular files in lexical path order and excludes:

- the generated `index.json` itself;
- `.git/`;
- `__pycache__/`;
- `.pytest_cache/`.

The index contains no timestamps or host-specific absolute paths, so an unchanged package regenerates byte-identically.

## Control rules

1. `index.json` is generated inventory, never a second content authority.
2. A changed file hash refreshes lineage; it does not by itself imply semantic change, acceptance, or compliance credit.
3. Package-local glossary terms must not silently override parent/global governed meanings.
4. `session_manifest.md` records the next executable unit and external blockers so a handover can resume without reconstructing history.
5. Domain-specific evidence stays in its owning repository/package; this helper only standardizes package mechanics.
