#!/usr/bin/env python3
"""Build MissionControl Mycelium graph from governed public GitHub metadata.

Live mode reads only public repository metadata from GitHub.  Offline mode reads
an endpoint-keyed JSON fixture and is used for deterministic CI tests.

The builder does not promote remote engineering truth.  It updates repository
identity, exact head SHA and open pull-request topology only.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "mission_control" / "mycelium" / "sources.json"
GRAPH = ROOT / "mission_control" / "mycelium" / "interaction_graph.json"
PAGES_GRAPH = ROOT / "docs" / "data" / "missioncontrol_interaction_graph.json"
API_ROOT = "https://api.github.com"


def _now() -> str:
    forced = os.environ.get("MISSIONCONTROL_NOW")
    if forced:
        return forced
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class SourceClient:
    def __init__(self, fixture: dict[str, Any] | None = None) -> None:
        self.fixture = fixture
        self.token = os.environ.get("GITHUB_TOKEN")

    def get(self, endpoint: str) -> Any:
        if self.fixture is not None:
            if endpoint not in self.fixture:
                raise KeyError(f"fixture missing endpoint: {endpoint}")
            return self.fixture[endpoint]

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GBOGEB-CODEX-MissionControl",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(API_ROOT + endpoint, headers=headers)
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))


def _upsert(nodes: list[dict[str, Any]], node: dict[str, Any]) -> None:
    for index, current in enumerate(nodes):
        if current.get("id") == node["id"]:
            merged = dict(current)
            merged.update(node)
            old_meta = current.get("meta") or {}
            new_meta = node.get("meta") or {}
            merged["meta"] = {**old_meta, **new_meta}
            nodes[index] = merged
            return
    nodes.append(node)


def _replace_ingested_prs(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    repo_node_id: str,
    repository: str,
    pulls: list[dict[str, Any]],
) -> None:
    prefix = f"gh_pr:{repository}:"
    removed = {n["id"] for n in nodes if str(n.get("id", "")).startswith(prefix)}
    nodes[:] = [n for n in nodes if n.get("id") not in removed]
    edges[:] = [e for e in edges if e.get("from") not in removed and e.get("to") not in removed]

    for pr in pulls:
        number = pr["number"]
        node_id = f"{prefix}{number}"
        head = (pr.get("head") or {}).get("sha")
        _upsert(nodes, {
            "id": node_id,
            "type": "pull_request",
            "label": f"{repository} #{number} {pr.get('title', '')}".strip(),
            "state": str(pr.get("state", "open")).upper(),
            "url": pr.get("html_url"),
            "ingest_source": repository,
            "meta": {
                "number": number,
                "head_sha": head,
                "draft": bool(pr.get("draft", False)),
                "updated_at": pr.get("updated_at"),
            },
        })
        edges.append({"from": repo_node_id, "to": node_id, "type": "contains"})


def build(*, fixture_path: Path | None = None) -> dict[str, Any]:
    config = _load_json(SOURCES)
    graph = _load_json(GRAPH)
    fixture = _load_json(fixture_path) if fixture_path else None
    client = SourceClient(fixture)

    nodes = graph.setdefault("nodes", [])
    edges = graph.setdefault("edges", [])
    graph["snapshot_at"] = _now()
    graph["ingestion"] = {
        "mode": "fixture" if fixture_path else "github_public_api",
        "public_metadata_only": True,
        "authority_transfer": False,
        "source_results": [],
    }

    for source in config["sources"]:
        repository = source["repository"]
        repo_node_id = source["node_id"]
        repo_endpoint = f"/repos/{repository}"
        try:
            repo = client.get(repo_endpoint)
            default_branch = repo.get("default_branch") or "main"
            commit = client.get(f"/repos/{repository}/commits/{default_branch}")
            limit = int(source.get("max_open_prs", 12))
            pulls = client.get(f"/repos/{repository}/pulls?state=open&per_page={limit}")
            sha = commit.get("sha")
            if not sha:
                raise ValueError(f"{repository}: missing exact head SHA")

            _upsert(nodes, {
                "id": repo_node_id,
                "type": "repo",
                "label": repository,
                "state": source["authority_class"],
                "url": repo.get("html_url") or f"https://github.com/{repository}",
                "ingest_source": repository,
                "meta": {
                    "sha": sha,
                    "default_branch": default_branch,
                    "pushed_at": repo.get("pushed_at"),
                    "authority_class": source["authority_class"],
                    "role": source["role"],
                    "ingested_at": graph["snapshot_at"],
                },
            })
            _replace_ingested_prs(nodes, edges, repo_node_id, repository, pulls)
            graph["ingestion"]["source_results"].append({
                "repository": repository,
                "status": "FRESH",
                "head_sha": sha,
                "open_prs_ingested": len(pulls),
            })
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            existing = next((n for n in nodes if n.get("id") == repo_node_id), None)
            if existing:
                existing["state"] = f"{source['authority_class']}_STALE_SOURCE"
                existing.setdefault("meta", {})["ingestion_error"] = str(exc)
                existing["meta"]["last_ingestion_attempt"] = graph["snapshot_at"]
            graph["ingestion"]["source_results"].append({
                "repository": repository,
                "status": "STALE_SOURCE",
                "error": str(exc),
            })

    return graph


def write_graph(graph: dict[str, Any]) -> None:
    text = json.dumps(graph, indent=2) + "\n"
    GRAPH.write_text(text, encoding="utf-8")
    PAGES_GRAPH.parent.mkdir(parents=True, exist_ok=True)
    PAGES_GRAPH.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    built = build(fixture_path=args.fixture)
    if args.check:
        current = _load_json(GRAPH)
        if built != current:
            raise SystemExit("MissionControl graph is stale relative to configured source input")
        print("MissionControl dynamic graph check: PASS")
        return
    write_graph(built)
    print(json.dumps(built["ingestion"], indent=2))


if __name__ == "__main__":
    main()
