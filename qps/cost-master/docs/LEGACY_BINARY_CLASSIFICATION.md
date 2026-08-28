# QPS COST_Master legacy binary classification

Control: GOV-001 / W005
Status: source-side hardening audit
Date: 2026-08-28

## Purpose

This document separates the QPS COST_Master source-only policy from the wider historical binary estate already present in CODEX. It is a classification record, not a history rewrite and not permission to delete unreviewed assets.

## Policy boundary

The controlled QPS paths remain text-source only:

- `07_ops/qps_roundtrip/`
- `qps/cost-master/`

New QPS release binaries are not committed to GitHub. They are built in the local workspace, published as immutable OneDrive releases, and represented publicly only by sanitized release pointers and hashes.

## Confirmed root-level binary candidates

| Path | Size bytes | Classification | Decision basis | Next action |
|---|---:|---|---|---|
| `3_3_6_preview-01.png` | 256810 | REGENERATE_OR_MIGRATE | Root-level rendered preview; `book_md/3_3_6_qplant_control_system.md` is the text source surface and the W007 repository audit records this PNG as a standalone root artifact. | Remove from current source tree in a dedicated cleanup PR after recording its source replacement. Do not rewrite history. |
| `3_3_6_qplant_control_system_master.docx` | 2266361 | MIGRATE_EXTERNAL_REFERENCE | Generated/editable Office master is incompatible with the new QPS source-only release boundary. Text-source chapter exists in `book_md/3_3_6_qplant_control_system.md`. | Move the authoritative working/release copy to the external project document store/OneDrive; remove current-tree copy in dedicated cleanup PR after preservation is confirmed. |
| `3_3_6_qplant_control_system_master.pdf` | 114739 | MIGRATE_EXTERNAL_REFERENCE | `data/pdf/README.md` explicitly states PDF reference masters are intentionally not committed and names this file as an external-store reference. | Remove current-tree copy in dedicated cleanup PR. External reference remains in the controlled project document store. |

These three files total 2,637,910 bytes in the current repository root.

## Wider legacy binary estate

The W007 repository audit also records historical/reference binaries such as:

- `Addendum_book_master.docx`;
- `Full_VCR_Handover*.docx`;
- `VCR_*.docx` and `VCR_*.pdf`;
- `Input/Addendum II - Cryoplant Technical Requirements_*.docx`;
- `Input/cryoplant_deck_handover_R1C2.zip`.

These files pre-date the QPS COST_Master source-only roundtrip and can serve as historical inputs, reference masters, regression fixtures, or generated outputs. They are therefore **not** blanket-deleted by the QPS hardening programme.

Default classification for these older assets is:

`REVIEW_KEEP_OR_MIGRATE`

until all of the following are known:

1. whether the file is source evidence, a generated output, or a regression fixture;
2. whether a canonical text/source representation exists;
3. where the preserved external copy resides;
4. whether tests or documentation still reference the tracked path;
5. whether removal from the current tree changes reproducibility or historical review capability.

## ABACUS boundary

ABACUS is audited separately because it contains many rendered examples, engineering outputs and fixtures across non-QPS subsystems. The QPS hardening programme does not apply a repository-wide binary purge to ABACUS.

The enforceable QPS rule is narrower and stronger: no QPS COST_Master confidential evidence or generated XLSX/DOCX/PPTX/PDF/image/archive output may be added under the controlled QPS source paths.

## Classification vocabulary

- `KEEP`: intentionally version-controlled source/reference fixture with documented purpose.
- `MIGRATE_EXTERNAL_REFERENCE`: preserve in controlled external storage; remove current-tree copy after the preservation pointer exists.
- `REGENERATE_OR_MIGRATE`: generated/rendered content whose source is version controlled or whose authoritative copy belongs outside Git.
- `REVIEW_KEEP_OR_MIGRATE`: insufficient provenance for automatic removal.
- `POLICY_VIOLATION`: binary appears inside a controlled text-only QPS path; blocks merge immediately.

## Cleanup rule

Binary cleanup is performed by normal forward commits only. No Git history rewrite is authorized by this programme.

A deletion PR must state the replacement source or external preservation location and must pass all repository CI before merge.
