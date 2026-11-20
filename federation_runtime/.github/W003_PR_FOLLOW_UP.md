# FEDERATION GOVERNANCE HEADER (MANDATORY BLOCK)

## PR CLASSIFICATION
- PR-ID: PR-330
- WAVE: W003
- SPRINT: S1-P1
- DOMAIN: EXECUTION_GOVERNANCE_INFRASTRUCTURE
- TYPE: GOVERNANCE
- CRITICALITY: HIGH
- TOPOLOGY IMPACT: NO
- SCHEMA MUTATION: CONTROLLED

---

# MERGE ORDER GOVERNANCE
- REQUIRED PREDECESSORS: GBOGEB/cryoplant-project#219, GBOGEB/ABACUS#795
- CURRENT TRACK: GBOGEB/CODEX#330
- BLOCKED SUCCESSOR: QPS child W08 ACCEPT/REJECT/DEFER disposition
- FOLLOW-UP UPDATE: W08 semantic/schema validator contract, exact child-owned workstream taxonomy, thresholded PR-head control stats, and candidate return-receipt semantic artifact vocabulary.

## A8.1 FOLLOW-UP — PR-682
- PURPOSE: preserve W003 governance-gate compatibility while A8.1 repairs the renderer-receipt vocabulary first-red.
- CHANGE BOUNDARY: `semantic_card` glossary governance plus exact PR-head SHA binding for ABACUS renderer receipts.
- AUTHORITY: governance/provenance only; no child engineering authority or QPS acceptance semantics are changed.
- EXPECTED PROOF: exact-head ABACUS renderer execution receipt + promotion receipt + W003 governance gate PASS before merge.

## CODE PURPLE OBSERVABILITY FOLLOW-UP — PR-995
- PR-ID: PR-995
- PURPOSE: correct deterministic executable inventory drift and observe
  exact-SHA CI check outcomes without fabricating admission or worker evidence.
- WAVE: W114
- DOMAIN: EXECUTION_GOVERNANCE_INFRASTRUCTURE
- TYPE: CI_CD
- CRITICALITY: HIGH
- TOPOLOGY IMPACT: NO
- SCHEMA MUTATION: NO
- BOUNDARY: read-only check-run telemetry, non-authoritative and unknown-safe.
- REQUIRED PROOF: exact-head W003, Mycelium and CODE PURPLE Live Observation
  terminal results; independent security review before governed merge.
- AUTHORITY: no QPS/ABACUS transfer, waiver, REX launch or formal credit.

## BINARY ENGINE FOLLOW-UP — PR-1330

- PR-ID: PR-1330
- WAVE: W003
- SPRINT: S1-P1
- DOMAIN: EXECUTION_GOVERNANCE_INFRASTRUCTURE
- TYPE: GOVERNANCE
- CRITICALITY: HIGH
- TOPOLOGY IMPACT: NO
- SCHEMA MUTATION: CONTROLLED
- PURPOSE: qualify source-bound OCR and native workbook/PPTX behavior through
  the existing binary engines, preserving source authority boundaries.
- FIRST-RED DISPOSITION: update legacy OCR tests that expected confidence-based
  authority promotion; retire the strict expected failure for repaired raster
  classification and retain an executable positive regression across formats.
- REQUIRED PROOF: current-head semantic validation, ordinary tests, security,
  and this governance header; local tests do not satisfy native CI admission.
- AUTHORITY: OCR remains derived evidence. Neither recognition confidence,
  execution receipts nor a passing test confer QPS engineering acceptance.
- CONTROLLED CONTRACT MIGRATION: native workbook features v2 normalize Boolean
  spellings with paired ABACUS parser 1.2.1; source-bound OCR region/crop/reference
  contracts remain subordinate. Historical v1 fingerprints are retained, not relabelled.
