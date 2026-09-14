# QPS Visual Knowledge System v1.6 — Restart Pointer

`SOURCE_DOV_COMPLETE_D21_D22_ANCHORS_BOUND_BD005_OPEN_CONTROLS_PARTIAL` · first red `V16-BD-005_LOOP_DEGRADED_BOUNDARY_AND_TRANSIENT_INPUTS` · `GLOBAL_PROJECT_DOV = WITHHELD`

Read in order:
1. `triage_v1_6.yaml`
2. `state_reconciliation_v1_6.yaml`
3. `source_proof_receipt.json`
4. `source_render_manifest.yaml`
5. `source_text_manifest.yaml`
6. `source_vs_curated_dov_v1_6.yaml`
7. `source_lineage.yaml`
8. `engineering_reconciliation_v1_6.yaml`
9. `loop_evidence_v1_6.yaml`
10. `loop_pressure_loading_v1_6.yaml`
11. `loop_hvac_boundary_v1_6.yaml`
12. `loop_contract_boundary_v1_6.yaml`
13. `control_signal_classification_v1_6.yaml`
14. `utilities_dense.md`
15. `controls_dense.md`

## Current evidence state

- BD-001 source identity: CLOSED — exact bytes and SHA256 bound for all four source PPTX objects.
- BD-002 source renders: CLOSED — all 63 bound source slides rendered and hashed.
- Native source text: CLOSED — native PPTX text bound for all 63 source slides.
- BD-003 content-trace DoV: CLOSED — 63/63 source slides explicitly dispositioned; `silent_drop_count = 0`.
- BD-004 utility semantic scope: CLOSED_SCOPE_RECONCILED — no facility sizing/acceptance credit implied.
- BD-005 LOOP evidence: OPEN_PRESSURE_BOUND — scenario/value provenance is strong, but degraded ES02/PAB12/HV03 boundary conditions and the transient proof remain open.
- BD-006 Controls: PARTIAL_EVIDENCE_BOUND — tender classifications exist; detailed cause/effect, fail-safe behavior and L2 I/O remain open.

`source_proof_execution_v1_6.yaml`, `utilities_reconciliation_v1_6.yaml` and `control_signal_classification_v1_6.yaml` remain useful child/history artifacts. Their stale top-level state is reconciled by `state_reconciliation_v1_6.yaml`; later merge timestamp alone does not reopen stronger retained execution receipts.

## D2.1 / D2.2 anchor policy

**Temporal age and provenance authority are separate dimensions.**

- **D2.1 Preliminary Design — SCK CEN/81777062** remains a specific preliminary-design evidence/provenance anchor.
- **D2.2 Technical Specification for MINERVA Cryogenic System — DSBT-TN-2024-19 Rev 4.0** remains a specific technical-specification evidence/provenance anchor.
- Both may be temporarily aged and therefore require current-revision/change checks before being used as the final current design point.
- “Aged” does **not** mean deprecated, withdrawn, invalid, or erased.
- Later interface lists, addenda, bidder evidence and analytical SSOTs may show design evolution or refinement; conflicts become explicit reconciliation edges and preserve the originating D2.1/D2.2 lineage.
- Only an explicit governed revision, withdrawal or approved change should mark an anchor requirement/value as superseded.

The Addendum applicable-documents basis itself anticipates this pattern: information is supplied at the maturity needed for the offer and updated versions may be provided during Contract execution.

## Active first red — BD-005

Keep the two LOOP evidence lanes separate:

- **WCS / compressor-room LOOP:** one-HP emergency operation, ES02, PAB12, HV03, heat paths, room/equipment thermal inventory, `~2 h` onset and `~6 h` stabilization.
- **D2.1 / Line-S cryogenic return:** helium return/release, pressure accumulation and recovery path. This remains authoritative evidence for that lane, but does not close the WCS-room thermal transient by analogy.

Next evidence sequence:

`current revision/change lineage` → `exact one-HP electrical point + auxiliaries` → `emergency PAB12 hydraulics` → `HV03 LOOP airflow/ducting` → `effective room/equipment thermal mass` → `define ~2 h variable/limit` → `define ~6 h stabilization criterion` → `first-law transient + independent review`.

Do not build another exporter. Reuse the merged generic publication carrier. ODP and Microsoft Office host reflow remain separate proof boundaries. No visual/document/publication result grants engineering, functional-safety or acceptance credit.
