"""Tests for the GLOOB global mesh book projection runtime (W111)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from src.orchestration.global_mesh_book_runtime_v1 import (
    BOUNDARY_ORDER,
    RENDERER_VERSION,
    GlobalMeshBookRuntime,
)

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "federation" / "global_mesh"
NODES = json.loads((MESH / "example_nodes.json").read_text(encoding="utf-8"))["nodes"]
MANIFEST = json.loads((MESH / "view_manifest.default.json").read_text(encoding="utf-8"))
CONTRACT = yaml.safe_load((MESH / "GLOBAL_MESH_VIEW_CONTRACT_v1.yaml").read_text(encoding="utf-8"))


def _manifest(**overrides):
    manifest = copy.deepcopy(MANIFEST)
    manifest.update(overrides)
    return manifest


def test_runtime_boundaries_match_contract_order():
    assert BOUNDARY_ORDER == CONTRACT["boundaries"]["ordered"]


def test_default_view_projects_only_nodes_within_boundary_and_depth():
    projected = GlobalMeshBookRuntime(NODES, MANIFEST).project()
    assert [node["id"] for node in projected] == ["mesh.global", "mesh.qps"]


def test_wider_view_exposes_children_and_graph_edges():
    runtime = GlobalMeshBookRuntime(NODES, _manifest(boundary="ATOM", depth=5))
    projected = runtime.project()
    assert [node["id"] for node in projected] == [node["id"] for node in NODES]
    graph = runtime.to_graph(projected)
    edges = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    assert ("mesh.qps", "mesh.qps.codex") in edges
    assert ("mesh.qps.codex", "mesh.qps.codex.runtime") in edges


def test_execute_is_deterministic_and_binds_identity(tmp_path):
    first = GlobalMeshBookRuntime(NODES, MANIFEST).execute(tmp_path / "a")
    second = GlobalMeshBookRuntime(NODES, MANIFEST).execute(tmp_path / "b")
    assert first == second
    assert first["renderer_version"] == RENDERER_VERSION
    for required in CONTRACT["artifact_identity"]["required_receipt_fields"]:
        assert first[required]
    for name in ("book.md", "book.html", "graph.json", "render_receipt.json"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()


def test_identity_changes_with_view_manifest(tmp_path):
    base = GlobalMeshBookRuntime(NODES, MANIFEST).execute(tmp_path / "a")
    deeper = GlobalMeshBookRuntime(NODES, _manifest(depth=5)).execute(tmp_path / "b")
    assert base["source_sha256"] == deeper["source_sha256"]
    assert base["artifact_identity_sha256"] != deeper["artifact_identity_sha256"]


def test_projection_never_mutates_source_nodes(tmp_path):
    nodes = copy.deepcopy(NODES)
    GlobalMeshBookRuntime(nodes, _manifest(boundary="ATOM", depth=5)).execute(tmp_path)
    assert nodes == NODES


def test_html_escapes_node_content():
    nodes = [dict(NODES[0], title="<script>x</script>", content="a & b")]
    html_text = GlobalMeshBookRuntime(nodes, MANIFEST).to_html(nodes)
    assert "<script>x</script>" not in html_text
    assert "&lt;script&gt;x&lt;/script&gt;" in html_text
    assert "a &amp; b" in html_text


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        (_manifest(schema_version="other/1.0.0"), "unsupported view manifest schema"),
        (_manifest(boundary="PLANET"), "unknown boundary"),
        (_manifest(depth=6), "depth must be 0..5"),
    ],
)
def test_invalid_manifest_fails_closed(manifest, message):
    with pytest.raises(ValueError, match=message):
        GlobalMeshBookRuntime(NODES, manifest)


def test_invalid_nodes_fail_closed():
    with pytest.raises(ValueError, match="duplicate node id"):
        GlobalMeshBookRuntime([NODES[0], NODES[0]], MANIFEST)
    missing = {k: v for k, v in NODES[0].items() if k != "content"}
    with pytest.raises(ValueError, match="missing required field content"):
        GlobalMeshBookRuntime([missing], MANIFEST)
