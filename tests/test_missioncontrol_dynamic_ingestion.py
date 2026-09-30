import json
from pathlib import Path

import scripts.build_missioncontrol_graph as builder


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "missioncontrol_github_public_metadata.json"


def test_dynamic_graph_ingestion_is_deterministic(monkeypatch) -> None:
    monkeypatch.setenv("MISSIONCONTROL_NOW", "2026-09-30T10:00:00+00:00")
    graph = builder.build(fixture_path=FIXTURE)

    assert graph["ingestion"]["mode"] == "fixture"
    assert all(item["status"] == "FRESH" for item in graph["ingestion"]["source_results"])

    nodes = {node["id"]: node for node in graph["nodes"]}
    assert nodes["repo_codex"]["meta"]["sha"] == "cb60cc2e89767920528dd0a7cf0ddf5ea3d25a53"
    assert nodes["repo_abacus"]["meta"]["sha"] == "713a152e99024165aea81bffbf530d2073e164bb"
    assert nodes["gh_pr:GBOGEB/ABACUS:1491"]["meta"]["head_sha"] == "97ef46c4cecfd4c5f9d297d63125792e88576d5c"

    edge_pairs = {(edge["from"], edge["to"], edge["type"]) for edge in graph["edges"]}
    assert ("repo_abacus", "gh_pr:GBOGEB/ABACUS:1491", "contains") in edge_pairs


def test_write_graph_materializes_identical_views(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MISSIONCONTROL_NOW", "2026-09-30T10:00:00+00:00")
    graph = builder.build(fixture_path=FIXTURE)
    assert json.dumps(graph, sort_keys=True)
