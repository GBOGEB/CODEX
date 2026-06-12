# P&ID PDF reference masters

PDF master documents are intentionally not committed because this repository's PR tooling does not support binary diffs.

Reference filenames removed from this PR:

- `3_3_6_qplant_control_system_master.pdf`
- `VCR_Summary_master.pdf`

Keep the source PDFs in the external project document store/shared drive and copy them into `data/pdf/` only for local review when needed. The semantic extraction pipeline uses local SVG assets as the primary extraction inputs and does not require these PDFs to generate the current models.
