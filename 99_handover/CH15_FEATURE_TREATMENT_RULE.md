# Chapter 15 Feature Treatment Rule ("This Is the Way")

This rule defines how Chapter 15 calculator/versioning features move through HANDOVER, canonical artefacts, and archive/prune states in `GBOGEB/CODEX`.

## Decision Framework

### Keep in HANDOVER (do not fold into canonical artefacts yet)

Keep the item in HANDOVER when any of the following is true:

- It is still draft/scaffold-level.
- Review comments are unresolved.
- Checks/regression are incomplete.
- Duplicate content is not yet mapped to reference/interlude.
- TODO governance items are still open.

### Merge into canonical artefacts

Merge when all of the following are true:

- Tests/checks pass.
- Version metadata is explicit and consistent.
- Traceability is preserved.
- Decision log records `keep` or `merge hybrid`.
- No conflict exists with the canonical artefact chain.

### Prune (archive, not delete)

Prune to archive when any of the following is true:

- Content is superseded by a newer accepted version.
- Content duplicates an accepted canonical item.
- Content is temporary review scaffolding.
- Content is marked reference-only and replaced by SSOT source.

Pruning must use archive paths (for example `archive/retired_artifacts/**/*`) and must not hard-delete lineage-critical files.

## Practical Timeline for Chapter 15

1. **Feature branch** — implement calculator/versioning updates.
2. **Handover state** — keep in handover docs while review comments are open.
3. **Stage gate** — run smoke/regression and decide keep/merge/prune.
4. **Release gate** — freeze accepted artefacts + tag/snapshot + bundle archive.
5. **Post-merge cleanup** — prune superseded handover-only files into retired archive paths.

## Required PR Checklist (Chapter 15+)

- [ ] Decision state declared: `HANDOVER`, `CANONICAL`, or `PRUNE`.
- [ ] Test evidence attached (unit + relevant smoke/regression).
- [ ] Version metadata evidence attached (`VERSION.json` / package version / artefact version).
- [ ] Traceability link attached (issue/PR/thread/decision log).
- [ ] If `PRUNE`, archive destination listed and validated.

## Governance Notes

- Prefer merge-forward with explicit decision logs; avoid implicit lifecycle transitions.
- Keep HANDOVER as the controlled staging area, not a permanent sink.
- Treat pruning as lineage-preserving archival, not deletion.
