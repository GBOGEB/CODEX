# W007 Runtime Architecture

## Overview

W007 establishes a lightweight runtime foundation for ABACUS governance and visualization. The runtime is intentionally static-first so it can operate on GitHub Pages without external services while preserving a clean path to generated dashboards in W008.

## Architecture Layers

1. **Source of Truth Layer**
   - `ssot/traceability_dashboard.yaml`
   - `ssot/governance_dashboard.yaml`
   - `ssot/runtime_metrics.yaml`

2. **Governance Control Layer**
   - `governance/artifact_promotion_policy.yaml`
   - `governance/runtime_readiness_checklist.yaml`
   - `governance/decision_log.md`

3. **Validation Layer**
   - `.github/workflows/rtm-validation.yml`
   - `.github/workflows/manifest-validation.yml`
   - `.github/workflows/release-readiness.yml`

4. **Presentation Layer**
   - `docs/index.html`
   - `docs/dashboards/executive.html`
   - `docs/dashboards/traceability.html`
   - `docs/dashboards/governance.html`

5. **Reporting Layer**
   - `docs/reports/W007_REPO_AUDIT.md`
   - `docs/reports/W007_COMPLETION_REPORT.md`

## Runtime Data Flow

```text
SSOT YAML models
  -> validation workflows
  -> static dashboard placeholders
  -> release readiness report
  -> W008 generated dashboard pipeline
```

## Design Principles

- Do not recreate existing historical artifacts.
- Add W007-specific runtime surfaces in additive paths.
- Prefer static HTML and checked-in YAML over external dependencies.
- Make missing references visible as runtime risks.
- Preserve a deterministic path for CI validation.

## Release Readiness Criteria

A W007 release candidate is ready when:

- Required SSOT dashboard models exist.
- Q3, Q4, and Q5 traceability chains are represented.
- Governance runtime controls exist.
- Dashboard pages exist and have local navigation.
- Validation workflows are present.
- Completion report identifies risks and W008 backlog.

## W008 Target Architecture

W008 should add a generator that reads SSOT YAML and writes dashboard HTML, release metrics, and manifest status tables. The generator should remain dependency-light and should fail if required references are absent.
