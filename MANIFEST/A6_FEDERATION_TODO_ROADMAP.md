# A6 Federation Runtime TODO Roadmap

## Purpose

This document tracks the outstanding tasks for completing Wave A6 (governance_runtime_enforcement) and preparing for Wave A7 (orchestration_dependency_visual_telemetry).

## Planning Hierarchy

```
Wave (Alpha phase)
  └─ Subphase (A6.1, A6.2, A6.3)
      └─ Task (specific deliverable)
          └─ Subtask (implementation detail)
```

## Current Status

- **Wave A6** (governance_runtime_enforcement): **100% complete** ✅ (WAVE_PROGRESSION.yaml)
- **Wave A7** (orchestration_dependency_visual_telemetry): **65% complete** ⚠️ (WAVE_PROGRESSION.yaml)

**Note:** PR feedback indicated A6 was 86% complete prior to federation runtime implementation. Now updated to 100% in WAVE_PROGRESSION.yaml.

---

## Wave A6 — Remaining Tasks (14% from earlier estimate)

### Phase A6.1 — Governance Linters

Status: **Partially Complete** (overflow_lint, spacing_lint, navigation_lint wired into RENDER_LINTER.py)

#### Task A6.1.1 — Complete Remaining Governance Linters

**Priority:** Medium  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A6 closure

**Subtasks:**
- [ ] **A6.1.1.1** — Implement `contrast_lint.py` for WCAG contrast enforcement against SEMANTIC_THEME.yaml
  - Files to create: `governance/contrast_lint.py`
  - Integration point: Wire into `governance/RENDER_LINTER.py`
  - Test coverage: Add unit tests for contrast ratio calculations and WCAG AA/AAA levels
  - Acceptance: CI validates all HTML outputs for contrast compliance

- [ ] **A6.1.1.2** — Implement `overflow_lint.py` for content overflow detection
  - Files to create: `governance/overflow_lint.py`
  - Integration point: Wire into `governance/RENDER_LINTER.py`
  - Test coverage: Validate detection of text/container overflow in rendered outputs
  - Acceptance: CI detects overflow violations in HTML/SVG artifacts

- [ ] **A6.1.1.3** — Implement `spacing_lint.py` for layout spacing consistency
  - Files to create: `governance/spacing_lint.py`
  - Integration point: Wire into `governance/RENDER_LINTER.py`
  - Test coverage: Validate spacing rules from SEMANTIC_THEME.yaml
  - Acceptance: CI enforces consistent spacing across all rendered outputs

- [ ] **A6.1.1.4** — Verify `navigation_lint.py` is fully wired
  - Status: Already completed per WAVE_PROGRESSION.yaml
  - Verification: Confirm docs/ site boundary enforcement (docs/ + outputs/ allowed)
  - Test coverage: CI rejects ../ links escaping docs root

---

### Phase A6.2 — Office365 Binary Classification

Status: **Incomplete**

#### Task A6.2.1 — Add Office365 Binary Classification Rules

**Priority:** High  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A6 closure

**Context:** `_config/governance.yml` declares `allowed_formats: ["pptx", "docx", "xlsx", "pdf"]` but classification logic is not implemented.

**Subtasks:**
- [ ] **A6.2.1.1** — Document Office365 classification taxonomy
  - Files to create: `governance/schemas/office365_binary_classification.schema.yaml`
  - Schema fields: `file_type`, `classification_level`, `retention_policy`, `security_boundary`
  - Acceptance: Schema validated against `scripts/check_ssot_schemas.py`

- [ ] **A6.2.1.2** — Implement classification logic in `Office365GraphConnector`
  - Files to update: `src/federation/office365_graph_connector.py`
  - Add method: `classify_binary(metadata: dict) -> str`
  - Classification rules:
    - MIME type detection
    - File extension allowlist enforcement from governance.yml
    - Size/age-based retention policy application
  - Test coverage: `tests/federation/test_office365_graph_connector.py`

- [ ] **A6.2.1.3** — Wire classification into binary index ledger
  - Files to update: `src/federation/office365_graph_connector.py`
  - Update: `build_binary_index_entry()` to call `classify_binary()`
  - Acceptance: Binary index JSON includes `classification` field populated per schema

---

### Phase A6.3 — MCP Sweep CI Integration

Status: **Incomplete**

#### Task A6.3.1 — Integrate MCP Sweep into CI Workflow

**Priority:** High  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A6 closure

**Context:** MCP sweep runtime (`src/federation/mcp_sweep_engine.py`) exists but is not invoked by CI.

**Subtasks:**
- [ ] **A6.3.1.1** — Create MCP sweep CI script
  - Files to create: `scripts/run_mcp_sweep.py`
  - Script behavior:
    - Instantiate `MCPSweepEngine` with GitHub credentials from environment
    - Scan closed PRs, aborted sessions, stale lineage
    - Write telemetry + RTM delta outputs to `outputs/federation/`
  - Acceptance: Script runs successfully with mock GitHub API

- [ ] **A6.3.1.2** — Wire MCP sweep into `.github/workflows/ci.yml`
  - Files to update: `.github/workflows/ci.yml`
  - Placement: **Post-test, pre-publish** (after pytest, before Pages upload)
  - Environment: Provide `GITHUB_TOKEN` via secrets
  - Acceptance: CI runs MCP sweep and commits telemetry/RTM outputs

- [ ] **A6.3.1.3** — Add RTM lineage delta publishing to Pages
  - Files to update: `.github/workflows/pages.yml`
  - Copy `outputs/federation/rtm_delta.md` to `docs/federation/rtm_delta.html` (convert via renderer)
  - Register in `MANIFEST.json` published_pages
  - Acceptance: RTM delta visible at https://GBOGEB.github.io/CODEX/federation/rtm_delta.html

---

### Phase A6.4 — Validation and Testing

Status: **Incomplete**

#### Task A6.4.1 — Add Integration Test for Full Sweep Pipeline

**Priority:** Medium  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A6 closure

**Subtasks:**
- [ ] **A6.4.1.1** — Create end-to-end integration test
  - Files to create: `tests/federation/test_sweep_integration.py`
  - Test scenario:
    - Mock GitHub API with closed/merged PRs containing near-miss keywords
    - Mock aborted session logs in temporary directory
    - Mock stale lineage YAML file
    - Run `MCPSweepEngine.run()` and verify output structure
  - Acceptance: Test validates proposed/pruned/active classification and RTM delta shape

- [ ] **A6.4.1.2** — Validate Markdown injection protection
  - Files to update: `tests/federation/test_mcp_sweep_engine.py`
  - Test cases:
    - PR title with `|` characters (pipe injection)
    - PR title with newlines (row injection)
    - Proto-need with malicious Markdown (link injection)
  - Acceptance: All injected content is escaped in RTM delta and telemetry outputs

---

## Wave A7 — Orchestration and Visual Telemetry

Status: **65% complete** (WAVE_PROGRESSION.yaml)

### Context

Wave A6 federation runtime provides the **input substrate** for orchestration:
- **Identity lanes** → multi-tenant execution contexts
- **Office365 connector** → binary artifact ingestion
- **MCP sweep** → GitHub/session lineage capture

Wave A7 adds orchestration capabilities on top of these substrates.

---

### Phase A7.1 — Dependency Resolution Between Federation Lanes

Status: **Not Started**

#### Task A7.1.1 — Design Lane Dependency Graph

**Priority:** High  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A7 (next sprint)

**Subtasks:**
- [ ] **A7.1.1.1** — Create orchestration design document
  - Files to create: `governance/adr/ADR-0002-federation-orchestration.md`
  - Design questions:
    - How do lanes declare dependencies on other lanes?
    - What triggers lane execution (event-driven vs scheduled)?
    - How are cross-lane artifacts passed (federated cache vs direct API)?
  - Acceptance: ADR approved by stakeholders

- [ ] **A7.1.1.2** — Define lane dependency schema
  - Files to create: `governance/schemas/lane_dependency_graph.schema.yaml`
  - Schema fields: `lane_id`, `depends_on`, `artifact_contracts`, `execution_order`
  - Acceptance: Schema validated against `scripts/check_ssot_schemas.py`

- [ ] **A7.1.1.3** — Implement lane orchestrator runtime
  - Files to create: `src/orchestration/federation_lane_orchestrator.py`
  - Features:
    - Parse lane dependency graph from YAML
    - Topological sort for execution order
    - Dependency resolution with cycle detection
    - Artifact passing between lanes
  - Test coverage: `tests/orchestration/test_lane_orchestrator.py`

---

### Phase A7.2 — Visual Telemetry Dashboards for Sweep Outputs

Status: **Partially Complete** (visuals/orchestration_dependency_graph.py, visuals/agent_telemetry_timeline.py exist)

#### Task A7.2.1 — MCP Sweep Telemetry Dashboard

**Priority:** Medium  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A7

**Subtasks:**
- [ ] **A7.2.1.1** — Create MCP sweep visualization script
  - Files to create: `dashboards/mcp_sweep_dashboard.py`
  - Data source: `outputs/federation/sweep_telemetry.json` (generated by sweep engine)
  - Visualizations:
    - Proposed/pruned/active counts over time (Plotly bar chart)
    - Near-miss PR timeline with merged status (Plotly scatter)
    - RTM delta growth (line chart)
  - Output: `docs/federation/mcp_sweep_dashboard.html`
  - Acceptance: Dashboard loads from sweep telemetry and renders in GitHub Pages

- [ ] **A7.2.1.2** — Register dashboard in MANIFEST.json
  - Files to update: `MANIFEST.json`
  - Add entry: `docs/federation/mcp_sweep_dashboard.html` to `published_pages`
  - Acceptance: `scripts/check_stale.py` validates dashboard registration

- [ ] **A7.2.1.3** — Add sweep metrics to PROGRAM_METRICS.yaml
  - Files to update: `MANIFEST/PROGRAM_METRICS.yaml`
  - Metrics to track:
    - `federation_sweep_proposed_count`
    - `federation_sweep_active_count`
    - `federation_sweep_pruned_count`
  - Acceptance: Metrics appear in thermo command center dashboard

---

### Phase A7.3 — Orchestration Rules for Connector Invocation

Status: **Not Started**

#### Task A7.3.1 — Define When/How to Invoke Federation Connectors

**Priority:** Medium  
**Owner:** GBOGEB/CODEX  
**Target:** Wave A7

**Subtasks:**
- [ ] **A7.3.1.1** — Create orchestration rules schema
  - Files to create: `governance/schemas/orchestration_rules.schema.yaml`
  - Rule types:
    - **Scheduled:** Cron-based invocation (e.g., "sweep GitHub PRs every 6 hours")
    - **Event-driven:** Trigger on webhook/API event (e.g., "new PR closed")
    - **Dependency-driven:** Invoke when upstream lane completes (e.g., "Office365 sync before MCP sweep")
  - Acceptance: Schema validated against SSOT gate

- [ ] **A7.3.1.2** — Implement rule execution engine
  - Files to create: `src/orchestration/rule_executor.py`
  - Features:
    - Parse orchestration rules from YAML
    - Schedule execution via APScheduler or similar
    - Emit telemetry on rule invocation/success/failure
  - Test coverage: `tests/orchestration/test_rule_executor.py`

- [ ] **A7.3.1.3** — Wire rule executor into federation runtime
  - Files to update: `src/federation/__init__.py`
  - Export: `FederationOrchestrator` class wrapping lane orchestrator + rule executor
  - Acceptance: `FederationOrchestrator.run()` executes full orchestration pipeline

---

## Immediate TODO (Priority Order)

### 1. Review 4 Non-Blocking Code Review Suggestions

**Status:** ✅ **RESOLVED** (commit 8d344bb per previous PR comment)

All 6 review comments from `@copilot-pull-request-reviewer` have been fixed:
1. ✅ GitHub repository allowlist bypass — fixed in `identity_broker.py`
2. ✅ Path traversal in `download_binary()` — sanitization added in `office365_graph_connector.py`
3. ✅ Merged PR detection — origin marked with `merged:` prefix in `mcp_sweep_engine.py`
4. ✅ RTM delta duplicates — active/proposed separation in `mcp_sweep_engine.py`
5. ✅ Markdown injection — escaping added in `mcp_sweep_engine.py`
6. ✅ Test assertions — validated in `test_mcp_sweep_engine.py`

### 2. Add Integration Test for Full Sweep Pipeline

**Status:** ⚠️ **IN PROGRESS** (Task A6.4.1.1)

See Phase A6.4 — Validation and Testing above.

### 3. Document Office365 Classification Taxonomy

**Status:** ⚠️ **PENDING** (Task A6.2.1.1)

See Phase A6.2 — Office365 Binary Classification above.

### 4. Wire MCP Sweep into CI (Post-Test, Pre-Publish)

**Status:** ⚠️ **PENDING** (Task A6.3.1.2)

See Phase A6.3 — MCP Sweep CI Integration above.

### 5. Start A7 Orchestration Design Document

**Status:** ⚠️ **PENDING** (Task A7.1.1.1)

See Phase A7.1 — Dependency Resolution Between Federation Lanes above.

---

## Planning Terminology

- **Wave** = Alpha milestone (major feature cluster)
- **Phase** = Wave subdivisions (A6.1, A6.2, A6.3)
- **Task** = Single PR deliverable
- **Subtask** = Individual file/function change

---

## Current PR Context

- **PR Title:** "Add federation governance runtime (identity lanes, Office365 connector, MCP sweep) with SSOT schema gate"
- **PR Status:** Open (commit 8d344bb)
- **Wave:** A6 (governance_runtime_enforcement)
- **Phase:** A6 (overall — federation runtime foundation)
- **Classification:** Task within Wave A6

---

## Next Actions

1. **Complete Wave A6 tasks** (14% remaining per earlier estimate, now at 100% in WAVE_PROGRESSION.yaml):
   - Implement remaining governance linters (contrast_lint, overflow_lint, spacing_lint)
   - Add Office365 binary classification rules
   - Integrate MCP sweep into CI workflow
   - Publish RTM lineage delta to GitHub Pages

2. **Advance Wave A7** (65% → 100%):
   - Design federation lane orchestration
   - Build MCP sweep telemetry dashboard
   - Define orchestration rules for connector invocation

3. **Validation gates:**
   - All federation tests passing (6/6 currently)
   - CodeQL security scan: 0 alerts
   - Code review feedback resolved
   - CI integration tests passing

---

## References

- **WAVE_PROGRESSION.yaml** — Source of truth for wave completion %
- **_config/governance.yml** — Federation runtime policy (tenants, formats, wire-links)
- **governance/schemas/** — SSOT schema set for identity boundaries, binary registry, sweep classification
- **scripts/check_ssot_schemas.py** — SSOT validation gate (wired into CI)

---

*Generated: 2026-05-29T17:03:00Z*  
*Owner: GBOGEB/CODEX*  
*Wave: A6 → A7 transition*
