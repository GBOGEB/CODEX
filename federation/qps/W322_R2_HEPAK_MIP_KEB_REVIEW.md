# FEDERATION GOVERNANCE HEADER

## PR CLASSIFICATION
- WAVE: W322-R2
- DOMAIN: QPS_HEPAK_LINEB_SOURCE_RECEIPT_GOVERNANCE
- TYPE: SEMANTIC_PROVENANCE_REVIEW
- CRITICALITY: HIGH
- TOPOLOGY IMPACT: NO
- SCHEMA MUTATION: NO
- AUTHORITY TRANSFER: NO

## Exact child payload
- repository: GBOGEB/cryoplant-project
- PR: #1616
- exact head: dad08cdbb002843cc0cccceafc43cda10feb1eca
- predecessor child: #1608 / merge 6109292a29b25bdf8a8e1ed70968b2dda753ded6
- child authority: retained

## KEB challenge
Review only the residual BT1-BT4 hardening added after the original #1608 review:

1. **BT1 current geometry**
   - top-level source locator and revision must be substantive;
   - segment population must be non-empty, source-usable and free of duplicate segment IDs;
   - current geometry shall not be inferred from historic DN150 lineage.

2. **BT2 per-QCELL B-flow**
   - required source/provenance and numeric cells must be nonblank;
   - governed populations must cover 2K_OP and 2K_SB for config24 and config30;
   - duplicate per-QCELL identities and invalid numeric fields fail closed.

3. **BT3 thermal/property field**
   - source/provenance and governed numeric property cells must be substantive;
   - provider must be HEPAK for the low-T property row;
   - duplicate segment identities fail closed.

4. **BT4 applicant S-line recovery/PSV**
   - applicant, pressure hierarchy, source-locator and PSV structures must be substantive;
   - PSV source/tag/set/reseat/basis/destination must be bound;
   - set pressure must not be replaced by the 1.30 bara operating interface;
   - historic 3x120 m3 remains audit-only.

5. Control instrumentation and parent review create zero engineering/compliance/negotiation/runtime-GOLD credit.

Expected return: ACCEPT_REVIEW_CONTRACT | FINDING_P1/P2 | REJECT_SEMANTIC_DRIFT

formal_credit_delta = 0
