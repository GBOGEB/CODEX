# Governance Dashboard Specification

## Purpose

The governance dashboard summarizes runtime controls, review-gate status, release readiness, and artifact promotion state for the ABACUS repository.

## Scope

The W007 dashboard focuses on governance signals needed for runtime release decisions:

- Governance artifact inventory.
- Review gate completeness.
- Release status.
- Artifact promotion state.
- Workflow validation status placeholders.
- Open governance risks and decisions.

## Data Contract

Primary conceptual source: `ssot/governance_dashboard.yaml`.

Required top-level fields:

- `dashboard.id`
- `dashboard.version`
- `artifact_counts`
- `review_status`
- `release_status`
- `controls[]`
- `promotion_summary`
- `open_risks[]`

## Metrics

- Governance file count.
- SSOT model count.
- Review artifact count.
- Workflow count.
- Review gate completion percentage.
- Release readiness percentage.
- Open decision count.
- Open risk count.

## User Experience Requirements

- Provide an executive summary strip with review and release status.
- Provide cards for promotion policy, runtime readiness checklist, decision log, and workflow gates.
- Use responsive static HTML with no external dependencies.
- Use placeholder metrics in W007 and mark them as SSOT-backed placeholders.

## Validation Requirements

The `release-readiness.yml` workflow shall verify that governance runtime controls exist before release-candidate completion. The `manifest-validation.yml` workflow shall verify that dashboard SSOT models and required dashboard pages exist.

## W008 Enhancements

- Connect workflow status badges from GitHub Actions.
- Generate counts from repository scans.
- Add signed approval fields for release governance.
