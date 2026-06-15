# Universal Work Report Schema SSOT

The Universal Work Report is the canonical evidence container for ABACUS work units. It supports human review, machine rollup, federation handoffs, and bridge integration without requiring production runtime execution.

## Required identity header

```yaml
schema_name: universal_work_report
schema_version: 1.0.0
work_id: PR-563
agent: CODEX
level: WAVE
parent_id: null
track_type: PAR
risk_class: REVERSIBLE
review_status: REVIEW-FIRST
merge_allowed: false
```

## Canonical sections

0. Identity and mapping
1. Intent
2. Goal
3. Action taken / commit refs
4. Victory checklist delta
5. Track status [SEQ]/[PAR]
6. FF / FB loops
7. Milestone vs hold-point
8. Blockers and environment limitations
9. Testing ledger
10. Artifacts / files touched
11. Audit / data available

## Required fields

| Field | Purpose | Required |
| --- | --- | --- |
| `schema_name` | Must be `universal_work_report`. | Yes |
| `schema_version` | Schema version, starting at `1.0.0`. | Yes |
| `work_id` | Durable unit identifier. | Yes |
| `agent` | Producing agent or system. | Yes |
| `level` | ABACUS hierarchy level. | Yes |
| `parent_id` | Parent unit or `null`. | Yes |
| `track_type` | `SEQ` or `PAR`. | Yes |
| `risk_class` | `REVERSIBLE`, `IRREVERSIBLE`, `SECRET-SENSITIVE`, or `EXTERNAL-EFFECT`. | Yes |
| `review_status` | Review mode such as `REVIEW-FIRST`. | Yes |
| `merge_allowed` | Boolean gate. | Yes |
| `victory` | Criteria, status, and evidence. | Yes |
| `testing_ledger` | Checks with status and evidence. | Yes |
| `artifacts` | Runtime-only, committed, and persistent-verified artifacts. | Yes |
| `audit` | Data availability, tree identity, and merge gate. | Yes |

## Canonical enums

- `level`: `PROGRAMME`, `WAVE`, `SUB-WAVE`, `PHASE`, `SPRINT`, `TASK`, `SUBTASK`
- `track_type`: `SEQ`, `PAR`
- `risk_class`: `REVERSIBLE`, `IRREVERSIBLE`, `SECRET-SENSITIVE`, `EXTERNAL-EFFECT`
- `status`: `PASS`, `FAIL`, `PARTIAL`, `N/A`
- `test_status`: `PASS`, `FAIL`, `ENVIRONMENT-LIMITATION`
- `patch_type`: `FEATURE`, `FIX`, `HARDENING`, `VALIDATION`, `NO-OP`

## LIGHT / STANDARD / FULL application rules

| Mode | Use when | Required content |
| --- | --- | --- |
| LIGHT | Small reversible documentation-only or planning updates. | Required identity header, sections 0-4, blockers/limitations, testing ledger, artifacts. |
| STANDARD | Normal CODEX batch commits and review-first PRs. | All sections 0-11, victory tally, FF/FB loop, committed artifacts, audit data. |
| FULL | Secret-sensitive, irreversible, external-effect, release, or cross-agent federation work. | STANDARD plus hold-point records, bridge contracts, dependency graph, durable tree identity, and human GO checklist. |

## Machine-readable twin

Every Markdown report should have a YAML or JSON twin containing at least sections 0, 4, and 11 for rollup. The twin must not include secrets and must preserve blocker vs environment-limitation separation.
