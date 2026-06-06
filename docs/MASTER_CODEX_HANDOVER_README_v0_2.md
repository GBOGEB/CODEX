# MASTER Contract Governance Workbench Handover v0.2

This handover initializes the GitHub-ready bootstrap for the MASTER Contract
Governance Workbench in `GBOGEB/CODEX`.

## Ownership model

ABACUS owns contract data. CODEX owns automation. ARTSTYLE owns visualization.

## Tender lifecycle context

- Selection complete
- Applicant notification complete
- ITT issued
- Clarification period active
- Applicant offers expected July 2026
- Negotiation Round 1
- Negotiation Round 2
- BAFO
- Award recommendation
- Contract award
- PO target 01-Jan-2027
- Execution: 34 calendar months, 6 phases

## Governance rules

1. `MASTER_input/00_ITT_RELEASE_BASELINE/` is locked baseline material.
2. Do not overwrite released ITT documents.
3. All updates must be additive.
4. YAML SSOT is authoritative.
5. Excel, HTML, dashboards and reports are generated outputs only.
6. Any Excel or HTML edits must become change requests back into SSOT.
7. Preserve lineage from source document → requirement → clarification → applicant response → evaluation → negotiation → BAFO → award → execution deliverable.

## Bootstrap locations

- Locked baseline input: `MASTER_input/00_ITT_RELEASE_BASELINE/`
- Additive input workstream: `MASTER_input/01_CONTRACT/` through `MASTER_input/11_EXECUTION/`
- Archive: `MASTER_input/99_ARCHIVE/`
- Authoritative SSOT: `ssot/master_contract_ssot_v0_2.yaml`
- SSOT schema: `schemas/master_contract_ssot.schema.yaml`
- Generated outputs: `generated/`
- Automation stubs: `generators/`
- Delivery roadmap: `roadmap/`
