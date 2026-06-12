# Governance Runtime Export

- Schema version: `0.1`
- Runtime ID: `5fa3613f-ec83-5da1-86b0-409bdda0b8bb`

## Export Registry

| Format | Status |
| --- | --- |
| json | implemented |
| yaml | implemented |
| markdown | implemented |
| excel | placeholder |
| html | placeholder |

## Validation Reports

| Key | Status | Error Count | Report |
| --- | --- | ---: | --- |
| dependency_trace | pass | 0 | `generated/trace_matrix.json` |
| lineage | pass | 0 | `generated/lineage.json` |
| master_input | pass | 0 | `generated/master_input_validation.json` |
| ssot | pass | 0 | `generated/validation_report.json` |

## Dependency Trace Model

Requirement → Applicant Response → Review → Change Request → Approval → Generated Artifact

- Nodes: `6`
- Links: `5`
- Status: `pass`

## Lineage Trace Model

ITT → Applicant Package → Review → Revision → Approval → Baseline

- Nodes: `6`
- Links: `5`
- Status: `pass`
