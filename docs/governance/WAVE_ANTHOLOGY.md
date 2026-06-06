# WAVE ANTHOLOGY — DMAIC Execution Framework

Canonical project tracking file for the Confluence-GitHub Bridge, Orchestration, and Rudimentary Federation System.

Core principle: **Federation, not duplication.** GitHub remains the source-of-truth and artifact-generation engine; Confluence remains the human-facing navigation, presentation, brainstorming, and contextual hub.

Phase 0 context: Atlassian site root `https://myrrha.atlassian.net`, source page ID `1023934467`, source space `ACR`, Basic Auth via email plus API token, and a strict read-only control rule: **NO write, publish, or update operations until read-only ingestion is stable.**

## DMAIC Control Model

Every implementation wave SHALL be tracked through:

```text
Define → Measure → Analyze → Improve → Control
```

Each wave record SHALL preserve:

```text
Wave ID
Objective
Inputs
Outputs
Risks
Acceptance Criteria
Completion State
Architectural Truths Learned
```

## Wave Register

| Wave ID | Objective | Inputs | Outputs | Risks | Acceptance Criteria | Completion State | Architectural Truths Learned |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PHASE0-CD-ITEM1 | Read targeted Confluence page and emit GitHub-controlled artifacts. | Confluence Space `ACR`; page `DSBT Task 3 - Technical Support`; page ID `1023934467`; optional Confluence REST credentials; offline storage fixture for CI smoke execution. | `outputs/confluence/page_1023934467/raw_storage.html`; `content.md`; `metadata.yaml`; `links.json`; `attachments.json`. | Credential unavailability; Confluence storage-format macro variance; attachment permission boundaries; page hierarchy drift. | Pipeline can read live page when credentials are supplied or run deterministic fixture mode in CI; artifacts preserve raw storage, readable Markdown, metadata, links, attachments, hierarchy counts, macros, images, tables, and expandable sections. | Initialized — fixture artifacts generated; live-read path implemented and gated by credentials. | Confluence is a federation/navigation surface; raw storage must be preserved because lossy Markdown conversion cannot be the contractual archive. |
| PHASE0-CD-ITEM2 | Ingest locked QPLANT contractual baseline into structured GitHub-controlled content while preserving source traceability. | `Book_Master.md`; `VCR_Requirements.md`; `VCR_Summary.md`; future locked contractual source artifacts. | `docs/qplant/baseline/`; `docs/qplant/rtm/`; `outputs/qplant/contractual_ingestion/`. | Accidental reinterpretation of contractual obligations; overwrite of locked baselines; weak delta visibility; ambiguous requirement numbering. | Generated manifest records source checksums; RTM links extracted requirement statements to source file and line markers; deltas are emitted separately; locked source files are not mutated. | Initialized — baseline manifest, RTM, requirements JSON, and empty delta ledger generated. | Contractual baselines must remain immutable inputs; GitHub artifacts are traceable projections and delta ledgers, not replacement authorities. |
| PHASE0-ORCH-001 | Seed orchestration links and rudimentary cross-repository signals. | CD_Item1 metadata; CD_Item2 manifest; repository module ownership; future ABACUS/CODEX processing jobs. | `outputs/orchestration/task_links.yaml`; `outputs/orchestration/cross_repo_signals.yaml`. | Premature issue binding; target repository ownership ambiguity; signal schema growth without governance. | Signals include `source_content_id`, `target_repository`, `requested_action`, `payload_status`, and `trace_reference`; task links map content to issues, engineering tasks, modules, and future jobs. | Initialized — rudimentary YAML signals generated. | Cross-repository triggering starts as auditable intent files before automation mutates downstream repositories. |

## DMAIC Baseline — Phase 0

### Define

Phase 0 initializes a bridge in which Confluence content can be read and represented as GitHub artifacts, QPLANT locked contractual material can be ingested without source mutation, and orchestration signals can link extracted content to engineering work.

### Measure

Initial control metrics:

- Confluence artifact set present for page ID `1023934467`.
- QPLANT baseline source checksums captured.
- Extracted QPLANT requirement count captured in `docs/qplant/baseline/contractual_baseline_manifest.yaml`.
- Orchestration task-link and cross-repository signal files present.

### Analyze

Phase 0 separates three concerns:

1. **Acquisition** — read Confluence or contractual sources.
2. **Projection** — emit GitHub-controlled artifacts for archival, navigation, and machine processing.
3. **Signaling** — describe downstream requested actions without prematurely coupling repositories.

### Improve

Immediate improvement backlog:

- Add authenticated Confluence CI execution once repository secrets are available.
- Add richer Confluence storage macro normalization for Jira, excerpt, page-tree, status, and attachment-preview macros.
- Add schema validation for task-link and cross-repository signal YAML.
- Add dedicated QPLANT baseline source manifests for future locked PDFs/DOCX bundles.

### Control

Control rules:

- Do not overwrite locked contractual source requirements.
- Do not reinterpret contractual obligations without trace markers.
- Preserve raw Confluence storage HTML alongside derived Markdown.
- Emit deltas separately from baseline projections.
- Keep cross-repository requests as auditable signals until target repository governance authorizes automation.
- Do not add Confluence write, publish, update, delete, or synchronization methods during Phase 0 read-only stabilization.
