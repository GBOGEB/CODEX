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
PORT_REGISTRY = MC / "port_registry.json"
REENTRY = MC / "reentry_v0_2.yaml"
CONTROL_PLANE = MC / "control_plane_projection.json"
PAGES_CONTROL_PLANE = DOCS / "data" / "missioncontrol_control_plane.json"
CONTROL_EVENTS = MC / "control_events.json"
PAGES_CONTROL_EVENTS = DOCS / "data" / "missioncontrol_control_events.json"
EXECUTABLE = MC / "executable_projection.json"
PAGES_EXECUTABLE = DOCS / "data" / "missioncontrol_executable_projection.json"
PREDECESSOR_PROOF = MC / "receipts" / "MYCELIUM_V02_PR839_PROOF.json"
FEDERATION_EVENTS = MC / "federation_events.json"
PAGES_FEDERATION_EVENTS = DOCS / "data" / "missioncontrol_federation_events.json"
LIVE_INGEST_WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-live-federation.yml"

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
        PORT_REGISTRY, REENTRY, CONTROL_PLANE, PAGES_CONTROL_PLANE,
        CONTROL_EVENTS, PAGES_CONTROL_EVENTS, EXECUTABLE, PAGES_EXECUTABLE,
        PREDECESSOR_PROOF, FEDERATION_EVENTS, PAGES_FEDERATION_EVENTS,
        LIVE_INGEST_WORKFLOW,
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
    control = _json(CONTROL_PLANE)
    pages_control = _json(PAGES_CONTROL_PLANE)
    events = _json(CONTROL_EVENTS)
    pages_events = _json(PAGES_CONTROL_EVENTS)
    executable = _json(EXECUTABLE)
    pages_executable = _json(PAGES_EXECUTABLE)
    predecessor = _json(PREDECESSOR_PROOF)
    federation_events = _json(FEDERATION_EVENTS)
    pages_federation_events = _json(PAGES_FEDERATION_EVENTS)
    source_registry = yaml.safe_load(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source_status = _json(SOURCE_STATUS)

    for name, canonical, pages in [
        ("graph", graph, pages_graph),
        ("metrics", metrics, pages_metrics),
        ("control-plane", control, pages_control),
        ("control-events", events, pages_events),
        ("executable-projection", executable, pages_executable),
        ("federation-events", federation_events, pages_federation_events),
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
        'id="progressRows"',
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

    registry_sources = source_registry.get("sources", [])
    status_sources = {row.get("id"): row for row in source_status.get("sources", [])}
    if len(registry_sources) != 3:
        errors.append(f"expected exactly 3 governed federation sources, found {len(registry_sources)}")
    for source in registry_sources:
        sid = source.get("id")
        ingest = set(source.get("ingest", []))
        if "head" not in ingest:
            errors.append(f"source registry missing exact-head ingestion: {sid}")
        if not source.get("branch"):
            errors.append(f"source registry missing branch: {sid}")
        if int(source.get("freshness_minutes", 0)) <= 0:
            errors.append(f"source registry invalid freshness threshold: {sid}")
        observed = status_sources.get(sid)
        if not observed:
            errors.append(f"source status missing governed source: {sid}")
            continue
        head_sha = observed.get("head_sha")
        if not isinstance(head_sha, str) or len(head_sha) != 40:
            errors.append(f"source status missing exact 40-char head SHA: {sid}")
        if observed.get("freshness_status") not in {"FRESH", "STALE", "ERROR"}:
            errors.append(f"source status invalid freshness state: {sid}")

    if federation_events.get("append_only") is not True:
        errors.append("federation event history must be append-only")
    if federation_events.get("authority") != "PUBLIC_METADATA_OBSERVATION_ONLY":
        errors.append("federation event authority must remain observation-only")
    for event in federation_events.get("events", []):
        if event.get("authority_transfer") is not False:
            errors.append(f"federation event may transfer authority: {event.get('id')}")

    live_workflow = LIVE_INGEST_WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "MissionControl Live Federation Ingestion",
        "schedule:",
        "--output-dir",
        "missioncontrol-live-federation",
        "GITHUB_TOKEN",
        "contents: read",
        "pull-requests: read",
    ):
        if token not in live_workflow:
            errors.append(f"live federation workflow contract missing: {token}")
    if metrics.get("nodes", {}).get("repo_codex", {}).get("docking", {}).get("status") not in EVIDENCE_STATES:
        errors.append("docking metric has invalid evidence state")
    if metrics.get("nodes", {}).get("repo_codex", {}).get("ports", {}).get("status") not in EVIDENCE_STATES:
        errors.append("port metric has invalid evidence state")

    for layout_mode in {"2x3", "3x2", "golden_focus", "single_focus"}:
        if layout_mode not in set(manifest.get("layout", {}).get("selectable_modes", [])):
            errors.append(f"missing selectable layout mode: {layout_mode}")

    cp = manifest.get("control_plane", {})
    if cp.get("version") != "0.2.2":
        errors.append("control_plane.version must be 0.2.2")
    live_ingest = manifest.get("live_federation_ingestion", {})
    if live_ingest.get("mode") != "READ_ONLY_PUBLIC_METADATA":
        errors.append("live federation ingestion must remain read-only public metadata")
    if live_ingest.get("exact_head_required") is not True:
        errors.append("live federation ingestion must require exact heads")
    if live_ingest.get("authority_transfer") is not False:
        errors.append("live federation ingestion may not transfer authority")
    if live_ingest.get("repository_mutation") is not False:
        errors.append("live federation ingestion may not mutate repositories")

    if cp.get("command_input", {}).get("static_pages_mode") != "STAGE_OR_DRY_RUN_ONLY":
        errors.append("static Pages command input must remain stage/dry-run only")
    if cp.get("command_input", {}).get("authenticated_apply_gateway_required") is not True:
        errors.append("authenticated Apply gateway guard missing")
    if cp.get("execution_model", {}).get("executable_projection_must_be_DAG") is not True:
        errors.append("executable projection DAG guard missing")
    federation_status = control.get("federation_status", {})
    for key in ("bridge_status", "cherry_pick_state", "merge_state", "conflict_state", "remote_authority_state"):
        if not federation_status.get(key):
            errors.append(f"federation control state missing: {key}")
    if federation_status.get("authority_transfer") is not False:
        errors.append("federation status must preserve authority_transfer=false")
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
    executable_states = {n.get("id"): n.get("state") for n in executable.get("nodes", [])}
    if executable_states.get("LIVE_TEMPORAL_FEDERATION_INGESTION") not in {"IN_PROGRESS", "COMPLETED"}:
        errors.append("live temporal federation ingestion is not admitted in executable DAG")
    for required_atom in ("HOSTED_LIVE_INGESTION_PROOF", "BIND_FEDERATION_FRESHNESS", "CONSUME_TYPED_REMOTE_RETURNS"):
        if required_atom not in executable_states:
            errors.append(f"missing live federation successor atom: {required_atom}")

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
