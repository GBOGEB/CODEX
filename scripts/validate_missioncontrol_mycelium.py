#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
DOCS = ROOT / "docs"
MANIFEST = MC / "control_manifest.yaml"
GRAPH = MC / "interaction_graph.json"
PAGES_GRAPH = DOCS / "data" / "missioncontrol_interaction_graph.json"
HTML = DOCS / "missioncontrol_mycelium.html"
CONTROL_JS = DOCS / "assets" / "missioncontrol" / "control-plane.js"
INDEX = DOCS / "index.html"
METRICS = MC / "metrics_snapshot.json"
PAGES_METRICS = DOCS / "data" / "missioncontrol_metrics.json"
HISTORY = MC / "progress_history.json"
LOG_ANALYSIS = MC / "log_analysis.json"
SOURCE_REGISTRY = MC / "source_registry.yaml"
SOURCE_STATUS = MC / "source_status.json"
PAGES_SOURCE_STATUS = DOCS / "data" / "missioncontrol_source_status.json"
PORT_REGISTRY = MC / "port_registry.json"
REENTRY = MC / "reentry_v0_2.yaml"
CONTROL_PLANE = MC / "control_plane_projection.json"
PAGES_CONTROL_PLANE = DOCS / "data" / "missioncontrol_control_plane.json"
CONTROL_EVENTS = MC / "control_events.json"
PAGES_CONTROL_EVENTS = DOCS / "data" / "missioncontrol_control_events.json"
EXECUTABLE = MC / "executable_projection.json"
PAGES_EXECUTABLE = DOCS / "data" / "missioncontrol_executable_projection.json"
PREDECESSOR_PROOF = MC / "receipts" / "MYCELIUM_V02_PR839_PROOF.json"
LIVE_FEDERATION_PROOF = MC / "receipts" / "LIVE_FEDERATION_INGESTION_20260930T111600Z_PROOF.json"
GATEWAY_CONTRACT = MC / "gateway_contract.yaml"
GATEWAY_SCRIPT = ROOT / "scripts" / "missioncontrol_command_gateway.py"
GATEWAY_WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-command-gateway.yml"

EVIDENCE_STATES = {"MEASURED", "DERIVED_FROM_MEASURED", "WITHHELD"}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _is_dag(executable: dict) -> bool:
    nodes = {n.get("id") for n in executable.get("nodes", [])}
    indegree = {node: 0 for node in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in executable.get("edges", []):
        if not isinstance(edge, list) or len(edge) != 2:
            return False
        a, b = edge
        if a not in nodes or b not in nodes:
            return False
        outgoing[a].append(b)
        indegree[b] += 1
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for nxt in outgoing[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return visited == len(nodes)


def validate() -> list[str]:
    errors: list[str] = []

    required_paths = [
        MANIFEST, GRAPH, PAGES_GRAPH, HTML, CONTROL_JS, INDEX, METRICS,
        PAGES_METRICS, HISTORY, LOG_ANALYSIS, SOURCE_REGISTRY, SOURCE_STATUS,
        PAGES_SOURCE_STATUS, PORT_REGISTRY, REENTRY, CONTROL_PLANE, PAGES_CONTROL_PLANE,
        CONTROL_EVENTS, PAGES_CONTROL_EVENTS, EXECUTABLE, PAGES_EXECUTABLE,
        PREDECESSOR_PROOF, LIVE_FEDERATION_PROOF, GATEWAY_CONTRACT,
        GATEWAY_SCRIPT, GATEWAY_WORKFLOW,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing MissionControl surface: {path.relative_to(ROOT)}")
    if errors:
        return errors

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    reentry = yaml.safe_load(REENTRY.read_text(encoding="utf-8"))
    graph = _json(GRAPH)
    pages_graph = _json(PAGES_GRAPH)
    metrics = _json(METRICS)
    pages_metrics = _json(PAGES_METRICS)
    source_status = _json(SOURCE_STATUS)
    pages_source_status = _json(PAGES_SOURCE_STATUS)
    control = _json(CONTROL_PLANE)
    pages_control = _json(PAGES_CONTROL_PLANE)
    events = _json(CONTROL_EVENTS)
    pages_events = _json(PAGES_CONTROL_EVENTS)
    executable = _json(EXECUTABLE)
    pages_executable = _json(PAGES_EXECUTABLE)
    predecessor = _json(PREDECESSOR_PROOF)
    live_federation_proof = _json(LIVE_FEDERATION_PROOF)
    gateway_contract = yaml.safe_load(GATEWAY_CONTRACT.read_text(encoding="utf-8"))
    gateway_script = GATEWAY_SCRIPT.read_text(encoding="utf-8")
    gateway_workflow = GATEWAY_WORKFLOW.read_text(encoding="utf-8")

    for name, canonical, pages in [
        ("graph", graph, pages_graph),
        ("metrics", metrics, pages_metrics),
        ("source-status", source_status, pages_source_status),
        ("control-plane", control, pages_control),
        ("control-events", events, pages_events),
        ("executable-projection", executable, pages_executable),
    ]:
        if canonical != pages:
            errors.append(f"Pages {name} materialization differs from canonical")

    allowed_nodes = set(manifest["graph_contract"]["node_types"])
    allowed_edges = set(manifest["graph_contract"]["edge_types"])
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    ids = [n.get("id") for n in nodes]
    node_ids = set(ids)

    if len(ids) != len(node_ids):
        errors.append("duplicate graph node id")

    for node in nodes:
        if node.get("type") not in allowed_nodes:
            errors.append(f"unknown node type: {node.get('type')} for {node.get('id')}")
        if not node.get("state"):
            errors.append(f"node without state: {node.get('id')}")
        url = node.get("url")
        if isinstance(url, str) and url.startswith("../"):
            errors.append(f"Pages-unsafe graph URL: {node.get('id')} -> {url}")

    for edge in edges:
        if edge.get("type") not in allowed_edges:
            errors.append(f"unknown edge type: {edge.get('type')}")
        if edge.get("from") not in node_ids or edge.get("to") not in node_ids:
            errors.append(f"orphan edge endpoint: {edge}")

    required_nodes = {
        "codex_bd_queue", "current_next", "user_steer", "epic_cryoplant",
        "topic_2k_refrigeration", "qps_triage_b", "dow_b_pressure_drop",
        "repo_cryoplant_project", "config_control_plane", "evidence_pr839",
        "human_command_input", "external_abacus_authority",
        "external_cryoplant_authority", "out_control_plane", "evidence_pr845",
        "gateway_contract", "gateway_workflow", "gateway_receipts",
    }
    missing_nodes = sorted(required_nodes - node_ids)
    if missing_nodes:
        errors.append("missing interaction-control nodes: " + ", ".join(missing_nodes))

    required_federation_fields = {
        "mechanism", "source_repo", "source_ref", "source_sha", "target_repo",
        "target_ref", "target_sha", "authority_before", "authority_after", "proof",
    }
    for edge in [e for e in edges if e.get("type") == "federates"]:
        missing = sorted(k for k in required_federation_fields if not edge.get(k))
        if missing:
            errors.append(
                f"federation edge {edge.get('from')}->{edge.get('to')} missing provenance: "
                + ", ".join(missing)
            )

    html = HTML.read_text(encoding="utf-8")
    js = CONTROL_JS.read_text(encoding="utf-8")
    panel_ids = [panel["id"] for panel in manifest["layout"]["panels"]]
    expected_panels = [
        "COMMAND_INPUT_ROOT", "EXECUTION_RECOVERY", "MYCELIUM_GRAPH",
        "OUTPUT_EVIDENCE", "ANALYTICS", "FEDERATION_CONTROL",
    ]
    if panel_ids != expected_panels:
        errors.append(f"canonical panel order mismatch: {panel_ids}")
    for panel_id in panel_ids:
        if f'data-panel="{panel_id}"' not in html:
            errors.append(f"missing UI panel: {panel_id}")

    if "../mission_control/" in html:
        errors.append("Pages HTML reaches outside docs tree")
    if "data/missioncontrol_interaction_graph.json" not in html:
        errors.append("Pages HTML is not bound to materialized graph")
    if 'assets/missioncontrol/control-plane.js' not in html:
        errors.append("Pages HTML is not bound to modular control-plane JS")
    if "missioncontrol_mycelium.html" not in INDEX.read_text(encoding="utf-8"):
        errors.append("Pages index does not link MissionControl Mycelium")

    ui_tokens = {
        "golden-focus", "single-focus", 'id="focus"', 'id="projection"',
        'id="graphFilter"', 'id="graphOverlay"', 'id="edgeInspect"',
        'id="commandInput"', 'id="configUpload"', 'id="dryRunCommand"',
        'id="applyCommand"', 'id="laneRows"', 'id="priorityHorizon"',
        'id="controlEventRows"', 'id="artifactFilter"', 'id="federationRows"',
        'id="federationState"', 'id="federationEdgeRows"', "THIS IS THE WAY", 'id="metricRows"',
        'id="progressRows"', 'id="commandCopy"', 'id="gatewayLaunch"', 'id="gatewayGuide"',
    }
    for token in ui_tokens:
        if token not in html:
            errors.append(f"missing v0.2.1 UI contract token: {token}")

    js_tokens = {
        "STAGED_APPLY_WITHHELD_NO_AUTHENTICATED_GATEWAY",
        "mutation_claim:false",
        "missioncontrol_control_plane.json",
        "missioncontrol_control_events.json",
        "renderGraphArtifacts",
        "renderFederationEdges",
        "stagePrioritySteer",
        "live_federation_ingestion", "GATEWAY_URL", "probeCurrentCodeXHead",
        "trace provenance", "OPEN_GITHUB_AUTHENTICATED_GATEWAY_WORKFLOW",
    }
    for token in js_tokens:
        if token not in js:
            errors.append(f"missing modular control-plane behavior: {token}")

    invariant = manifest.get("projection_invariant", {})
    if invariant.get("id") != "THIS_IS_THE_WAY" or invariant.get("one_graph_multiple_projections") is not True:
        errors.append("THIS_IS_THE_WAY projection invariant is not bound")
    if metrics.get("guards", {}).get("same_graph_multiple_projections") is not True:
        errors.append("metrics do not preserve same-graph projection guard")

    for required_path in (HISTORY, LOG_ANALYSIS, SOURCE_REGISTRY, SOURCE_STATUS, PORT_REGISTRY):
        if not required_path.exists():
            errors.append(f"missing dynamic-ingestion control surface: {required_path.relative_to(ROOT)}")
    if metrics.get("nodes", {}).get("repo_codex", {}).get("docking", {}).get("status") not in EVIDENCE_STATES:
        errors.append("docking metric has invalid evidence state")
    if metrics.get("nodes", {}).get("repo_codex", {}).get("ports", {}).get("status") not in EVIDENCE_STATES:
        errors.append("port metric has invalid evidence state")
    source_rows = source_status.get("sources", [])
    measured_sources = [row for row in source_rows if str(row.get("status", "")).upper() in {"FRESH", "MEASURED_CHAT_CONNECTOR", "AUTHENTICATED_GATEWAY"}]
    if source_rows and len(measured_sources) != len(source_rows):
        errors.append("live federation source freshness is not complete")
    docking = metrics.get("nodes", {}).get("repo_codex", {}).get("docking", {})
    if source_rows and docking.get("fresh_sources") != len(measured_sources):
        errors.append("docking freshness metric does not match measured source count")
    if source_rows and docking.get("declared_sources") != len(source_rows):
        errors.append("docking declared-source count does not match source status")

    for layout_mode in {"2x3", "3x2", "golden_focus", "single_focus"}:
        if layout_mode not in set(manifest.get("layout", {}).get("selectable_modes", [])):
            errors.append(f"missing selectable layout mode: {layout_mode}")

    cp = manifest.get("control_plane", {})
    if cp.get("version") != "0.2.1":
        errors.append("control_plane.version must be 0.2.1")
    if cp.get("command_input", {}).get("static_pages_mode") != "STAGE_OR_DRY_RUN_ONLY":
        errors.append("static Pages command input must remain stage/dry-run only")
    if cp.get("command_input", {}).get("authenticated_apply_gateway_required") is not True:
        errors.append("authenticated Apply gateway guard missing")
    command_input = cp.get("command_input", {})
    if command_input.get("source_lock") != "EXACT_SHA":
        errors.append("gateway command input must preserve exact-SHA source lock")
    if command_input.get("mutation_mode") != "AUTOMATION_BRANCH_PR_ONLY":
        errors.append("gateway mutation mode must remain automation branch/PR only")
    if command_input.get("direct_main_write") is not False:
        errors.append("gateway must not permit direct-main write")
    if command_input.get("allowed_actions") != ["REFRESH_FEDERATION_HEADS"]:
        errors.append("gateway v0.1 action allow-list drifted")
    if "api.github.com/repos/GBOGEB/CODEX/commits/main" not in js:
        errors.append("Pages gateway source lock is not live-probed from CODEX main")
    if cp.get("execution_model", {}).get("executable_projection_must_be_DAG") is not True:
        errors.append("executable projection DAG guard missing")
    federation_status = control.get("federation_status", {})
    for key in ("bridge_status", "cherry_pick_state", "merge_state", "conflict_state", "remote_authority_state"):
        if not federation_status.get(key):
            errors.append(f"federation control state missing: {key}")
    if federation_status.get("authority_transfer") is not False:
        errors.append("federation status must preserve authority_transfer=false")
    live_federation = control.get("live_federation_ingestion", {})
    if live_federation:
        freshness = live_federation.get("freshness", {})
        if freshness.get("fresh_sources") != len(measured_sources):
            errors.append("control-plane live freshness does not match source status")
        if freshness.get("declared_sources") != len(source_rows):
            errors.append("control-plane declared source count does not match source status")
        if live_federation.get("authority_transfer") is not False:
            errors.append("live federation ingestion must preserve authority_transfer=false")
        if live_federation.get("engineering_truth_promoted") is not False:
            errors.append("live federation ingestion must not promote engineering truth")
    if gateway_contract.get("transport", {}).get("type") != "GITHUB_ACTIONS_WORKFLOW_DISPATCH":
        errors.append("gateway transport must be GitHub Actions workflow_dispatch")
    mutation = gateway_contract.get("mutation", {})
    if mutation.get("mode") != "AUTOMATION_BRANCH_PR_ONLY" or mutation.get("direct_main_write") is not False:
        errors.append("gateway contract mutation boundary is not PR-only")
    actions = gateway_contract.get("actions", {})
    if set(actions) != {"REFRESH_FEDERATION_HEADS"}:
        errors.append("gateway contract contains unapproved v0.1 action")
    if "workflow_dispatch:" not in gateway_workflow:
        errors.append("gateway workflow lacks authenticated workflow_dispatch entrypoint")
    if "contents: write" not in gateway_workflow or "pull-requests: write" not in gateway_workflow:
        errors.append("gateway workflow lacks branch/PR publication permissions")
    if "git push -u origin" not in gateway_workflow or "gh pr create" not in gateway_workflow:
        errors.append("gateway workflow does not publish reviewable branch/PR output")
    if "git push origin main" in gateway_workflow or "git push origin HEAD:main" in gateway_workflow:
        errors.append("gateway workflow contains forbidden direct-main push")
    for token in ("ALLOWED_ACTIONS", "stale source authority", "AUTOMATION_BRANCH_PR_ONLY"):
        if token not in gateway_script:
            errors.append(f"gateway fail-closed implementation token missing: {token}")
    if live_federation_proof.get("disposition") != "CONTROLLED_GREEN":
        errors.append("PR #845 live federation predecessor proof is not controlled green")
    live_hosted = live_federation_proof.get("exact_head_proof", {})
    if live_hosted.get("conclusion") != "success" or int(live_hosted.get("executed_steps", 0)) <= 0:
        errors.append("PR #845 exact-head proof lacks >0-step success")
    live_pages = live_federation_proof.get("pages", {})
    if any(live_pages.get(key) != "PASS" for key in ("build", "report", "deploy")):
        errors.append("PR #845 Pages readback is not success")
    gateway_state = control.get("authenticated_execution_gateway", {})
    if gateway_state.get("runtime_proof") != "WITHHELD_OWNER_DISPATCH_REQUIRED":
        errors.append("gateway runtime proof must remain withheld until owner dispatch")

        rendering = cp.get("rendering", {})
    for isolation_key in (
        "plotly_failure_blocks_core",
        "matplotlib_failure_blocks_core",
        "pages_failure_blocks_core",
        "browser_disconnect_blocks_core",
    ):
        if rendering.get(isolation_key) is not False:
            errors.append(f"renderer isolation guard must be false: {isolation_key}")
    if "@media(max-width:900px)" not in html:
        errors.append("responsive tablet/mobile fallback contract missing")
    for layout_token in (".grid.layout-3x2", ".grid.golden-focus", ".grid.single-focus"):
        if layout_token not in html:
            errors.append(f"responsive layout CSS missing: {layout_token}")
    if "loadControlPlane().catch" not in js or "Core graph renderer remains available by isolation contract." not in js:
        errors.append("control-plane timeout/fallback isolation behavior missing")

    if not events.get("append_only"):
        errors.append("control event history must be append-only")
    horizons = events.get("horizons", {})
    for horizon in ("current", "mid", "long"):
        if not horizons.get(horizon):
            errors.append(f"priority horizon missing or empty: {horizon}")

    if executable.get("executable_projection_must_be_DAG") is not True:
        errors.append("executable projection does not declare DAG requirement")
    if not _is_dag(executable):
        errors.append("executable projection is cyclic or malformed")
    if executable.get("guards", {}).get("replay_completed_atoms") is not False:
        errors.append("executable projection may replay completed atoms")

    if predecessor.get("disposition") != "CONTROLLED_GREEN_PREDECESSOR":
        errors.append("PR #839 predecessor proof is not controlled green")
    hosted = predecessor.get("hosted_proof", {})
    if hosted.get("conclusion") != "success" or int(hosted.get("executed_steps", 0)) <= 0:
        errors.append("PR #839 hosted proof lacks >0-step success")
    if hosted.get("validator") != "PASS" or hosted.get("tests") != "PASS":
        errors.append("PR #839 validator/tests proof missing")
    if predecessor.get("pages_readback", {}).get("conclusion") != "success":
        errors.append("PR #839 merged-main Pages readback is not success")

    reentry_root = reentry.get("reentry", {})
    invariants = reentry_root.get("invariants", {})
    if invariants.get("authority_transfer") is not False:
        errors.append("reentry authority_transfer must remain false")
    if invariants.get("formal_credit_delta") != 0 or invariants.get("engineering_credit_delta") != 0:
        errors.append("reentry credit deltas must remain zero")
    if invariants.get("replay_completed_atoms_on_reentry") is not False:
        errors.append("reentry must not replay completed atoms")
    if invariants.get("independent_lanes_continue") is not True:
        errors.append("reentry must preserve independent lane continuation")
    if invariants.get("static_pages_apply_mutates_repository") is not False:
        errors.append("static Pages must not claim repository mutation")

    if manifest.get("authority_transfer") is not False:
        errors.append("authority_transfer must remain false")
    if manifest.get("formal_credit_delta") != 0:
        errors.append("formal_credit_delta must remain zero")
    if manifest.get("engineering_authority") is not False:
        errors.append("CODEX UI must not self-promote engineering authority")

    return errors


if __name__ == "__main__":
    found = validate()
    if found:
        for item in found:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("MissionControl Mycelium validation: PASS")
