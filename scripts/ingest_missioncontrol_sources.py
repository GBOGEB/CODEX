#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
DOCS = ROOT / "docs" / "data"
REGISTRY = MC / "source_registry.yaml"
CACHE = MC / "source_status.json"
PAGES = DOCS / "missioncontrol_source_status.json"
EVENTS = MC / "federation_events.json"
PAGES_EVENTS = DOCS / "missioncontrol_federation_events.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _payload_for_kind(
    kind: str,
    source: dict[str, Any],
    result: dict[str, Any],
    *,
    token: str | None,
    fixture_dir: Path | None,
) -> Any:
    sid = source["id"]
    repo = source["repository"]
    if fixture_dir:
        return fixture_get(fixture_dir, sid, kind)
    if kind == "repository":
        return github_get(f"/repos/{repo}", token)
    if kind == "head":
        branch = source.get("branch") or result.get("default_branch") or "main"
        return github_get(f"/repos/{repo}/branches/{urllib.parse.quote(str(branch), safe='')}", token)
    if kind == "pulls":
        return github_get(f"/repos/{repo}/pulls?state=all&per_page=30&sort=updated&direction=desc", token)
    if kind == "issues":
        return github_get(f"/repos/{repo}/issues?state=open&per_page=30&sort=updated&direction=desc", token)
    if kind == "workflows":
        return github_get(f"/repos/{repo}/actions/runs?per_page=30", token)
    raise ValueError(f"unsupported ingest kind: {kind}")


def collect_source(
    source: dict[str, Any],
    *,
    token: str | None,
    fixture_dir: Path | None,
    observed_at: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": source["id"],
        "repository": source["repository"],
        "authority_class": source["authority_class"],
        "role": source["role"],
        "branch": source.get("branch", "main"),
        "freshness_minutes": int(source.get("freshness_minutes", 60)),
        "status": "FRESH",
        "freshness_status": "FRESH",
        "observed_at": observed_at,
        "data": {},
    }
    try:
        for kind in source.get("ingest", []):
            payload = _payload_for_kind(
                kind, source, result, token=token, fixture_dir=fixture_dir
            )
            result["data"][kind] = payload
            if kind == "repository":
                result["default_branch"] = payload.get("default_branch")
                if not source.get("branch") and payload.get("default_branch"):
                    result["branch"] = payload["default_branch"]

        repo_meta = result["data"].get("repository", {})
        head_meta = result["data"].get("head", {})
        result["pushed_at"] = repo_meta.get("pushed_at")
        result["open_issue_count"] = repo_meta.get("open_issues_count")
        result["head_sha"] = (head_meta.get("commit") or {}).get("sha")
        result["head_url"] = (head_meta.get("commit") or {}).get("html_url")
        if "head" in source.get("ingest", []) and not result["head_sha"]:
            raise ValueError(f"head SHA missing for {source['repository']}:{result['branch']}")
    except (
        OSError,
        urllib.error.URLError,
        json.JSONDecodeError,
        ValueError,
        KeyError,
    ) as exc:
        result["status"] = "ERROR"
        result["freshness_status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def recover_stale(
    current: list[dict[str, Any]], previous: dict[str, Any] | None
) -> list[dict[str, Any]]:
    if not previous:
        return current
    old = {x["id"]: x for x in previous.get("sources", [])}
    recovered: list[dict[str, Any]] = []
    for item in current:
        if item.get("status") != "ERROR" or item["id"] not in old:
            recovered.append(item)
            continue
        fallback = dict(old[item["id"]])
        fallback["status"] = "STALE_CACHE"
        fallback["freshness_status"] = "STALE"
        fallback["stale_reason"] = item.get("error")
        fallback["refresh_attempted_at"] = item.get("observed_at")
        fallback["freshness_minutes"] = item.get(
            "freshness_minutes", fallback.get("freshness_minutes", 60)
        )
        recovered.append(fallback)
    return recovered


def _next_event_number(existing: list[dict[str, Any]]) -> int:
    found = []
    for event in existing:
        raw = str(event.get("id", ""))
        if raw.startswith("FE-") and raw[3:].isdigit():
            found.append(int(raw[3:]))
    return max(found, default=0) + 1


def derive_federation_events(
    *,
    sources: list[dict[str, Any]],
    previous: dict[str, Any] | None,
    existing: dict[str, Any] | None,
    observed_at: str,
) -> dict[str, Any]:
    old_sources = {
        row["id"]: row for row in (previous or {}).get("sources", [])
    }
    events = list((existing or {}).get("events", []))
    next_number = _next_event_number(events)

    for source in sources:
        prior = old_sources.get(source["id"], {})
        prior_sha = prior.get("head_sha")
        current_sha = source.get("head_sha")
        status = source.get("status")

        if status in {"ERROR", "STALE_CACHE"}:
            event_type = "FEDERATION_REFRESH_DEGRADED"
        elif current_sha and not prior_sha:
            event_type = "FEDERATION_HEAD_BOUND"
        elif current_sha and prior_sha and current_sha != prior_sha:
            event_type = "FEDERATION_HEAD_ADVANCED"
        else:
            event_type = "FEDERATION_REFRESH_CONFIRMED"

        events.append(
            {
                "id": f"FE-{next_number:06d}",
                "at": observed_at,
                "type": event_type,
                "source_id": source["id"],
                "source_repo": source["repository"],
                "source_ref": source.get("branch") or source.get("default_branch"),
                "source_sha": current_sha,
                "previous_sha": prior_sha,
                "authority_class": source.get("authority_class"),
                "status": status,
                "freshness_status": source.get("freshness_status"),
                "authority_transfer": False,
            }
        )
        next_number += 1

    return {
        "schema_version": "0.1",
        "append_only": True,
        "authority": "PUBLIC_METADATA_OBSERVATION_ONLY",
        "generated_at": observed_at,
        "events": events,
    }


def build(
    *,
    fixture_dir: Path | None = None,
    token: str | None = None,
    observed_at: str | None = None,
    previous: dict[str, Any] | None = None,
    existing_events: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    observed_at = observed_at or now_iso()
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    if previous is None and CACHE.exists():
        previous = json.loads(CACHE.read_text(encoding="utf-8"))
    if existing_events is None and EVENTS.exists():
        existing_events = json.loads(EVENTS.read_text(encoding="utf-8"))

    collected = [
        collect_source(
            source,
            token=token,
            fixture_dir=fixture_dir,
            observed_at=observed_at,
        )
        for source in registry.get("sources", [])
    ]
    sources = recover_stale(collected, previous)
    snapshot = {
        "schema_version": "0.2",
        "generated_at": observed_at,
        "public_metadata_only": True,
        "authority_transfer": False,
        "sources": sources,
    }
    temporal = derive_federation_events(
        sources=sources,
        previous=previous,
        existing=existing_events,
        observed_at=observed_at,
    )
    return snapshot, temporal


def _write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--observed-at")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write read-only live probe outputs outside the repository.",
    )
    args = parser.parse_args()

    snapshot, temporal = build(
        fixture_dir=args.fixture_dir,
        token=os.environ.get("GITHUB_TOKEN"),
        observed_at=args.observed_at,
    )

    if args.output_dir:
        _write_payload(args.output_dir / "source_status.json", snapshot)
        _write_payload(args.output_dir / "federation_events.json", temporal)
    else:
        _write_payload(CACHE, snapshot)
        _write_payload(PAGES, snapshot)
        _write_payload(EVENTS, temporal)
        _write_payload(PAGES_EVENTS, temporal)

    states = ", ".join(
        f"{x['id']}={x['status']}@{str(x.get('head_sha') or 'NO_HEAD')[:12]}"
        for x in snapshot["sources"]
    )
    print(f"MissionControl live federation ingestion: {states}")


if __name__ == "__main__":
    main()
