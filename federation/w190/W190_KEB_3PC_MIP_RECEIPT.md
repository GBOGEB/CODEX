# W190 KEB Receipt: Full 3PC + MIP Handover

CODEX/KEB binds the W190 handover chain.

## Consumed Records

| Lane | PR | Exact Head |
| --- | --- | --- |
| Child | [cryoplant #1178](https://github.com/GBOGEB/cryoplant-project/pull/1178) | `bc93ce38e3266099470e49904749c5bd2d31d64d` |
| DOW | [ABACUS #1213](https://github.com/GBOGEB/ABACUS/pull/1213) | `857152cca43a1ac10a68f5db3e81153f70830a15` |

## 3PC Receipt

| Phase | KEB State |
| --- | --- |
| PREPARE | PASS_EXACT_HEAD_CHAIN_IDENTIFIED |
| PROVE | PARTIAL_HANDOVER_CHAIN_PRESENT_OPEN_BLOCKERS_REMAIN |
| COMMIT | DEFER_GLOBAL_DOV_WITH_RECEIPT_CHAIN_OPEN |

## MIP Receipt

- Modernize: durable exact-head receipt records.
- Innovate: handover becomes a governed cross-repo payload.
- Perpetuate: exact-SHA, ACCEPT/REJECT/DEFER and fresh-checkout repeat gates remain mandatory.

## Disposition

- W190 handover chain: **ACCEPT**
- Global engineering/release DoV: **DEFER**

This receipt carries no engineering/compliance/negotiation/release credit by itself.
