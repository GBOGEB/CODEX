# ABACUS / CODEX / FEDERATION Runtime Governance Scaffold

This repository is bootstrapped for **W000** runtime governance.

## Responsibility split

- **ABACUS**: runtime governance, orchestration, telemetry.
- **CODEX**: execution workers, agents, patches, pull requests.
- **FEDERATION**: capability mesh, Office/diagram adapters, binaries, APIs.

## W000 scaffold

- `governance/runtime_governance.yml`
- `governance/agent_registry.yml`
- `governance/federation_registry.yml`
- `docs/index.html`
- `docs/runtime_map.html`
- `scripts/validate_yaml.py`
- `scripts/build_manifest.py`
- `governance/runtime_manifest.json` (generated)

## Quickstart

```bash
python3 scripts/validate_yaml.py
python3 scripts/build_manifest.py
# writes governance/runtime_manifest.json
```

## W000-FEDERATED-SEMANTIC-TRACE

This repository now includes a Wave W000 bootstrap for a dual-render federation model connecting ABACUS, CODEX, and MCP runtime orchestration.

- Human semantic layer for topic-first readability
- Machine sequential layer for temporal orchestration and telemetry
- Federated traceability with semantic prefix indexing
- Completion-vector scaffolding and drift monitoring bootstrap

See:
- `federation/semantic_index/schema.yaml`
- `telemetry/pca/drift_monitor.py`
- `agents/codex/MCP_INSTRUCTION.md`
- `agents/abacus/FEDERATION_PROTOCOL.md`

# 🌌 G9 Unified Federation Framework & System Verification Specification

## Benefits of Unified Approach

1. **Maintenance**: Single codebase to maintain instead of duplicated code
2. **Consistency**: Same API and behavior across environments
3. **Testing**: Test once, works everywhere
4. **Configuration**: Only configuration differs, not implementation
5. **Deployment**: Same deployment process for both environments

## Answer to Original Question

**"Do I need to duplicate in enterprise as well?"**

**NO** - This implementation demonstrates that you can have a single, unified codebase that works with both GitHub.com and GitHub Enterprise Server through configuration-based differences rather than code duplication.

The same classes, methods, and logic work for both environments - only the URLs and configuration parameters change.

## Cross-Repository Federation (CODEX + ABACUS)

For the `GBOGEB/(CODEX + ABACUS)` topology, treat CODEX and ABACUS as separate "core-sequence" systems connected through a federation layer rather than a monorepo merge.

### Federation goals
- Preserve each repository's independent orchestration, hierarchy, and agent behavior.
- Share knowledge/events through GitHub + MCP contracts.
- Trigger follow-up workflows from lifecycle states (`start`, `in_progress`, `completed`, `failed`).

### Federation control plane
1. **State emission in each repo**
   - Emit normalized state records (`source_repo`, `workflow`, `run_id`, `state`, `timestamp`, `artifact`).
2. **Knowledge-share transport**
   - Publish state and artifacts via GitHub releases/artifacts/issues and expose them through MCP resources.
3. **Cross-repo orchestrator**
   - Subscribe to MCP resources and GitHub events; map conditions to actions.
4. **Triggered actions**
   - Open/close follow-up issues, dispatch workflows, or update status ledgers in peer repos.

### Event contract (recommended)
Use one shared event schema across CODEX and ABACUS:

```json
{
  "federation": "repo-highway-v1",
  "source_repo": "GBOGEB/CODEX",
  "workflow": "publish-overlay",
  "run_id": "12345678",
  "target_repo": "GBOGEB/ABACUS",
  "state": "completed",
  "metric": {"name": "validation_score", "value": 0.98},
  "artifact": {"kind": "manifest", "ref": "docs/gistau-ch15/data/generated_overlay_manifest.json"},
  "correlation_id": "<uuid>",
  "timestamp": "2026-05-26T00:00:00Z"
}
```

### Practical trigger examples
- **Completion trigger**: CODEX publish step reaches `completed` -> ABACUS ingest workflow starts.
- **Quality gate trigger**: metric threshold crossed -> open ABACUS optimization issue automatically.
- **Initiation trigger**: ABACUS experiment starts -> CODEX creates watch status/checkpoint.

This keeps repo autonomy while enabling deterministic federation behavior through explicit contracts and event-driven orchestration.

## PR-H2 generated overlay pipeline

This repository now includes the PR-H2 generated overlay pipeline layer for thermodynamic visualization artifacts.

- **Lineage**: `PR-G2 (backend governance) -> PR-H (visual review infrastructure) -> PR-H2 (generated overlay pipeline)`.
- **Main entrypoint**: `src/gistau_ch15/visualization/refresh_overlay_artifacts.py::refresh_overlay_artifacts()`.
- **Manifest contract + loader/validator**: `src/gistau_ch15/visualization/overlay_artifact_manifest.py`.
- **Default generated manifest location**: `docs/gistau-ch15/data/generated_overlay_manifest.json`.

`refresh_overlay_artifacts()` refreshes Pages-visible overlay artifacts and regenerates a versioned manifest containing artifact path, checksum, and size metadata for CI and publication workflows.

## Packaging conversation archives

This repository now ships with a lightweight archiving pipeline that can zip conversation folders and produce consistent manifests.

### Running the pipeline
```bash
python -m scripts.build_index --source data/handover_final --output output --dataset-name handover_final
```

The command above writes ZIP archives to `output/handover_final/` and refreshes `GLOBAL_index.json`.

### Tests
```bash
pytest
```

## Repo-level rendered Markdown (HTML) with user-friendly URL copy

If you publish this repository README as rendered HTML, prefer a **plain-language "Copy URL" action** instead of exposing only a long trace-style link. End users should be able to copy one clean link and paste it directly into:

- Microsoft Edge (Windows PC)
- Safari (iPhone)
- Chrome (iPhone)

### UX requirements (recommended)

1. Show a visible button label: **Copy URL**.
2. Copy only the canonical page URL (not debug/tracing query parameters).
3. Provide a fallback when clipboard APIs are blocked (manual select + copy prompt).
4. Keep the button touch-friendly for iPhone (minimum 44px tap target).

### Reference implementation (browser-compatible)

```html
<button id="copy-url-btn" type="button" aria-live="polite">Copy URL</button>
<script>
  (function () {
    const btn = document.getElementById("copy-url-btn");
    if (!btn) return;

    function canonicalUrl() {
      return window.location.origin + window.location.pathname;
    }

    async function copyUrl() {
      const url = canonicalUrl();
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(url);
          btn.textContent = "Copied";
          setTimeout(() => (btn.textContent = "Copy URL"), 1200);
          return;
        }
      } catch (_) {}

      const ok = window.prompt("Copy this URL:", url);
      if (ok !== null) {
        btn.textContent = "Copy URL";
      }
    }

    btn.addEventListener("click", copyUrl);
  })();
</script>
```

### Notes

- On iPhone Safari/Chrome, Clipboard API behavior can vary by iOS version and page security context; the prompt fallback keeps the flow usable.
- If governance requires traceability, store trace IDs in backend logs/metadata rather than forcing end users to copy parameter-heavy URLs.

## One-cycle SDLC, lineage, and CI/CD reference

For a direct, operations-ready definition of one full engineering cycle (clone/sync -> validate -> build -> test -> artifact lineage -> commit/push -> CI/CD gates), see:

- [`LINEAGE_BUILD_DEPLOY_CICD.md`](LINEAGE_BUILD_DEPLOY_CICD.md)

Use this as the 100% completion checklist for build/deploy governance and release readiness.
