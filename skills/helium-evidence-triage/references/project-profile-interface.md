# Project profile interface

A project profile supplies project-specific values, locators, governance, UI labels and propagation targets. Generic provider lineage, receipt/hash, PRE->3-pulse->POST, reverse-pressure, PCA, sensitivity, Monte Carlo and BT remain in the core.

Required groups:
- identity/governance: project/system, child authority, dispositions, closure metrics, source precedence;
- property authority: provider policy, controlled versions, reference roles, datum alignment;
- engineering states/paths: named states, T/P/mass-flow, phase/quality, process nodes/edges, pressure basis;
- hydraulics: downstream target, local ceiling, geometry hierarchy, user positions/flow accumulation, T(x)/h(x) sources;
- evidence: contract/RTM/ICD locators, evidence classes, blockers, accepted receipts;
- human views: Excel sheets, HTML navigation/cards/drilldowns/status labels/diagnostics boundary;
- propagation: Zod/schema, Excel/HTML, graph/cards/ICDs, federation and analysis/release consumers.

Composition: `PROJECT PROFILE -> helium-evidence-triage core -> project governance -> project views`.
