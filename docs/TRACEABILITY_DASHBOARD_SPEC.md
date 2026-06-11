# Traceability Dashboard Specification

## Purpose

The traceability dashboard provides a runtime view from ALAT question themes to the reviewed answer evidence. It is a static GitHub Pages surface backed conceptually by the checked-in SSOT YAML models until a W008 generator connects live data.

## Scope

The W007 traceability dashboard shall cover the critical Q3, Q4, and Q5 chains:

- Question -> RTM reference -> Contractual gap -> Clarification -> Answer status.
- Coverage metrics for each chain.
- Missing-link indicators for review-gate escalation.
- Artifact references needed by release readiness workflows.

## Required Traceability Chains

| Question | Required path | Runtime status rule |
| --- | --- | --- |
| Q3 | Q3 -> RTM -> Contractual Gap -> Clarification -> Answer | Complete only when all four references exist and answer status is `approved` or `ready_for_review`. |
| Q4 | Q4 -> RTM -> Contractual Gap -> Clarification -> Answer | Complete only when all four references exist and answer status is `approved` or `ready_for_review`. |
| Q5 | Q5 -> RTM -> Contractual Gap -> Clarification -> Answer | Complete only when all four references exist and answer status is `approved` or `ready_for_review`. |

## Data Contract

Primary conceptual source: `ssot/traceability_dashboard.yaml`.

Required top-level fields:

- `dashboard.id`
- `dashboard.version`
- `coverage.overall_percent`
- `coverage.required_questions`
- `chains[].question_id`
- `chains[].rtm_reference`
- `chains[].contractual_gap_reference`
- `chains[].clarification_reference`
- `chains[].answer_reference`
- `chains[].status`
- `open_items[]`

## Metrics

- Overall traceability coverage percentage.
- Complete chain count.
- Partial chain count.
- Missing reference count.
- Q3/Q4/Q5 individual completion status.

## User Experience Requirements

- Show one summary panel per Q3, Q4, and Q5.
- Use plain HTML and CSS only; no external dependencies.
- Render placeholder metrics when the YAML model has not been transformed into page data.
- Clearly distinguish `complete`, `partial`, `blocked`, and `not_started` statuses.
- Keep the page usable on mobile screens with stacked cards.

## Validation Requirements

The `rtm-validation.yml` workflow shall verify that the traceability dashboard model exists and that Q3, Q4, and Q5 chain entries include RTM, contractual gap, clarification, and answer references.

## W008 Enhancements

- Generate dashboard HTML from `ssot/traceability_dashboard.yaml`.
- Link each reference to the authoritative review artifact.
- Add trend history for coverage changes per release candidate.
