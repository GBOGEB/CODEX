"""Source-contract checks for the review-only federated MissionControl launchpad."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "docs/data/missioncontrol_federated_dag_v1.json"
HTML = ROOT / "docs/missioncontrol_federated_launchpad.html"


def test_graph_semantics() -> None:
    d = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = d["nodes"]
    edges = d["edges"]
    ids = [node["id"] for node in nodes]
    assert len(ids) == len(set(ids))
    assert all(e["from"] in ids and e["to"] in ids for e in edges)
    assert len(nodes) >= 18 and len(edges) >= 20
    adj = {id_: [] for id_ in ids}
    for edge in edges:
        if edge["kind"] == "dependency":
            adj[edge["from"]].append(edge["to"])
    active, seen = set(), set()

    def visit(node: str) -> None:
        assert node not in active, "dependency cycle found"
        if node in seen:
            return
        active.add(node)
        for child in adj[node]:
            visit(child)
        active.remove(node)
        seen.add(node)

    for n in ids:
        visit(n)
    assert d["snapshot"]["mutation_enabled"] is False
    assert d["snapshot"]["P0_admission"] == "HOLD"
    assert d["snapshot"]["authenticated_abacus_worker_run_id"] is None
    assert d["scheduler"]["dispatch_state"] == "STAGED_NOT_LAUNCHED"
    assert len(d["sipoc"]) >= 5


def test_coverage_scope_and_missing_data() -> None:
    d = json.loads(GRAPH.read_text(encoding="utf-8"))
    coverage = d["snapshot"]["coverage"]
    assert coverage["main"]["baseline_pct"] == 36.85
    assert coverage["pr_broad"]["baseline_pct"] == 36.92
    assert coverage["pr_diff"]["baseline_pct"] == 51
    assert all(v["current_pct"] is None and v["delta_pp"] is None for v in coverage.values())


def test_launchpad_links_and_accessibility() -> None:
    d = json.loads(GRAPH.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    assert "<title>" in html and "<h1>" in html
    assert "aria-label=" in html and "keydown" in html
    assert "missioncontrol_federated_dag_v1.json" in html
    assert "No live refresh" in html
    for link in d["links"]:
        href = link["href"]
        if "://" not in href:
            assert (ROOT / "docs" / href).is_file(), href
    assert all(n["url"].startswith("https://github.com/") or (ROOT / "docs" / n["url"]).exists() for n in d["nodes"])
