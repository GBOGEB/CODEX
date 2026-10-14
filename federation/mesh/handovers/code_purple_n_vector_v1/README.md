# CODE PURPLE / EVERRED — GitHub-native evolutionary handover

**Entry point / handover SSOT:** this Git tree, not a ZIP attachment. **Status:** documentation and offline mathematical reference, not merged authority or an authenticated live runner.

## Resume from a fresh checkout

1. Read [HANDOVER.md](HANDOVER.md), [STATE.json](STATE.json), [MODEL.md](MODEL.md), and [DROPIN.md](DROPIN.md).
2. Refresh both repositories' `main` SHAs and the heads, reviews, workflows, artifacts and effective rules for each owner PR **before editing**. An historical observation remains historical; it does not become a live result.
3. Reconcile existing owner branches before any new repair PR. CODEX #1037 owns recovery control; ABACUS #1929 owns the BD/LDAB evidence contract; ABACUS #1860 owns admission HOLD. Merged CODEX #1041 and ABACUS #1962 remain historical implementation owners, not pretexts to duplicate their changes.
4. Run `cd federation/mesh/handovers/code_purple_n_vector_v1 && python -m unittest -v test_temporal_matrix.py` for **local/offline reference proof only**.
5. Record every new material observation with repository, full 40-character SHA, UTC timestamp, run/attempt/job, producer/config/scope/denominator, existing causal root and owner, terminal result, and disposition.
6. Append a new source-bound revision observation and *separate logical recovery-cycle entry*; never rewrite historical receipts. Update issue [CODEX #1037](https://github.com/GBOGEB/CODEX/issues/1037) and [ABACUS #1929](https://github.com/GBOGEB/ABACUS/issues/1929) after verification.

## File contract

- `HANDOVER.md`: human-run restart and source/evidence crosswalk.
- `STATE.json`: frozen machine-readable checkpoint, units and unknowns. Do not treat as live.
- `MODEL.md`: revision vs logical-cycle, reindexing and masked difference equations.
- `temporal_matrix.py` / `test_temporal_matrix.py`: stdlib-only **reference** library/tests; no GitHub API mutations or merge functions.
- `DROPIN.md`: copyable continuation instruction referring to this Git path rather than a ZIP.
- `MANIFEST.json`: file list, evidence lineage and migration integrity warnings.
- `VALIDATION.md`: exact acceptance ladders and intentionally missing proof.

## Governance invariants

**UNKNOWN is not zero; historical PASS is not current-head PASS; a successful worker is not an independent reviewer; a merge is not proof of governed admission.** No bypass, waiver, aut-merge, remote mutation or authenticated debugger-session claim is conferred by this handover. Read-only source federation does not transfer authority.

## Migration note

The source `CODE_PURPLE_N_VECTOR_RECOVERY_20261014.zip` had seven files, with a stale `manifest.json` referencing an eighth `DROPIN_DELTA.md` that was **not in the recovery ZIP**. Its older WBS/model/tests also recorded an obsolete 11→2 Ruff snapshot. This Git package corrects that source inconsistency; it does not claim full migration of the older `HANDOVER_V2.zip` (29-file inventory referenced in issue comments; raw bytes not available in this session).
