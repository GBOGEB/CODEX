# ADR: USER Interface Descriptive Note as SSOT-Derivative Configuration

## Status

Proposed — derivative locked candidate pending review.

## Context

The QPS CONTRACT is the authoritative single source of truth (SSOT) for the cold and warm USER interface configuration. USER-facing consumers also need a dominant, rendered, descriptive note that consolidates the contract-derived interface hierarchy, terminal-point responsibilities, line functions, route-length basis, tap-off logic, and internal surface-area calculations.

## Decision

Create `USER_INTERFACES_COLD_WARM_NOTE.md` as a supplementary, descriptive, user-facing document derived from the QPS CONTRACT SSOT.

The note is classified as `SSOT_derivative`: it is not authoritative over the CONTRACT, but once reviewed it should be treated as fixed/locked scientific configuration unless a future approved change is traced to the CONTRACT or to an approved configuration-change decision.

Quantitative line values are stored in reusable YAML and JSON data files so future calculated artefacts can consume the same structured facts instead of scraping rendered prose or tables.

## Governance Rules

* CONTRACT remains the authoritative SSOT.
* This note is derivative and explanatory.
* Quantitative values are structured for future calculated artefacts.
* Any future change to diameters, lengths, or line functions must trace back to CONTRACT or approved configuration change.
* Rendered Markdown, HTML, and PDF export paths must remain available because user-facing governance requires reviewable rendered artefacts.

## Consequences

* The Markdown note can govern user-facing interpretation only as a derivative artefact.
* The HTML view supports immediate rendered review.
* The documented PDF path supports formal review packages and offline distribution.
* Calculation pipelines can reuse the YAML and JSON data without re-keying tabular values.
