# W190 KEB Receipt: Full 3PC + MIP Handover

CODEX/KEB binds the repaired final W190 handover chain and the DOW execution-repair receipt.

## Consumed Records

| Lane | PR | Active exact identity |
| --- | --- | --- |
| Child | `GBOGEB/cryoplant-project#1178` | final head `c283eb1f7d19eaa22b31a888a51c798c36107df5`; merge `460979c48d0c15814ed14547116e99718c2cdcd1` |
| Child execution receipt | `federation/w190/W190_3PC_MIP_EXECUTION_RECEIPT.json` | declared head `37623d581df7d91c6ad9ee4e732d3666b44c3569`; state `WITHHELD_INFRA_PREEXECUTION`; `runner_id=0`, `steps=0` |
| DOW original | `GBOGEB/ABACUS#1213` | superseded consumer of interim child head |
| DOW lineage repair | `GBOGEB/ABACUS#1215` | head `b8e4b801d37ac9ee6e8958ba1b32579e50e1c29e`; merge `5cf2c0274da72b9f97a5dd68c065cf1595cd2ea1` |
| DOW execution repair | `GBOGEB/ABACUS#1216` | head `3abe48e318843c972c0e1e480ffb6c44889e10be`; merge `158093da5234805f8bb3348b0de0c2ff0bfe60fd` |

Superseded historical identities remain recorded rather than rewritten:
- child interim head `bc93ce38e3266099470e49904749c5bd2d31d64d`;
- DOW interim head `857152cca43a1ac10a68f5db3e81153f70830a15`.

## 3PC Receipt

| Phase | KEB State |
| --- | --- |
| PREPARE | PASS_FINAL_EXACT_LINEAGE_AND_EXECUTION_RECEIPT_IDENTIFIED |
| PROVE | PASS_HANDOVER_LINEAGE_CHAIN_BOUND_WITH_INFRA_PREEXECUTION_PROOF |
| COMMIT | ACCEPT_HANDOVER_CHAIN_DEFER_GLOBAL_DOV |

## MIP Receipt

- **Modernize:** repair stale interim-head lineage and schema mismatch while preserving historical evidence.
- **Innovate:** represent correction by explicit supersession edges and DOW execution-repair consumption instead of rewriting prior receipts.
- **Perpetuate:** the handover chain is durable at final merge identities; runtime/release perpetuation remains gated by native child execution, exact-SHA receipt, `runner_id != 0`, `steps > 0`, and repeat.

## Disposition

- W190 final handover lineage chain and receipt visibility: **ACCEPT**
- Invalid schema/receipt mismatch or contradictory payload: **REJECT** when observed
- Global engineering/release DoV and runtime promotion: **DEFER**
- Engineering/compliance/negotiation/release credit delta: **0**

Canonical restart text remains in `cryoplant-project:handover/qps_recursive/W190_3PC_MIP_DROPIN.md`.
