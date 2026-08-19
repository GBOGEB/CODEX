# Bridge Layer

The bridge layer defines documentation-only handoff contracts between ABACUS and adjacent systems. No bridge in this file is active automation; every runtime or API implementation requires a follow-on PR.

| Bridge | Purpose | Input contract | Output contract | Failure mode | Report emitted | Handoff target |
| --- | --- | --- | --- | --- | --- | --- |
| CODEX <-> ABACUS | Convert repository commits, reports, and artifacts into ABACUS rollup records. | Work ID, branch, scope, victory criteria, touched files, testing ledger. | Markdown report, YAML twin, commit refs, blocker/limitation split. | Missing report twin, dirty tree, schema mismatch, or forbidden runtime side effect. | Universal Work Report STANDARD for reversible work; FULL for release/secret/external-effect work. | ABACUS Report Registry and human PR reviewer. |
| GEMINI <-> ABACUS | Accept independent analysis or parallel review into ABACUS without losing provenance. | Prompt scope, source bundle, constraints, expected evidence, risk class. | Analysis summary, findings, confidence notes, report fragment. | Unsupported source, unverified claim, stale context, or inability to cite evidence. | Universal Work Report LIGHT or STANDARD depending on risk and artifacts. | ABACUS Contract Registry, then Report Registry. |
| CODESPACES_JUPYTER <-> ABACUS | Capture notebook or interactive workspace execution as governed evidence. | Notebook path, dataset manifest, environment notes, commands, expected outputs. | Executed-cell summary, generated artifacts, environment limitations, reproducibility notes. | Non-reproducible state, missing data, kernel dependency failure, or uncommitted artifact drift. | Universal Work Report STANDARD with testing ledger and runtime-only artifact list. | ABACUS Report Registry and CODEX if files need repository changes. |
| DOCX_RTM <-> ABACUS | Bridge document and requirements traceability outputs into governed PR records. | Requirement IDs, source document URI/path, extraction rules, traceability target. | RTM delta, coverage table, unresolved requirement gaps, generated document references. | Ambiguous requirement, protected document mutation, missing source, or conflicting IDs. | Universal Work Report STANDARD with RTM artifact references. | ABACUS Report Registry and DOCX_RTM owner. |
| CHATGPT <-> GITHUB_ACTIONS | Document future PR-body and work-report gate integration. | PR number, branch, report paths, lifecycle checklist, validation policy. | Gate summary, annotations, review comment draft, pass/fail status. | CI unavailable, token missing, schema validation failure, or policy conflict. | Universal Work Report FULL if enforcement is active; scaffold-only report while inactive. | Human reviewer; no auto-merge target. |

## Bridge invariants

- Every bridge must preserve `work_id`, `level`, `parent_id`, `track_type`, `risk_class`, and `merge_allowed`.
- Every bridge must emit or update a Universal Work Report before closure.
- Failures must be labeled as open blockers or environment limitations; silent skips are invalid.
- Handoffs may prepare evidence, but human-only merge gates remain untouched.
