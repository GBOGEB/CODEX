"""The QPS navigation graph is generated from the node YAML records and kept current."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEM = REPO_ROOT / "docs/qps-slide-system"


def _builder():
    spec = importlib.util.spec_from_file_location("build_qps_node_graph", REPO_ROOT / "tools/build_qps_node_graph.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_graph_and_node_pages_are_current():
    builder = _builder()
    assert builder.stale_outputs(builder.render_all()) == [], "regenerate: python tools/build_qps_node_graph.py"


def test_render_is_deterministic():
    builder = _builder()
    assert builder.render_all() == builder.render_all()


def test_every_node_has_a_page_and_a_box():
    builder = _builder()
    nodes = builder.load_nodes()
    svg = (SYSTEM / builder.SVG_PATH).read_text(encoding="utf-8")
    for node_id, rec in nodes.items():
        assert (SYSTEM / f"html/node/{rec['stem']}.html").exists()
        assert f'<a href="../../html/node/{rec["stem"]}.html" data-node="{node_id}">' in svg


def test_tree_and_interface_edges_are_drawn_distinctly():
    builder = _builder()
    nodes = builder.load_nodes()
    svg = (SYSTEM / builder.SVG_PATH).read_text(encoding="utf-8")
    drawn = {kind: set() for kind in ("tree", "link")}
    for kind, a, b in re.findall(r'data-edge="(tree|link)" data-from="([^"]+)" data-to="([^"]+)"', svg):
        drawn[kind].add(frozenset((a, b)))
    tree = {frozenset((rec["parent"], n)) for n, rec in nodes.items() if rec["parent"] != builder.ROOT}
    assert drawn["tree"] == tree
    declared = {frozenset((n, o)) for n, rec in nodes.items() for o in rec["interfaces"]}
    assert drawn["link"] == declared - tree  # every interface drawn once; tree pairs are not redrawn
    assert drawn["link"], "the graph must show at least one interface link, not only the tree"


def test_every_relative_link_resolves():
    builder = _builder()
    for rel in builder.render_all():
        page = SYSTEM / rel
        for href in re.findall(r'(?:href|data)="([^"#:]+)"', page.read_text(encoding="utf-8")):
            assert (page.parent / href).resolve().exists(), f"{rel}: broken link {href}"


def _write_nodes(tmp_path: Path, records: dict[str, dict]) -> Path:
    nodes_dir = tmp_path / "nodes"
    nodes_dir.mkdir()
    for stem, record in records.items():
        base = {"type": "subsystem", "interfaces": [], "plots": [], "slides": [], "source_refs": []}
        (nodes_dir / f"{stem}.yaml").write_text(yaml.safe_dump({"node": {**base, **record}}), encoding="utf-8")
    return nodes_dir


@pytest.mark.parametrize(
    ("records", "message"),
    [
        ({"a": {"id": "A", "parent": "MISSING"}}, "parent MISSING is not a node"),
        ({"a": {"id": "A", "parent": "ROOT", "interfaces": ["GHOST"]}}, "interface GHOST is not a node"),
        ({"a": {"id": "A", "parent": "ROOT", "interfaces": ["A"]}}, "interface to itself"),
        ({"a": {"id": "A", "parent": "ROOT"}, "b": {"id": "A", "parent": "ROOT"}}, "duplicate node id A"),
        ({"a": {"id": "A", "parent": "B"}, "b": {"id": "B", "parent": "A"}}, "cycle"),
        ({"a": {"id": "A", "parent": "ROOT", "plots": "UTIL.PLOT.01"}}, "'plots' must be a list"),
    ],
)
def test_invalid_records_fail_closed(tmp_path, records, message):
    builder = _builder()
    with pytest.raises(builder.NodeGraphError, match=re.escape(message)):
        builder.load_nodes(_write_nodes(tmp_path, records), builder.SCHEMA)


def test_missing_schema_key_fails_closed(tmp_path):
    builder = _builder()
    nodes_dir = tmp_path / "nodes"
    nodes_dir.mkdir()
    (nodes_dir / "a.yaml").write_text(yaml.safe_dump({"node": {"id": "A", "parent": "ROOT"}}), encoding="utf-8")
    with pytest.raises(builder.NodeGraphError, match="missing keys"):
        builder.load_nodes(nodes_dir, builder.SCHEMA)


def test_check_mode_reports_stale(monkeypatch, tmp_path):
    builder = _builder()
    outputs = builder.render_all()
    monkeypatch.setattr(builder, "SYSTEM", tmp_path)
    assert set(builder.stale_outputs(outputs)) == set(outputs)
    monkeypatch.setattr(builder, "render_all", lambda: outputs)
    assert builder.main(["--check"]) == 1
    assert builder.main([]) == 0
    assert builder.main(["--check"]) == 0
