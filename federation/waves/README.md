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
- **The current-wave declarations agree on `QPS:W113`.** CODEX declares it in `GLOB.yaml` (`wave: W113`), and ABACUS in `.mesh/MESH_DOCK.yaml#current_focus`. Correction to the seed note: CODEX `handover/CURRENT.json` (`Wave-0`) is not a stale pointer. `scripts/validate_all.py` pins it as the open Wave-0 bootstrap HOLD record, so the register gives it the role `bootstrap_record` and leaves it out of `current_wave_consensus`. The residual risk is only for agents that follow `AGENT_ENTRYPOINT -> handover/CURRENT.json` as a current-wave pointer; that is an owner decision and is out of scope here.
- **Single-digit ids outside a namespace context are tagged `QPS` with `confidence: inferred`.** These are QPS:W000..W009. They are collision candidates, so owners should either rename them or claim them into a namespace.

## Naming, claims and de-duplication (rules: `WAVE_NAMING_RULES.yaml`, must obey)

**Prerogative.** Each repo declares the waves it *owns* in its own `.waves/WAVE_CLAIMS.yaml`: canonical name, status, aliases, and `paths` (the worktree, workflow and generated-asset boundaries it owns). It also declares the waves it only *participates* in, with a role. Nobody else sets those fields.

**Roll-up.** `scripts/build_wave_register.py` reads every member's claims file at the exact source commit. `scripts/wave_claims.py` merges those claims with the observed census and writes the result into `WAVE_REGISTER.yaml`: each wave's `claim` plus the `dedup` census and violations. `--strict` exits 2 when there are errors.

| Rule | Code |
|---|---|
| One number has exactly one owner | `D1_DUP_OWNER`. The key is published as `CONTESTED`, with all claimants. |
| One canonical name maps to one key, forever: `W<nnn>_<SLUG>`, and the number must match the key | `C2`, `C3`, `D2_NAME_REUSE` |
| Aliases are free but must obey the rule: lower-case kebab, at most 40 chars, at most 5 per wave, no other wave's number, never equal to any canonical name | `C6`, `C7`, `D3_ALIAS_CLASH` |
| The number can increment: a successor takes a new number and may carry the slug forward only if it declares the earlier wave as `parent` (or lineage shows it) | `D4_SLUG_NO_LINEAGE` |
| New numbers are `next_free`; an unobserved hole below the maximum is never backfilled | `N1_BACKFILL` |
| Path boundaries inside a repo never overlap, unless the inner wave declares the outer one as parent | `D5_PATH_OVERLAP` |
| A repo that touches another repo's wave declares a role (overlapping worktrees) | `O1_UNDECLARED_PARTICIPANT` (warning) |
| Status is owner-set (`ACTIVE`, `HOLD`, `CLOSED`, `SUPERSEDED`); `OBSERVED` is the generator default | `C5_STATUS` |
| Private repos are validated in full, but publish only sha256 digests of names and aliases | redacted in messages |

**Owner workflow.**

1. Draft from your own records: `python scripts/wave_claims.py propose --repo GBOGEB/<NAME> --repo-path <checkout>`. The proposer only drafts rule-clean claims. It lists the rest under `needs_name` (no unique slug in your records) and `contested_ties` (another repo holds equal evidence).
2. Edit the draft and commit it as `.waves/WAVE_CLAIMS.yaml`.
3. Check it: `python scripts/wave_claims.py validate`.

## Next

1. ~~Owners set `status`~~: done via `.waves/WAVE_CLAIMS.yaml` (see above). CODEX has seeded its own claims; the other members add theirs.
2. ~~Add a lineage edge source~~: done. `lineage` indexes `parent_wave` / `parent_waves` fields as `child <- parent` id pairs. Private repos contribute only id pairs and counts. A Kahn sort over the edges reports `acyclic`, `roots` and `longest_chain`. Records whose own id is outside every namespace (e.g. `W25C.4`) are counted per source as `lineage_unresolved`, never guessed.
3. Run this on a schedule from pipeline-automation-hub and publish the register through the bot-PR path.
