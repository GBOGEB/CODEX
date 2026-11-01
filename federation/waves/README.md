# Federation wave register (CANDIDATE, v0.1)

One index of every wave id the federation uses, with a namespace that removes
the ambiguity of a bare "W". CODEX owns the index, not the waves: status stays
with the owning repo (`authority: index_only`, `authority_transfer: false`).

| File | Role |
|---|---|
| `WAVE_NAMESPACES.yaml` | Hand-maintained SSOT: namespaces (QPS, HYG, ULTRA, BOOT, CP, JADE), matching rules, status enum |
| `WAVE_REGISTER.yaml` | Generated. Do not edit. Every entry is `<NS>:<id>` with per-repo path counts and an anchor directory |
| `../../scripts/build_wave_register.py` | Generator (stdlib + PyYAML, deterministic, SHA-anchored) |
| `../../tests/test_wave_register.py` | Contract: ASCII, unique keys, known namespaces, no private file names, SHA anchors |

## Regenerate

Clone the members side by side, then run from the CODEX root:

```
python scripts/build_wave_register.py --repo GBOGEB/CODEX=. \
  --repo GBOGEB/ABACUS=../ABACUS --repo GBOGEB/pipeline-automation-hub=../pipeline-automation-hub \
  --repo GBOGEB/DOCX_RTM_Automation=../DOCX_RTM_Automation \
  --repo GBOGEB/document-organization-system=../document-organization-system \
  --private GBOGEB/cryoplant-project=../cryoplant-project
```

`--private` repos contribute only ids, path counts and a directory anchor:
CODEX is public.

## Seed findings (2026-11-01)

- **371 entries across 6 namespaces.** QPS has 338, BOOT 10, CP 7, HYG 7, JADE 6 and ULTRA 3. 156 entries appear in more than one repo.
- **The QPS exact range is W10..W381, with 44 gaps.** Gaps are unused numbers. They are not missing work.
- **The current-wave pointers disagree.** CODEX `handover/CURRENT.json` says `Wave-0`, while the ABACUS and cryoplant `MESH_DOCK.yaml` both say `QPS:W113`. A fresh agent entering CODEX starts from a stale pointer.
- **Single-digit ids outside a namespace context are tagged `QPS` with `confidence: inferred`.** These are QPS:W000..W009. They are collision candidates, so owners should either rename them or claim them into a namespace.

## Next

1. Owners set `status` for their waves; the generator never infers status.
2. Add a lineage edge source (cryoplant `triage/w373/discovery/waves.yaml` has `parent_wave` fields) for public repos.
3. Run this on a schedule from pipeline-automation-hub and publish the register through the bot-PR path.
