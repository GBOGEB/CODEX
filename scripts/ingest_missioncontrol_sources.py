#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "mission_control" / "mycelium" / "source_registry.yaml"
CACHE = ROOT / "mission_control" / "mycelium" / "source_status.json"
PAGES = ROOT / "docs" / "data" / "missioncontrol_source_status.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def github_get(path: str, token: str | None) -> Any:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MissionControl-Mycelium",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read())


def fixture_get(fixture_dir: Path, source_id: str, kind: str) -> Any:
    path = fixture_dir / f"{source_id}_{kind}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def collect_source(source: dict[str, Any], *, token: str | None, fixture_dir: Path | None) -> dict[str, Any]:
    sid = source["id"]
    repo = source["repository"]
    result: dict[str, Any] = {
        "id": sid,
        "repository": repo,
        "authority_class": source["authority_class"],
        "role": source["role"],
        "status": "FRESH",
        "observed_at": now_iso(),
        "data": {},
    }
    try:
        for kind in source.get("ingest", []):
            if fixture_dir:
                payload = fixture_get(fixture_dir, sid, kind)
            else:
                if kind == "repository":
                    payload = github_get(f"/repos/{repo}", token)
                elif kind == "pulls":
                    payload = github_get(f"/repos/{repo}/pulls?state=all&per_page=30&sort=updated&direction=desc", token)
                elif kind == "issues":
                    payload = github_get(f"/repos/{repo}/issues?state=open&per_page=30&sort=updated&direction=desc", token)
                elif kind == "workflows":
                    payload = github_get(f"/repos/{repo}/actions/runs?per_page=30", token)
                else:
                    continue
            result["data"][kind] = payload
        repo_meta = result["data"].get("repository", {})
        result["default_branch"] = repo_meta.get("default_branch")
        result["pushed_at"] = repo_meta.get("pushed_at")
        result["open_issue_count"] = repo_meta.get("open_issues_count")
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        result["status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def recover_stale(current: list[dict[str, Any]], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not previous:
        return current
    old = {x["id"]: x for x in previous.get("sources", [])}
    recovered = []
    for item in current:
        if item.get("status") != "ERROR" or item["id"] not in old:
            recovered.append(item)
            continue
        fallback = dict(old[item["id"]])
        fallback["status"] = "STALE_CACHE"
        fallback["stale_reason"] = item.get("error")
        fallback["refresh_attempted_at"] = item.get("observed_at")
        recovered.append(fallback)
    return recovered


def build(*, fixture_dir: Path | None = None, token: str | None = None) -> dict[str, Any]:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    previous = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else None
    collected = [
        collect_source(source, token=token, fixture_dir=fixture_dir)
        for source in registry.get("sources", [])
    ]
    sources = recover_stale(collected, previous)
    return {
        "schema_version": "0.1",
        "generated_at": now_iso(),
        "public_metadata_only": True,
        "authority_transfer": False,
        "sources": sources,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    args = parser.parse_args()
    payload = build(fixture_dir=args.fixture_dir, token=os.environ.get("GITHUB_TOKEN"))
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    CACHE.write_text(text, encoding="utf-8")
    PAGES.parent.mkdir(parents=True, exist_ok=True)
    PAGES.write_text(text, encoding="utf-8")
    states = ", ".join(f"{x['id']}={x['status']}" for x in payload["sources"])
    print(f"MissionControl source ingestion: {states}")


if __name__ == "__main__":
    main()
