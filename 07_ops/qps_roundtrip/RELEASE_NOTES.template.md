# QPS Cost Estimate Release Notes

Release ID: `<version>_<short-commit>_<build-id>`  
Control ID: `GOV-001`  
Generated UTC: `<timestamp>`

## Source state

- ABACUS commit: `<sha>`
- CODEX commit: `<sha>`
- Private overlay commit: `<sha>`
- Evidence registry hash: `<sha256>`
- Source-tree semantic hash: `<sha256>`

## Evidence state

List each required evidence ID, expected filename, verified SHA-256, size and classification. Do not embed confidential evidence content here.

## Main model changes

- `<change>`

## QA gates

- [ ] Evidence hash verification
- [ ] SSOT/schema validation
- [ ] Workbook formula validation
- [ ] Workbook visual/render validation
- [ ] DOCX render validation
- [ ] PPTX render validation
- [ ] PDF render validation
- [ ] HTML asset/navigation validation
- [ ] Semantic manifest generated
- [ ] Exact artifact manifest generated
- [ ] Clean verification-clone comparison

## Published artifacts

List artifact filename, semantic hash where applicable, exact artifact SHA-256 and size.

## Known limitations / open actions

- `<item>`

## Office review

Immutable release folder: `<path or release ID>`  
Working review copy: `<path or review ID>`

Office edits must be registered in the private overlay review-change register and assimilated into source before a new release is produced.
