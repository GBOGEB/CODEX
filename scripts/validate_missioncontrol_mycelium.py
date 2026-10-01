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
GRAPH_ANALYSIS = MC / "graph_analysis.json"
PAGES_GRAPH_ANALYSIS = DOCS / "data" / "missioncontrol_graph_analysis.json"
GRAPH_EXPLORER = DOCS / "missioncontrol_graph_explorer.html"
GRAPH_SVG = DOCS / "assets" / "missioncontrol" / "missioncontrol_degree_distribution.svg"
GRAPH_BUILDER = ROOT / "scripts" / "build_missioncontrol_graph_publication.py"
GRAPH_MATPLOTLIB = ROOT / "scripts" / "render_missioncontrol_graph_matplotlib.py"
GRAPH_WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-graph-publication.yml"
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
TRANSPORT_RUNTIME = ROOT / "scripts" / "missioncontrol_authenticated_transport.py"
TRANSPORT_WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-authenticated-transport.yml"
OWNER_COMMENT_WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-owner-comment-transport.yml"
OWNER_COMMENT_TEST = ROOT / "tests" / "test_missioncontrol_owner_comment_transport.py"
TRANSPORT_TEST = ROOT / "tests" / "test_missioncontrol_authenticated_transport.py"

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
        MANIFEST, GRAPH, PAGES_GRAPH, GRAPH_ANALYSIS, PAGES_GRAPH_ANALYSIS,
        GRAPH_EXPLORER, GRAPH_SVG, GRAPH_BUILDER, GRAPH_MATPLOTLIB, GRAPH_WORKFLOW,
        HTML, CONTROL_JS, INDEX, METRICS,
        PAGES_METRICS, HISTORY, LOG_ANALYSIS, SOURCE_REGISTRY, SOURCE_STATUS,
        PAGES_SOURCE_STATUS, PORT_REGISTRY, REENTRY, CONTROL_PLANE, PAGES_CONTROL_PLANE,
        CONTROL_EVENTS, PAGES_CONTROL_EVENTS, EXECUTABLE, PAGES_EXECUTABLE,
        PREDECESSOR_PROOF, TRANSPORT_RUNTIME, TRANSPORT_WORKFLOW, OWNER_COMMENT_WORKFLOW,
        OWNER_COMMENT_TEST, TRANSPORT_TEST,
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
    graph_analysis = _json(GRAPH_ANALYSIS)
    pages_graph_analysis = _json(PAGES_GRAPH_ANALYSIS)
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

    for name, canonical, pages in [
        ("graph", graph, pages_graph),
        ("graph-analysis", graph_analysis, pages_graph_analysis),
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
        "external_cryoplant_authority", "out_control_plane",
        "gateway_design", "gateway_transport", "gateway_transport_receipt",
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

    if "missioncontrol_graph_explorer.html" not in html:
        errors.append("Mycelium analytics panel does not link graph explorer")
    explorer = GRAPH_EXPLORER.read_text(encoding="utf-8")
    for token in (
        "data/missioncontrol_interaction_graph.json",
        "data/missioncontrol_graph_analysis.json",
        "cdn.plot.ly/plotly-2.35.2.min.js",
        "missioncontrol_degree_distribution.svg",
        "missioncontrol_degree_distribution.png",
        "source/original",
        "Plotly unavailable; core SVG/table fallback preserved.",
    ):
        if token not in explorer:
            errors.append(f"graph explorer missing publication token: {token}")
    graph_pub = manifest.get("graph_publication", {})
    if graph_pub.get("source_graph") != "mission_control/mycelium/interaction_graph.json":
        errors.append("graph publication is not bound to canonical source graph")
    if graph_pub.get("invariants", {}).get("one_graph_multiple_renderers") is not True:
        errors.append("graph publication one-graph/multiple-renderers invariant missing")
    if graph_pub.get("interactive", {}).get("failure_blocks_core") is not False:
        errors.append("Plotly projection may not block core")
    if graph_pub.get("static", {}).get("failure_blocks_core") is not False:
        errors.append("Matplotlib projection may not block core")
    if graph_analysis.get("authority_class") != "DERIVED_PROJECTION_ONLY":
        errors.append("graph analysis must remain derived projection only")
    if graph_analysis.get("graph", {}).get("node_count") != len(nodes):
        errors.append("graph analysis node count does not match canonical graph")
    if graph_analysis.get("graph", {}).get("edge_count") != len(edges):
        errors.append("graph analysis edge count does not match canonical graph")
    if "'removed '+mech.removed_w293+' / '+mech.files+' files" in html:
        errors.append("W293 renderer assumes optional removed/files fields and can emit undefined")
    for required_mech_token in ("mechDetails", "repository_total_flake8", "mech.evidence_pr"):
        if required_mech_token not in html:
            errors.append(f"W293 renderer missing resilient metric token: {required_mech_token}")

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
        "MISSIONCONTROL_AUTHENTICATED_TRANSPORT_URL",
        "buildAuthenticatedTransportRequest",
        "action_class:'STAGE_ONLY'",
        "mutation_claim:false",
        "missioncontrol_control_plane.json",
        "missioncontrol_control_events.json",
        "renderGraphArtifacts",
        "renderFederationEdges",
        "stagePrioritySteer",
        "live_federation_ingestion",
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
    measured_sources = [row for row in source_rows if str(row.get("status", "")).upper() in {"FRESH", "MEASURED_CHAT_CONNECTOR"}]
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
    if cp.get("execution_model", {}).get("executable_projection_must_be_DAG") is not True:
        errors.append("executable projection DAG guard missing")

    gateway = manifest.get("authenticated_execution_gateway", {})
    if gateway.get("state") != "BOUNDED_APPLY_IMPLEMENTED_DISABLED_EXACT_HEAD_GREEN":
        errors.append("authenticated gateway manifest is not bounded-apply exact-head green/disabled")
    if gateway.get("selected_transport_class") != "MANUALLY_APPROVED_ACTION":
        errors.append("authenticated transport must use manually approved action class")
    if gateway.get("selected_transport_implementation") != "GITHUB_ISSUE_COMMENT_OWNER_STAGE_ONLY":
        errors.append("authenticated owner-comment transport implementation mismatch")
    if gateway.get("enabled_mutation_transports") != [] or gateway.get("mutation_enabled") is not False:
        errors.append("authenticated runtime proof may not enable mutation")
    runtime_receipt_ref = gateway.get("runtime_receipt")
    if not runtime_receipt_ref:
        errors.append("authenticated runtime receipt reference missing")
        runtime_receipt = {}
    else:
        runtime_receipt_path = ROOT / runtime_receipt_ref
        if not runtime_receipt_path.exists():
            errors.append("authenticated runtime receipt file missing")
            runtime_receipt = {}
        else:
            runtime_receipt = _json(runtime_receipt_path)
    if runtime_receipt:
        if runtime_receipt.get("decision") != "EXECUTED":
            errors.append("runtime dry-run receipt decision is not EXECUTED")
        if runtime_receipt.get("observed_head_sha") != gateway.get("runtime_observed_head_sha"):
            errors.append("runtime receipt head does not match manifest")
        if runtime_receipt.get("workflow_run") != gateway.get("runtime_run"):
            errors.append("runtime receipt run does not match manifest")
        if runtime_receipt.get("workflow_job") != gateway.get("runtime_job"):
            errors.append("runtime receipt job does not match manifest")
        if runtime_receipt.get("after_sha") is not None:
            errors.append("runtime STAGE_ONLY receipt must have after_sha=null")
        if runtime_receipt.get("authority_transfer") is not False:
            errors.append("runtime receipt must preserve authority_transfer=false")
        if runtime_receipt.get("formal_credit_delta") != 0 or runtime_receipt.get("engineering_credit_delta") != 0:
            errors.append("runtime receipt may not grant formal/engineering credit")

    control_gateway = control.get("authenticated_execution_gateway", {})
    if control_gateway.get("mutation_enabled") is not False:
        errors.append("control plane may not advertise mutation-enabled gateway")
    if control_gateway.get("runtime_dry_run_proof") != "EXECUTED_EXACT_HEAD_NO_MUTATION":
        errors.append("runtime dry-run proof must be exact-head executed/no-mutation")

    executable_states = {n.get("id"): n.get("state") for n in executable.get("nodes", [])}
    if executable_states.get("AUTHENTICATED_EXECUTION_GATEWAY_DESIGN") != "COMPLETED":
        errors.append("gateway design predecessor is not completed")
    if executable_states.get("SELECT_AUTHENTICATED_TRANSPORT") != "COMPLETED":
        errors.append("authenticated transport selection is not completed")
    if executable_states.get("AUTHENTICATED_TRANSPORT_EXACT_HEAD_PROOF") != "COMPLETED":
        errors.append("authenticated transport exact-head proof atom is not completed")
    if executable_states.get("GATEWAY_RUNTIME_DRY_RUN_OWNER_DISPATCH") != "COMPLETED":
        errors.append("owner runtime dry-run atom is not completed")
    if executable_states.get("IMPLEMENT_CODEX_ONLY_BOUNDED_APPLY") != "COMPLETED":
        errors.append("bounded apply implementation atom is not completed")
    if executable_states.get("PROVE_GATEWAY_EXACT_HEAD_AND_REPLAY_GUARDS") != "COMPLETED":
        errors.append("bounded apply exact-head/replay proof atom is not completed")
    if executable_states.get("MUTATION_ENABLEMENT_GOVERNANCE_PROMOTION") != "WITHHELD_EXPLICIT_PROMOTION_REQUIRED":
        errors.append("mutation enablement promotion must remain explicitly withheld")
    if executable.get("first_incomplete_atoms") != ["MUTATION_ENABLEMENT_GOVERNANCE_PROMOTION"]:
        errors.append("mutation promotion hold is not the first incomplete atom after bounded-apply proof")
    if control_gateway.get("bounded_apply_state") != "IMPLEMENTED_DISABLED_EXACT_HEAD_GREEN":
        errors.append("control plane bounded-apply state is not exact-head green/disabled")
    if control_gateway.get("mutation_promotion_state") != "WITHHELD_EXPLICIT_PROMOTION_REQUIRED":
        errors.append("control plane mutation promotion is not explicitly withheld")
    if control_gateway.get("enabled_mutation_transports") != []:
        errors.append("control plane may not enable mutation transports after bounded-apply proof")

    transport_workflow = TRANSPORT_WORKFLOW.read_text(encoding="utf-8")
    if "contents: write" in transport_workflow or "pull-requests: write" in transport_workflow:
        errors.append("authenticated transport workflow must remain read-only")
    if "--execute" in transport_workflow or "git push" in transport_workflow:
        errors.append("authenticated transport workflow contains mutation path")
    for token in ("workflow_dispatch:", "contents: read", "missioncontrol_authenticated_transport.py"):
        if token not in transport_workflow:
            errors.append(f"authenticated transport workflow missing: {token}")
    owner_comment_workflow = OWNER_COMMENT_WORKFLOW.read_text(encoding="utf-8")
    if "contents: write" in owner_comment_workflow or "pull-requests: write" in owner_comment_workflow:
        errors.append("owner-comment stage transport may not gain repository write permission")
    if "--execute" in owner_comment_workflow or "git push" in owner_comment_workflow:
        errors.append("owner-comment stage transport contains mutation path")
    for token in (
        "issue_comment:",
        "github.event.issue.number == 879",
        "github.event.comment.author_association == 'OWNER'",
        "contents: read",
        "issues: write",
        "missioncontrol_authenticated_transport.py",
    ):
        if token not in owner_comment_workflow:
            errors.append(f"owner-comment transport missing: {token}")
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
