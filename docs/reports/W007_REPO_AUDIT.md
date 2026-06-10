# W007 Repository Audit

Generated: 2026-06-05 UTC

## Current File Tree (depth <= 3)

```text
.
.codex
.codex/tasks
.codex/tasks/g10_mcp_container_task.yaml
.codex/tasks/github_mcp_agentic_orchestration.yaml
.devcontainer
.devcontainer/devcontainer.json
.github
.github/copilot-instructions.md
.github/pull_request_template.md
.github/workflows
.github/workflows/abacus-render-pipeline-smoke.yml
.github/workflows/agentic-pr-discrepancy-scan.yml
.github/workflows/ci.yml
.github/workflows/codeql.yml
.github/workflows/codex_semantic_runtime_ci.yml
.github/workflows/confluence-github-bridge-phase0.yml
.github/workflows/dashboard-health.yml
.github/workflows/delta1-governance-validation.yml
.github/workflows/deploy-docs.yml
.github/workflows/deploy_pipeline.yml
.github/workflows/dmaic-commit-metrics.yml
.github/workflows/full-stack-governance.yml
.github/workflows/governance-gate.yml
.github/workflows/hbhs_ep_tuplebridge_pages.yml
.github/workflows/jekyll-gh-pages.yml
.github/workflows/pages.yml
.github/workflows/pages_deploy_runtime.yml
.github/workflows/receive_superpipeline_dispatch.yml
.github/workflows/release.yml
.github/workflows/render-governance-ci.yml
.github/workflows/render-parity.yml
.github/workflows/render-regression.yml
.github/workflows/renderer-lint.yml
.github/workflows/runtime-governance-gate.yml
.github/workflows/runtime_convergence_pipeline.yml
.github/workflows/runtime_federation_ci.yml
.github/workflows/runtime_release_gate.yml
.github/workflows/security-scan.yml
.github/workflows/semantic-validation.yml
.github/workflows/static.yml
.github/workflows/update-docs.yml
.github/workflows/w003-governance-gate.yml
.github/workflows/wcag-contrast.yml
.gitignore
01_requirements
01_requirements/RTM.csv
01_requirements/requirements.json
02_design
02_design/02A_PnID
02_design/02A_PnID/PID_ASSEMBLY_PREVIEWS.md
02_design/02A_PnID/PID_SYMBOL_CHEATSHEET.md
02_design/MASTER_FACE_SEAL_POLICY.md
03_bom
03_bom/BOM_Master.csv
04_quality
04_quality/ITP_HE_VCR.csv
04_quality/PROC_DBBA_Purge.md
04_quality/PROC_He_LeakTest_ISO20485.md
05_vendor
05_vendor/VENDOR_COSTS.md
06_arch
06_arch/ADR
06_arch/ADR/ADR.md
07_ops
07_ops/OCD
07_ops/OCD/OCD.md
3_3_6_preview-01.png
3_3_6_qplant_control_system_master.docx
3_3_6_qplant_control_system_master.pdf
99_handover
99_handover/ADDENDUM_MULTI_FORMAT_OUTPUT_TRIAGE.md
99_handover/BUILD_WORKFLOW.md
99_handover/CH15_FEATURE_TREATMENT_RULE.md
99_handover/CLEAN_HANDOVER_PACK.md
99_handover/CRYO_DASHBOARD_INTEGRATION_MASTER_PLAN.md
99_handover/FillMasterDiffPages.vba
99_handover/MASTER_DIFF.md
99_handover/MASTER_PATCH.md
99_handover/PROCESS_DMAIC.md
99_handover/RENAME_SBS.csv
ADR_OCD_Background.html
ADR_OCD_Background.md
AGENTIC
AGENTIC/comment_response_drafts.md
AGENTIC/proposed_fixes.yaml
Addendum_book_master.docx
BACKBONE_POLICY.md
BUILD_LOG.md
Book_Master.md
CHANGELOG.md
CODEX_Index.json
CODEX_Index.yaml
DELTA_1
DELTA_1/README.md
DELTA_1/branch_protection_manifest.md
DELTA_1/governance_adr_template.md
DELTA_1/governance_taxonomy.md
DELTA_1/operational_ownership_matrix.md
DELTA_1/operational_readiness_scorecard.md
DELTA_1/production_release_certification_model.md
DELTA_1/release_approval_governance.md
DELTA_1/release_audit_lineage.md
DELTA_1/release_milestone_schema.md
DELTA_1/runtime_support_governance.md
DELTA_1/sdlc_compliance_matrix.md
ERROR_LOG.md
FEATURE_BRANCH_LOCKSTEP_GUIDE.md
Full_VCR_Handover.docx
Full_VCR_Handover.html
Full_VCR_Handover.md
Full_VCR_Handover_master.docx
Full_VCR_Handover_master.html
GISTAU
GISTAU/sources
GISTAU/sources/master
GITHUB_CENTERED_SOFTWARE_DELIVERY.md
GLOBAL_index.json
GLOB_POLICY.md
GLOSSARY.yaml
GOVERNANCE.md
GitHub_Reproducible_Build_Process.md
Input
Input/Addendum II -  Cryoplant Technical Requirements_0711_1143.docx
Input/Addendum II -  Cryoplant Technical Requirements_2609_1313.docx
Input/Addendum_master.json
Input/Addendum_master.md
Input/cryoplant_deck_handover_R1C2.zip
KEB
KEB/governance
KEB/governance/GLOSSARY.yml
KEB/governance/governance_rules.yml
KEB/governance/metrics.yml
LINEAGE_BUILD_DEPLOY_CICD.md
MANIFEST
MANIFEST.json
MANIFEST/A6_FEDERATION_TODO_ROADMAP.md
MANIFEST/ABACUS_20PCT_COMPLETION_ROADMAP.md
MANIFEST/CHANGELOG.md
MANIFEST/CONVERGENCE_KPIS.yaml
MANIFEST/FEDERATION_GLOSSARY.yaml
MANIFEST/LAYOUT_GOVERNANCE.md
MANIFEST/LINEAGE.md
MANIFEST/MASTER_FIGURE_REGISTRY.yaml
MANIFEST/MASTER_SLIDE_REGISTRY.yaml
MANIFEST/PIPELINE_ARCHITECTURE.md
MANIFEST/PROGRAM_METRICS.yaml
MANIFEST/README.md
MANIFEST/README_MAX.md
MANIFEST/RENDER_RULES.md
MANIFEST/ROADMAP.md
MANIFEST/SESSION_OFFLOAD_PR_G2_A6.md
MANIFEST/SNAPSHOT_REGRESSION.md
MANIFEST/STYLE_GUIDE.md
MANIFEST/THERMODYNAMIC_KPIS.yaml
MANIFEST/TUPLE_OFFLOAD_SUMMARY.md
MANIFEST/WAVE_PROGRESSION.yaml
MANIFEST/manifest_a6.json
METRICS
METRICS/agentic_ascii_metrics.md
METRICS/g10_ascii_metrics.md
OUTPUT_MANIFEST.json
PIPELINE
PIPELINE/GLOSSARY.yaml
PIPELINE/SESSION_OFFLOADS
PIPELINE/SESSION_OFFLOADS/SESSION_2026_05_19_RUNTIME_AND_RENDER_GOVERNANCE.md
PR_CONFLICT_ANALYSIS.md
Portable_Recursive_Engineering_Handover.html
README.md
SDA_Maturity_Matrix_First_Render.md
SESSION_HISTORY
SESSION_HISTORY/2026
SESSION_HISTORY/2026/2026-05-19_A6_RENDERER_GOVERNANCE.md
SSOT
SSOT/g10_runtime_governance_ssot.yaml
SSOT/github_mcp_agentic_orchestration_ssot.yaml
TUPLES
TUPLES/2026-05-19_A6_TUPLE_SUMMARY.yaml
TUPLES/A6_RUNTIME_TUPLE_SUMMARY.yaml
TUPLES/W007.1_PR200_LINEAGE_TUPLE.yaml
VCR_ADR_OCD_Partial.docx
VCR_ADR_OCD_Partial.md
VCR_Only_Handover.docx
VCR_Only_Handover.md
VCR_Only_Handover_master.docx
VCR_Only_Handover_master.html
VCR_Quality_Procedures.docx
VCR_Quality_Procedures.md
VCR_Requirements.docx
VCR_Requirements.md
VCR_Summary.html
VCR_Summary.md
VCR_Summary.pdf
VCR_Summary_export.pdf
VCR_Summary_master.docx
VCR_Summary_master.pdf
VERSION.json
_config
_config.yml
_config/governance.yml
abacus_render_pipeline
abacus_render_pipeline/A6_renderer_governance
abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD
abacus_runtime
abacus_runtime/README.md
abacus_runtime/runtime_manifest.yaml
abacus_runtime/runtime_modules.md
agent_runtime
agent_runtime/AGENT_RUNTIME_ARCHITECTURE.md
agent_runtime/agent_metrics.json
agent_runtime/agent_topology.json
agents
agents/abacus
agents/abacus/.gitkeep
agents/abacus/FEDERATION_PROTOCOL.md
agents/codex
agents/codex/MCP_INSTRUCTION.md
agents/mcp
agents/mcp/.gitkeep
agents/sweep_mop_agent.py
automation
automation/pr_generator.py
book_md
book_md/00_title_page.md
book_md/01_table_of_contents.md
book_md/10_applicable_documents.md
book_md/10_books
book_md/10_books/20_slides
book_md/10_books/README.md
book_md/1_introduction.md
book_md/2_nature_of_the_procurement.md
book_md/3_3_10_commissioning.md
book_md/3_3_11_site_acceptance_testing.md
book_md/3_3_12_spare_parts.md
book_md/3_3_13_after_sales_services.md
book_md/3_3_14_documentation.md
book_md/3_3_1_introduction.md
book_md/3_3_2_nominal_operational_scenarios.md
book_md/3_3_3_performance_requirements.md
book_md/3_3_4_reliability_requirements.md
book_md/3_3_5_qplant_design_construction_requirements.md
book_md/3_3_6_qplant_control_system.md
book_md/3_3_7_interfaces.md
book_md/3_3_8_factory_testing.md
book_md/3_3_9_inspection_and_installation.md
book_md/3_technical_requirements.md
book_md/4_reliability_centred_maintenance_lifecycle_cost_management.md
book_md/5_safety_codes_and_standards.md
book_md/6_schedule.md
book_md/7_contract_performance.md
book_md/8_quality_assurance_and_control.md
book_md/9_appendix.md
book_md/I1_abbreviations.md
book_md/I2_terms_and_definitions.md
book_md/I3_table_of_figures.md
book_md/I4_table_of_tables.md
book_md/book_order.txt
book_md/master_outline.json
bottleneck_report.json
bridge_manifest.yaml
bridges
bridges/claude_mini_federation_bridge.yml
bridges/diagram_bridge.yml
bridges/office_bridge.yml
codex
codex/__init__.py
codex/bridges
codex/bridges/__init__.py
codex/bridges/superpipeline_payload.py
codex/renderers
codex/renderers/__init__.py
codex/renderers/abacus_report.py
codex/schemas
codex/schemas/superpipeline_render_request.schema.json
codex/templates
codex/templates/technical_status_report.md.j2
components
components/a66
components/a66/specs.md
conftest.py
core_bridge
core_bridge/__init__.py
core_bridge/absorb.py
core_bridge/ingress
core_bridge/ingress/sample_spec.txt
core_bridge/render.py
cryo
cryo-dashboard
cryo-dashboard/README.md
cryo/helium_refrigeration_requirements.md
dashboard.html
dashboards
dashboards/__init__.py
dashboards/telemetry_dashboard.py
dashboards/thermo_command_center.py
dashboards/w008_governance_dashboard.py
docs
docs/ADR
docs/ADR/README.md
docs/ALPHA_BRIDGE_ABACUS_CODEX.md
docs/ALPHA_BRIDGE_ABACUS_CODEX_REVIEW.md
docs/DMAIC
docs/DMAIC/README.md
docs/FEDERATION_BRIDGE_IMPLEMENTATION.md
docs/FEDERATION_BRIDGE_PROGRESS.md
docs/GOVERNANCE
docs/GOVERNANCE/README.md
docs/GOVERNANCE/reconciliation_matrix.md
docs/HUMAN.calculations.html
docs/HUMAN.index.html
docs/HUMAN.report.md
docs/HUMAN.traceability_table.html
docs/HUMAN.version_log.md
docs/INCUBATOR_ABACUS_BRIDGE.md
docs/INCUBATOR_INTEGRATION_PATTERNS.md
docs/INCUBATOR_W000_W001_COMPLETE.md
docs/OPENAI_CODEX_MCP_HANDOVER_2026-05-19.md
docs/RTM
docs/RTM/README.md
docs/alpha_a6_integration_layer.md
docs/architecture
docs/architecture/runtime-topology-normalization.md
docs/artifacts
docs/artifacts/CODEX_Index.json
docs/artifacts/CODEX_Index.yaml
docs/artifacts/GLOBAL_index.json
docs/artifacts/MANIFEST.json
docs/artifacts/OUTPUT_MANIFEST.json
docs/artifacts/handover_master_applied.glob.yaml
docs/cryo_dashboard
docs/cryo_dashboard/CODEX_DOCORG_DELTA_MAP_v0.4.9.md
docs/dashboard.html
docs/dashboard_topics.md
docs/deck-systems
docs/deck-systems/abacus-render-pipeline
docs/delta_1_pr_template.md
docs/engineering_portal.html
docs/features
docs/features/deck-convergence
docs/features/thermal-shields
docs/federation_bridge_dashboard.html
docs/federation_input_template.md
docs/federation_map.md
docs/gistau-ch15
docs/gistau-ch15/backend_delta_heatmap.html
docs/gistau-ch15/coolprop_binding_status.html
docs/gistau-ch15/data
docs/gistau-ch15/index.html
docs/gistau-ch15/nist_validation_review.html
docs/gistau-ch15/plots
docs/gistau-ch15/source_snippets.html
docs/gistau-ch15/visual_cards.css
docs/governance
docs/governance/WAVE_ANTHOLOGY.md
docs/governance_plan.md
docs/governance_states.md
docs/governance_w000.html
docs/handoff
docs/handoff/known-risks.md
docs/handoff/ownership.md
docs/handoff/support-model.md
docs/handover
docs/handover.html
docs/handover/RECURSIVE_IDEMPOTENT_METHOD_HANDOVER_v1.md
docs/hbhs-ep-v8.3-tuplebridge
docs/hbhs-ep-v8.3-tuplebridge/README.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_2_STATUS.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_3_STATUS.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_4_STATUS.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_6_STATUS.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_7_STATUS.md
docs/hbhs-ep-v8.3-tuplebridge/WAVE_PROGRESS_LEDGER.md
docs/hbhs-ep-v8.3-tuplebridge/index.html
docs/hbhs-ep-v8.3-tuplebridge/pr-notes.md
docs/hbhs-ep-v8.3-tuplebridge/recursive_topology.md
docs/hbhs-ep-v8.3-tuplebridge/runtime-metrics.json
docs/hbhs-ep-v8.3-tuplebridge/runtime_dashboard.html
docs/hbhs-ep-v8.3-tuplebridge/runtime_summary.md
docs/hbhs-ep-v8.3-tuplebridge/runtime_topology.json
docs/incubator-dmaic-dashboard.html
docs/incubator_index.md
docs/incubator_runtime_map.md
docs/index.html
docs/knowledge_transfer.html
docs/knowledge_transfer.md
docs/knowledge_transfer_slides.html
docs/leak_baseline
docs/leak_baseline/index.html
docs/manifest.html
docs/plots
docs/plots/01_leak_vs_loss.html
docs/plots/02_temperature_pressure_effects.html
docs/plots/03_cost_vs_leaktightness.html
docs/plots/04_fleet_sensitivity.html
docs/plots/05_reliability.html
docs/plots/index.html
docs/qcell_svg_rebuild_v0_6_0
docs/qcell_svg_rebuild_v0_6_0/CHANGELOG.md
docs/qcell_svg_rebuild_v0_6_0/docs_rebuild_plan.html
docs/qcell_svg_rebuild_v0_6_0/docs_rebuild_plan.md
docs/qcell_svg_rebuild_v0_6_0/lineage
docs/qcell_svg_rebuild_v0_6_0/reviews
docs/qcell_svg_rebuild_v0_6_0/src
docs/qplant
docs/qplant/baseline
docs/qplant/rtm
docs/qps-slide-system
docs/qps-slide-system/CHANGELOG.md
docs/qps-slide-system/README.md
docs/qps-slide-system/decks
docs/qps-slide-system/generated
docs/qps-slide-system/html
docs/qps-slide-system/index.html
docs/qps-slide-system/index.yaml
docs/qps-slide-system/maps
docs/qps-slide-system/review
docs/qps-slide-system/styles
docs/qps-slide-system/svg
docs/qps-slide-system/yaml
docs/qps-visual-knowledge-system-v1-0b
docs/qps-visual-knowledge-system-v1-0b/IMPLEMENTATION_STAGES.md
docs/qps-visual-knowledge-system-v1-3
docs/qps-visual-knowledge-system-v1-3/CODEX_HANDOFF_v1_3.md
docs/qps-visual-knowledge-system-v1-3/DECK_MANIFEST.md
docs/qps-visual-knowledge-system-v1-3/README.md
docs/reference
docs/reference/glossary.yaml
docs/reference/glossary_reference.md
docs/regression.html
docs/rendered_outputs
docs/rendered_outputs/sample_spec_export.csv
docs/rendered_outputs/sample_spec_export.html
docs/reports
docs/reports/W007_REPO_AUDIT.md
docs/review_parallel_track.md
docs/review_traceability.md
docs/rtm
docs/rtm/incubator_rtm_bridge.md
docs/rtm/local_rtm_lineage.md
docs/runbooks
docs/runbooks/deployment.md
docs/runbooks/incident.md
docs/runbooks/rollback.md
docs/runtime_governance.md
docs/runtime_map.html
docs/runtime_map.md
docs/slides_html.html
docs/traceability.html
docs/verification.html
docs/w008-governance-dashboard.html
docs/wave_packages
docs/wave_packages/A49
docs/wave_packages/A51_CLOSURE_SEQUENCE.md
docs/wave_packages/A52_kpi_registry.yaml
docs/wave_packages/A66_REGENERATION_CLOSURE.md
docs/wave_packages/glossary
docs/wave_packages/runtime
docs/wave_packages/topology
docs/wave_packages/validation
engineering_tools
engineering_tools/hbhs_ep
engineering_tools/hbhs_ep/README.md
engineering_tools/hbhs_ep/docs
engineering_tools/hbhs_ep/source
examples
examples/enterprise_config.json
examples/github_com_config.json
examples/usage_example.py
federation
federation/drift_monitor
federation/drift_monitor/.gitkeep
federation/orchestration
federation/orchestration/.gitkeep
federation/orchestration/codex_abacus_bridge_map.yaml
federation/runtime_registry
federation/runtime_registry/abacus_runtime.json
federation/runtime_registry/anthropic_runtime.json
federation/runtime_registry/artstyle_runtime.json
federation/runtime_registry/codex_runtime.json
federation/runtime_registry/gemini_runtime.json
federation/runtime_registry/qplant_runtime.json
federation/runtime_registry/runtime_registry.json
federation/runtime_registry/runtime_registry_report.json
federation/semantic_index
federation/semantic_index/schema.yaml
federation/tuple_registry
federation/tuple_registry/.gitkeep
federation/tuple_registry/T-20260530-PR200-001.yaml
federation_bridge
federation_bridge/bridge_manifest.yaml
federation_bridge/g3
federation_bridge/g3/g3_deep_matrix.json
federation_runtime
federation_runtime/.github
federation_runtime/.github/EXECUTION_HANDOVER.md
federation_runtime/.github/PULL_REQUEST_TEMPLATE.md
federation_runtime/.github/W003_PR_FOLLOW_UP.md
federation_runtime/.github/workflows
federation_runtime/README.md
federation_runtime/contracts
federation_runtime/contracts/federation_contract.yml
federation_runtime/contracts/governance_contract.schema.json
federation_runtime/contracts/mcp_runtime_directive.yml
federation_runtime/docs
federation_runtime/docs/FULL_PR_TRACE.md
federation_runtime/docs/pr_007_execution_checklist.md
federation_runtime/engines
federation_runtime/engines/build_manifest.py
federation_runtime/engines/confluence_artifact_pipeline.py
federation_runtime/engines/governance_parser.py
federation_runtime/engines/html_renderer.py
federation_runtime/engines/normalize.py
federation_runtime/engines/parser.py
federation_runtime/engines/phase0_orchestration.py
federation_runtime/engines/qplant_contractual_ingestion.py
federation_runtime/engines/validator.py
federation_runtime/governance
federation_runtime/governance/pr_track.yml
federation_runtime/governance/traceability_manifest.json
federation_runtime/governance/wave_recreation_plan.yml
federation_runtime/runtime
federation_runtime/runtime/core
federation_runtime/schema
federation_runtime/schema/governance_header.schema.json
federation_runtime/schema/registry.schema.json
federation_runtime/schema/render_graph.schema.json
federation_runtime/schema/semantic_ir.schema.json
federation_runtime/telemetry
federation_runtime/telemetry/telemetry_runtime.json
files.html
g10_production_manifest.json
g3_deep_matrix.json
g4_signal_manifest.json
g5_convergence_matrix.json
g7_production_manifest.json
g8_lifecycle_manifest.json
g9_lifecycle_manifest.json
glossary
glossary/yaml_glossary.yaml
governance
governance/BRIDGE_INTEGRATION_ANALYSIS.md
governance/LAYOUT_CONTRACTS.yaml
governance/LINEAGE_SCHEMA.yaml
governance/RENDER_LINTER.py
governance/RENDER_RULES.md
governance/RENDER_TEST_SUITE.md
governance/SEMANTIC_THEME.yaml
governance/SLIDE_ID_ENFORCER.py
governance/W000_SCAFFOLD_ANALYSIS.md
governance/WCAG_CONTRAST_CHECKER.py
governance/adr
governance/adr/ADR-0001-runtime-debug-governance.md
governance/agent_implementation_map.yml
governance/agent_registry.yml
governance/arbitration
governance/arbitration/autonomous-governance-arbitration-engine.yaml
governance/ci
governance/ci/minimum_pr_governance.yml
governance/completion
governance/completion/governance-runtime-completion-topology.yaml
governance/continuity
governance/continuity/operational-continuity-contracts.yaml
governance/continuity/recursive-sovereign-continuity.yaml
governance/contracts
governance/contracts/delta-1-runtime-federation-contract.yaml
governance/convergence
governance/convergence/operational-cognition-convergence.yaml
governance/dmaic
governance/dmaic/.gitkeep
governance/equilibrium
governance/equilibrium/theorem-equilibrium-propagation.yaml
governance/evolution
governance/evolution/federated-operational-evolution.yaml
governance/execution
governance/execution/recursive-execution-telemetry.yaml
governance/execution/recursive-runtime-observability.yaml
governance/federation_registry.yml
governance/finalization
governance/finalization/adaptive-theorem-propagation.yaml
governance/freeze
governance/freeze/delta1-topology-freeze.yaml
governance/interfaces
governance/interfaces/abacus-governance-interface-manifest.yaml
governance/interfaces/incubator-governance-interface-manifest.yaml
governance/lineage
governance/lineage/semantic-execution-lineage.yaml
governance/memory
governance/memory/federated-ecosystem-memory-semantics.yaml
governance/policy
governance/policy/federation_keb_topology.yml
governance/policy/runtime_debug_governance_rules.yml
governance/policy/ssot_runtime_control.yml
governance/preservation
governance/preservation/ecosystem-self-preservation-semantics.yaml
governance/proofs
governance/proofs/recursive-operational-completion-proofs.yaml
governance/regeneration
governance/regeneration/adaptive-continuity-recursion.yaml
governance/releases
governance/releases/delta1-release-governance.yaml
governance/render
governance/render/.gitkeep
governance/runtime
governance/runtime/delta-1-governance-runtime-index.yaml
governance/runtime_governance.yml
governance/runtime_manifest.json
governance/schemas
governance/schemas/binary_source_registry.schema.yaml
governance/schemas/identity_boundaries.schema.yaml
governance/schemas/rtm_lineage_delta.schema.yaml
governance/schemas/sweep_classification.schema.yaml
governance/sovereignty
governance/sovereignty/semantic-operational-sovereignty.yaml
governance/ssot
governance/ssot/.gitkeep
governance/stabilization
governance/stabilization/governance-cognition-stabilization.yaml
governance/synchronization
governance/synchronization/abacus-codex-recursive-sync.yaml
governance/synchronization/incubator-codex-sync.yaml
governance/telemetry
governance/telemetry/kpi_telemetry_overview.yml
governance/traceability_policy.yml
governance/trust
governance/trust/recursive-runtime-trust-engine.yaml
governance/trust/semantic-trust-propagation-engine.yaml
governance/verification
governance/verification/recursive-equilibrium-verification.yaml
handoff
handoff/README.md
handoff/v0_6_2
handoff/v0_6_2/index.html
handoff/v0_6_2/pressure_diagnostic_v0_6_2.svg
handoff/v0_6_2/qcell_view_policy_v0_6_2.yaml
handoff/v0_6_2/qps_svg_graph_navigation_mvp_v1_5
handoff/v0_6_2/temperature_analysis_v0_6_2.svg
handover
handover/ARTSTYLE_RECURSIVE_HANDOVER_2026_05_25.md
handover/ARTSTYLE_RECURSIVE_STATUS_2026_05_26.md
handover/GISTAU_CH15_TECH_TODO_IMPLEMENTATION_PLAN.md
handover/GISTAU_CH15_V11_PR_HANDOVER.md
handover/GISTAU_CH15_V11_STUDY_AND_TODO.md
handover/GISTAU_CH15_V12_PUBLISH_HTML_STATUS.md
handover/PHASE2_RECON_VALIDATION.md
handover/PHASE_3_HARDENING_CHECKLIST.md
handover/PR_G2_NUMERICAL_EXECUTION_CHECKLIST.md
handover/PR_G3_COOLPROP_BINDING_PLAN.md
handover/PR_G_BACKEND_BINDING_PHASE_PLAN.md
handover/PR_H_THERMO_VISUAL_OVERLAYS_HANDOVER.md
handover/RECURSIVE_IDEMPOTENT_GOVERNANCE_HANDOVER_2026_05_19.md
```

> Note: the repository contains deeper generated/doc trees; the bounded tree above captures the active top-level runtime, governance, docs, workflow, and SSOT surfaces without duplicating large historical output folders.

## Existing Workflows

- .github/workflows/abacus-render-pipeline-smoke.yml
- .github/workflows/agentic-pr-discrepancy-scan.yml
- .github/workflows/ci.yml
- .github/workflows/codeql.yml
- .github/workflows/codex_semantic_runtime_ci.yml
- .github/workflows/confluence-github-bridge-phase0.yml
- .github/workflows/dashboard-health.yml
- .github/workflows/delta1-governance-validation.yml
- .github/workflows/deploy-docs.yml
- .github/workflows/deploy_pipeline.yml
- .github/workflows/dmaic-commit-metrics.yml
- .github/workflows/full-stack-governance.yml
- .github/workflows/governance-gate.yml
- .github/workflows/hbhs_ep_tuplebridge_pages.yml
- .github/workflows/jekyll-gh-pages.yml
- .github/workflows/pages.yml
- .github/workflows/pages_deploy_runtime.yml
- .github/workflows/receive_superpipeline_dispatch.yml
- .github/workflows/release.yml
- .github/workflows/render-governance-ci.yml
- .github/workflows/render-parity.yml
- .github/workflows/render-regression.yml
- .github/workflows/renderer-lint.yml
- .github/workflows/runtime-governance-gate.yml
- .github/workflows/runtime_convergence_pipeline.yml
- .github/workflows/runtime_federation_ci.yml
- .github/workflows/runtime_release_gate.yml
- .github/workflows/security-scan.yml
- .github/workflows/semantic-validation.yml
- .github/workflows/static.yml
- .github/workflows/update-docs.yml
- .github/workflows/w003-governance-gate.yml
- .github/workflows/wcag-contrast.yml

## Existing Governance Files

- governance/BRIDGE_INTEGRATION_ANALYSIS.md
- governance/LAYOUT_CONTRACTS.yaml
- governance/LINEAGE_SCHEMA.yaml
- governance/RENDER_LINTER.py
- governance/RENDER_RULES.md
- governance/RENDER_TEST_SUITE.md
- governance/SEMANTIC_THEME.yaml
- governance/SLIDE_ID_ENFORCER.py
- governance/W000_SCAFFOLD_ANALYSIS.md
- governance/WCAG_CONTRAST_CHECKER.py
- governance/adr/ADR-0001-runtime-debug-governance.md
- governance/agent_implementation_map.yml
- governance/agent_registry.yml
- governance/arbitration/autonomous-governance-arbitration-engine.yaml
- governance/ci/minimum_pr_governance.yml
- governance/completion/governance-runtime-completion-topology.yaml
- governance/continuity/operational-continuity-contracts.yaml
- governance/continuity/recursive-sovereign-continuity.yaml
- governance/contracts/delta-1-runtime-federation-contract.yaml
- governance/convergence/operational-cognition-convergence.yaml
- governance/dmaic/.gitkeep
- governance/equilibrium/theorem-equilibrium-propagation.yaml
- governance/evolution/federated-operational-evolution.yaml
- governance/execution/recursive-execution-telemetry.yaml
- governance/execution/recursive-runtime-observability.yaml
- governance/federation_registry.yml
- governance/finalization/adaptive-theorem-propagation.yaml
- governance/freeze/delta1-topology-freeze.yaml
- governance/interfaces/abacus-governance-interface-manifest.yaml
- governance/interfaces/incubator-governance-interface-manifest.yaml
- governance/lineage/semantic-execution-lineage.yaml
- governance/memory/federated-ecosystem-memory-semantics.yaml
- governance/policy/federation_keb_topology.yml
- governance/policy/runtime_debug_governance_rules.yml
- governance/policy/ssot_runtime_control.yml
- governance/preservation/ecosystem-self-preservation-semantics.yaml
- governance/proofs/recursive-operational-completion-proofs.yaml
- governance/regeneration/adaptive-continuity-recursion.yaml
- governance/releases/delta1-release-governance.yaml
- governance/render/.gitkeep
- governance/runtime/delta-1-governance-runtime-index.yaml
- governance/runtime_governance.yml
- governance/runtime_manifest.json
- governance/schemas/binary_source_registry.schema.yaml
- governance/schemas/identity_boundaries.schema.yaml
- governance/schemas/rtm_lineage_delta.schema.yaml
- governance/schemas/sweep_classification.schema.yaml
- governance/sovereignty/semantic-operational-sovereignty.yaml
- governance/ssot/.gitkeep
- governance/stabilization/governance-cognition-stabilization.yaml
- governance/synchronization/abacus-codex-recursive-sync.yaml
- governance/synchronization/incubator-codex-sync.yaml
- governance/telemetry/kpi_telemetry_overview.yml
- governance/traceability_policy.yml
- governance/trust/recursive-runtime-trust-engine.yaml
- governance/trust/semantic-trust-propagation-engine.yaml
- governance/verification/recursive-equilibrium-verification.yaml

### Requested W007 Governance Baseline Presence

- MISSING: governance/pr_review_control.yaml
- MISSING: governance/ci_cd_control.yaml
- MISSING: governance/review_gate_policy.yaml
- MISSING: governance/release_policy.yaml
- MISSING: governance/branching_model.yaml

## Existing SSOT Files

- SSOT/g10_runtime_governance_ssot.yaml
- SSOT/github_mcp_agentic_orchestration_ssot.yaml

### Requested W007 SSOT Baseline Presence

- MISSING: */ssot_items.yaml
- MISSING: */clarification_register.yaml
- MISSING: */contractual_gap_register.yaml
- MISSING: */rtm_reference_matrix.yaml
- MISSING: */review_artifact_manifest.yaml
- MISSING: */semantic_traceability.yaml

## Existing Review Artifacts

- MISSING: docs/reports/MAIN_QA_REGISTER.md
- MISSING: docs/reports/COMPENDIUM.md
- MISSING: docs/reports/MANAGEMENT_SUMMARY.md
- MISSING: docs/reports/WHAT_ALAT_IS_REALLY_ASKING.md
- MISSING: docs/reports/CONTRACTUAL_GAPS.md
- MISSING: docs/review_deck.html
- MISSING: docs/VISUALIZATION_ROADMAP.md
- MISSING: docs/EXECUTIVE_DASHBOARD_SPEC.md

## Missing W007 Deliverables Before This Wave

- MISSING: docs/TRACEABILITY_DASHBOARD_SPEC.md
- MISSING: docs/GOVERNANCE_DASHBOARD_SPEC.md
- MISSING: docs/RUNTIME_ARCHITECTURE.md
- MISSING: ssot/traceability_dashboard.yaml
- MISSING: ssot/governance_dashboard.yaml
- MISSING: ssot/runtime_metrics.yaml
- MISSING: docs/dashboards/executive.html
- MISSING: docs/dashboards/traceability.html
- MISSING: docs/dashboards/governance.html
- MISSING: .github/workflows/rtm-validation.yml
- MISSING: .github/workflows/manifest-validation.yml
- MISSING: .github/workflows/release-readiness.yml
- MISSING: governance/artifact_promotion_policy.yaml
- MISSING: governance/runtime_readiness_checklist.yaml
- MISSING: governance/decision_log.md
- MISSING: docs/reports/W007_COMPLETION_REPORT.md

## Technical Debt List
- W007 named governance and SSOT baseline artifacts are not present under the expected lowercase `governance/` and `ssot/` paths, despite adjacent runtime governance assets existing elsewhere.
- Mixed `SSOT/` and missing lowercase `ssot/` conventions create ambiguity for automation and dashboard data discovery.
- Several GitHub Pages entry points already exist, but no unified W007 portal routing model ties executive, traceability, and governance views together.
- Existing workflows are broad and numerous; W007-specific runtime validation gates are not yet separated into focused RTM, manifest, and release-readiness workflows.
- Review package artifacts listed in the handoff are not discoverable at the expected paths, so the runtime layer must treat them as pending inputs rather than verified sources.
- Dashboard metrics are not yet backed by a live generator; initial pages should display static placeholders and clearly identify SSOT source expectations.

## Recommended Roadmap
1. Establish the W007 runtime contract: dashboard specifications, architecture, SSOT runtime models, and governance controls.
2. Add focused validation workflows that fail fast when RTM, manifest, SSOT, or release-gate references are missing.
3. Normalize SSOT naming by either migrating existing uppercase `SSOT/` sources or adding documented aliases for dashboard automation.
4. Connect static dashboard placeholders to checked-in YAML models via a deterministic build step in W008.
5. Backfill the missing review package and governance baseline artifacts or formally register their external locations in the manifest.
6. Add release evidence collection so future completion reports are generated from commits, workflow status, and artifact manifests.
