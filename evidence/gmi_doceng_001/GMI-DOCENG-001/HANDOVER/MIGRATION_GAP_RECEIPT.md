# Migration Gap Receipt — W274 Federated Source Proof Closed

Session: `GMI-DOCENG-20260917-001`

## Closed

- W274 CODEX #761 merged as `ea17b87311db4bf283d08f9e86124de47961b37a`.
- W274 ABACUS #1262 merged as `f55876e4d7985dd672304ff6e3945f24de9b9194`; receiver credit remains 0.
- Provider DOCX_RTM_Automation #59 merged as `db8bf4902459d710702dd5debb725eee406a6224`.
- QPS child authority #1445 merged at exact head `995829739edf0b7aa911bfa833c6254df19e2c36` as `34f04bf08dc2f957f196f33ea1d73ae1a5b07070`.
- Provider run `35272686738` / job `105375638322` independently verified the tracked Master DOCX: 5,063,178 bytes, Git blob `d95e6a15e28e0bf9e810e434b79b62e396511aaf`, SHA-256 `ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9`.
- Native canonical extraction and verification PASSed. `master_requirements_v1.json` contains 2,692 records with SHA-256 `5bed44a7ae2c0bcbd875e1162cdde292a7d9c8dc717e7328cf4a6d6f0cc13051`.
- QPS child disposition is now `source_bytes: ACCEPT` and `canonical_extraction: ACCEPT_UNLATCHED`.
- Exact-head QPS `verify-ssot` and federation-smoke failures on the merge candidate remained `steps: []`, `runner_id: 0`, so no semantic mutation was made from infrastructure/pre-execution evidence.

## Durable Drive proof

- Pointer contract: `1Ad4T-fv5nX8PAxPxIpNQ3b3VMls-MuVs`.
- Provider receipt: `1C88w2KpF0v0o3D5REYWn8-jbGbuUFSFv`.
- Extraction manifest: `1PCxrxgSGSDZnwkqVh-Qq_ON6A9029s-Z`.
- Unlocked canonical master requirements: `1kbtgTEX25l18HSYcmBZ2ax88WVI3O2Ok`.

## Still open / non-compensating

- Canonical lock/tag/release has **not** been performed.
- The first post-source Schrijfeditor/document-core execution is still pending.
- RAW conversation exports and the real `normal.dotm` remain unavailable.
- Replay/round-trip equivalence, Alexandria Graph runtime, and global CONTROL remain withheld.
- GT_BDQ is unchanged.

## Next governed gate

W274 is closed as a fully merged source-proof federation slice. The successor should either (a) execute an explicit canonical lock/tag mutation with its own receipt, or (b) keep lock deferred and consume the verified canonical requirements through the document-core adapter for the first post-source Schrijfeditor execution. Neither route may silently promote global CONTROL.
