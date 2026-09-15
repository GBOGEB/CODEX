# Anchor coverage penetration findings

Source snapshot: GBOGEB/CODEX@45f609f77f6f9990f643390635f60e5b957c652b

## Evidence boundaries

W104 counts were path heuristics, not verified integration coverage. Schema 2 removes directory-based linkage credit, uses anchor token boundaries, fixes version-folder recognition, retains complete candidate lists, and leaves verified linkage unknown. Historical W104 receipts are preserved, not silently restated.

## Source-read findings

- triage/RUNTIME_AGENT_REGISTRY.yaml explicitly registers agents and federation runtime paths. Their absence from KEB-named paths does not prove they are lost.
- src/keb/keb_client.py implements read-only glossary, governance-rule, KPI-category and confidence-level access to KEB/governance. This is a concrete reuse candidate, not proof that all callers use it.
- Vendor and child snapshot files must remain review candidates even when under triage/. No directory-level integration exemption is justified.

## Convergence gates

1. Resolve registry declarations to existing source paths, retaining evidence provenance.
2. Trace imports, entrypoints, workflow calls and producer/consumer artifacts; distinguish declared from executable edges.
3. Compare overlapping methods, signatures, side effects and tests before selecting canonical implementations.
4. Route retained capability through KEB/DOW contracts and exercise a representative end-to-end consumer.
5. Record exact tested commit, command, result and remaining unknowns. Only then claim verified coverage.

No Git gitlinks (mode 160000) were present in the complete recursive tree at this snapshot. Embedded directories are not thereby proven independent repositories; external repository discovery and historical/deleted-branch recovery remain unperformed.

## Verification

Four focused scanner regression tests passed locally for this repository. Full repository runtime and CI were not executed. This is a scanner correction and bounded source audit, not completed semantic coverage, recovered engineering value, or DoV promotion.
