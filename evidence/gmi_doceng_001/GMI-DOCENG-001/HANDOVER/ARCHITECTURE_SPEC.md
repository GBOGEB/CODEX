# Architecture Specification

## Runtime topology

Operator terminal → `cli.py: PathsManager` → `cli.py: AgentOrchestra` → DMAIC phases → interactive hold points.

DMAIC phases:
1. DEFINE — scope profiling and counts.
2. MEASURE — syntactic/normative statistics.
3. ANALYZE — structured data loading and diagnostics.
4. IMPROVE — grammar editing, requirement validation, aggregated operator-approved edits.
5. CONTROL — final composition, provenance log, audit trail.

Hold points:
1. Scope confirmation.
2. Schema validation.
3. Diagnostic findings acknowledgment.
4. Aggregated edits batch approval.
5. Composition and disk authorization.

## Storage topology

- Active Git working tree: local POSIX/NTFS disk.
- OneDrive: timestamped snapshot mirror only.
- Microsoft Graph live synchronization: deferred.
- Alexandria: external corporate-governed repository behind VPN; integration interface remains undeclared/unverified.
