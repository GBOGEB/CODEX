# QPLANT 3.3.6 binary source pointer

Control: GOV-001 / W005 cleanup
Date: 2026-08-28

This note records the replacement/preservation basis for removing three legacy root-level binaries from the current CODEX tree by a normal forward commit.

## Removed current-tree artifacts

- `3_3_6_preview-01.png`
- `3_3_6_qplant_control_system_master.docx`
- `3_3_6_qplant_control_system_master.pdf`

## Canonical source / preservation surfaces

- Text-source chapter: `book_md/3_3_6_qplant_control_system.md`.
- PDF reference policy: `data/pdf/README.md` states that PDF master documents are intentionally not committed and specifically lists `3_3_6_qplant_control_system_master.pdf` as an external project document-store/shared-drive reference.
- Rendered preview and Office/PDF master are treated as generated or external review artifacts under the current source-only policy; they are not canonical Git source.

## History and preservation rule

This cleanup removes the files from the **current tree only**. It does not rewrite Git history. The historical blobs remain addressable through prior commits while the current authoritative working/release copies belong in the controlled external document/release store.

No other historical DOCX/PDF/ZIP assets are removed by this cleanup because their individual source/evidence role has not yet been classified strongly enough for automatic deletion.
