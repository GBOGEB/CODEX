# Windows Repository Census Path-Length and Permission Failure — Tooling Evidence

## Status
Execution-log evidence for discovery-tool robustness. Not source authority for engineering content.

## Provenance
- Raw source: `Pasted text(45).txt`
- Source file id: `file_000000004ce871f4930829d2bcd6dda0`
- SHA256: `b0d98be03363a5ae9ddc451b54ec0f863e369501ba7104a4a522d079f7826fa4`
- Intake route: QPS W210 -> CODEX W211

## Observed failure modes
A broad recursive Windows scan emitted repeated failures of two types:

1. **Permission denied** on protected/system/user folders.
2. **Filename/path too long** across deeply nested engineering archives, backup trees, package caches and tool state.

The evidence demonstrates that an unrestricted recursive census can silently under-count or miss candidate files even when the command itself continues.

## Implication for Scout / census tooling
A governed discovery tool should make incomplete coverage visible instead of treating a partial traversal as complete. Candidate mitigations for currentness review include:

- bounded, explicitly selected roots rather than scanning the entire user/profile tree;
- long-path-aware access where supported;
- explicit skip/error counters and retained skipped-path classes;
- separate treatment of system/cache/dependency trees;
- fail-closed or `PARTIAL_CENSUS` status when access errors exceed the accepted boundary;
- coverage metrics that distinguish `visited`, `skipped_permission`, `skipped_path_length`, `excluded_by_policy`, and `unreadable`.

## Non-claim
This receipt does not prove that any specific target artifact is missing from the current governed census. It proves only that the historical scan strategy encountered conditions capable of making recursive discovery incomplete.

## Disposition
`ROUTE_AS_SCOUT_ROBUSTNESS_INPUT_NOT_SOURCE_AUTHORITY`

Formal engineering, compliance, negotiation, acceptance, release and runtime-GOLD credit: **0**.
