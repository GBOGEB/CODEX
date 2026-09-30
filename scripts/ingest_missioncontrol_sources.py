from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
DOCS_DATA = ROOT / "docs" / "data"
REGISTRY = MC / "source_registry.yaml"
CACHE = MC / "source_status.json"
PAGES = DOCS_DATA / "missioncontrol_source_status.json"
EVENTS = MC / "control_events.json"
PAGES_EVENTS = DOCS_DATA / "missioncontrol_control_events.json"


def now_iso() -> str:
    forced = os.environ.get("MISSIONCONTROL_NOW")
    return forced or datetime.now(UTC).isoformat()


def github_get(path: str, token: str | None) -> Any:
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MissionControl-Mycelium",
            "X-GitHub-Api-Version": "2022-11-28",
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


def _payload(
    source: dict[str, Any],
    kind: str,
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
    if kind == "pulls":
        return github_get(
            f"/repos/{repo}/pulls?state=all&per_page=30&sort=updated&direction=desc",
            token,
        )
    if kind == "issues":
        return github_get(
            f"/repos/{repo}/issues?state=open&per_page=30&sort=updated&direction=desc",
            token,
        )
    if kind == "workflows":
        return github_get(f"/repos/{repo}/actions/runs?per_page=30", token)
    raise ValueError(f"unsupported ingest kind: {kind}")


def collect_source(
    source: dict[str, Any],
    *,
    token: str | None,
    fixture_dir: Path | None,
) -> dict[str, Any]:
    sid = source["id"]
    repo = source["repository"]
    observed_at = now_iso()
    result: dict[str, Any] = {
        "id": sid,
        "repository": repo,
        "authority_class": source["authority_class"],
        "role": source["role"],
        "status": "FRESH",
        "observed_at": observed_at,
        "data": {},
        "telemetry_errors": {},
    }

    # Repository metadata establishes source readability. Exact head identity is
    # measured independently so an unavailable head probe is explicit and
    # non-fatal rather than poisoning otherwise readable repository metadata.
    try:
        repo_meta = _payload(
            source, "repository", token=token, fixture_dir=fixture_dir
        )
        result["data"]["repository"] = repo_meta
        default_branch = repo_meta.get("default_branch") or "main"
        result["default_branch"] = default_branch
        result["head_ref"] = default_branch
        result["pushed_at"] = repo_meta.get("pushed_at")
        result["open_issue_count"] = repo_meta.get("open_issues_count")
    except (
        OSError,
        urllib.error.URLError,
        json.JSONDecodeError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        result["status"] = "ERROR"
        result["identity_status"] = "WITHHELD_REPOSITORY_UNREADABLE"
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    try:
        if fixture_dir:
            head_path = fixture_dir / f"{sid}_head.json"
            if not head_path.exists():
                result["identity_status"] = "WITHHELD_FIXTURE_HEAD_MISSING"
                head = None
            else:
                head = fixture_get(fixture_dir, sid, "head")
        else:
            head = github_get(f"/repos/{repo}/commits/{default_branch}", token)

        if head is not None:
            head_sha = head.get("sha")
            if head_sha:
                result["head_sha"] = head_sha
                result["identity_status"] = "MEASURED"
                result["head_url"] = head.get("html_url") or (
                    f"https://github.com/{repo}/commit/{head_sha}"
                )
            else:
                result["identity_status"] = "WITHHELD_HEAD_SHA_MISSING"
    except (
        OSError,
        urllib.error.URLError,
        json.JSONDecodeError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        result["identity_status"] = "WITHHELD_HEAD_PROBE_ERROR"
        result["identity_error"] = f"{type(exc).__name__}: {exc}"

    for kind in source.get("ingest", []):
        if kind == "repository":
            continue
        try:
            result["data"][kind] = _payload(
                source, kind, token=token, fixture_dir=fixture_dir
            )
        except (
            OSError,
            urllib.error.URLError,
            json.JSONDecodeError,
            FileNotFoundError,
            ValueError,
        ) as exc:
            result["telemetry_errors"][kind] = f"{type(exc).__name__}: {exc}"

    pulls = result["data"].get("pulls") or []
    issues = result["data"].get("issues") or []
    workflows = (result["data"].get("workflows") or {}).get("workflow_runs", [])
    result["telemetry_status"] = (
        "PARTIAL" if result["telemetry_errors"] else "COMPLETE"
    )
    result["topology"] = {
        "pulls_observed": len(pulls) if isinstance(pulls, list) else 0,
        "open_pulls": sum(
            1
            for item in pulls
            if isinstance(item, dict) and item.get("state") == "open"
        )
        if isinstance(pulls, list)
        else 0,
        "open_issues_observed": sum(
            1
            for item in issues
            if isinstance(item, dict)
            and "pull_request" not in item
            and item.get("state") == "open"
        )
        if isinstance(issues, list)
        else 0,
        "workflow_runs_observed": len(workflows)
        if isinstance(workflows, list)
        else 0,
    }
    return result


def recover_stale(
    current: list[dict[str, Any]], previous: dict[str, Any] | None
) -> list[dict[str, Any]]:
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


def build(
    *, fixture_dir: Path | None = None, token: str | None = None
) -> dict[str, Any]:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    previous = (
        json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else None
    )
    collected = [
        collect_source(source, token=token, fixture_dir=fixture_dir)
        for source in registry.get("sources", [])
    ]
    sources = recover_stale(collected, previous)
    return {
        "schema_version": "0.2",
        "generated_at": now_iso(),
        "public_metadata_only": True,
        "authority_transfer": False,
        "engineering_state_promoted": False,
        "sources": sources,
    }


def temporal_refresh_events(
    previous: dict[str, Any] | None,
    current: dict[str, Any],
    events: dict[str, Any],
) -> dict[str, Any]:
    old = {
        item["id"]: item
        for item in (previous or {}).get("sources", [])
    }
    out = json.loads(json.dumps(events))
    event_list = out.setdefault("events", [])
    parent = event_list[-1]["id"] if event_list else None
    next_number = 1
    if event_list:
        try:
            next_number = max(int(str(x["id"]).split("-")[-1]) for x in event_list) + 1
        except (KeyError, ValueError):
            next_number = len(event_list) + 1

    for source in current.get("sources", []):
        before = old.get(source["id"], {})
        after_sha = source.get("head_sha")
        before_sha = before.get("head_sha")
        before_identity = before.get("identity_status")
        after_identity = source.get("identity_status")
        if before_identity is None and before.get("status") == "MEASURED_CHAT_CONNECTOR" and before_sha:
            before_identity = "MEASURED"
        if after_identity is None and source.get("status") == "MEASURED_CHAT_CONNECTOR" and after_sha:
            after_identity = "MEASURED"
        status_changed = source.get("status") != before.get("status")
        head_changed = after_sha != before_sha
        identity_changed = after_identity != before_identity
        if not (head_changed or status_changed or identity_changed):
            continue
        event_id = f"EV-{next_number:04d}"
        next_number += 1
        summary = (
            f"Federation source {source['repository']} refreshed: "
            f"{before_sha or 'UNBOUND'} -> {after_sha or 'UNAVAILABLE'}; "
            f"status {before.get('status', 'UNBOUND')} -> {source.get('status')}; "
            f"identity {before_identity or 'UNBOUND'} -> {after_identity or 'WITHHELD'}."
        )
        event = {
            "id": event_id,
            "at": current["generated_at"],
            "type": "EXTERNAL_RETURN"
            if source.get("authority_class") == "REMOTE_AUTHORITATIVE"
            else "RECOVERY",
            "node_id": f"repo_{source['id']}",
            "source_repo": source["repository"],
            "source_ref": source.get("default_branch") or "UNBOUND",
            "source_sha": after_sha,
            "identity_status_before": before_identity,
            "identity_status_after": after_identity,
            "parent_event": parent,
            "content_ref": "mission_control/mycelium/source_status.json",
            "summary": summary,
            "acceptance_decision": "PROJECTION_ONLY_NO_ACCEPTANCE",
            "projection_only": True,
            "authority_transfer": False,
        }
        event_list.append(event)
        parent = event_id

    return out


def write_payload(
    payload: dict[str, Any],
    *,
    emit_events: bool,
    previous: dict[str, Any] | None,
) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    CACHE.write_text(text, encoding="utf-8")
    PAGES.parent.mkdir(parents=True, exist_ok=True)
    PAGES.write_text(text, encoding="utf-8")

    if emit_events:
        events = json.loads(EVENTS.read_text(encoding="utf-8"))
        updated = temporal_refresh_events(previous, payload, events)
        event_text = json.dumps(updated, indent=2) + "\n"
        EVENTS.write_text(event_text, encoding="utf-8")
        PAGES_EVENTS.write_text(event_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument(
        "--emit-events",
        action="store_true",
        help="Append projection-only source head/status changes to control_events.json.",
    )
    args = parser.parse_args()
    previous = (
        json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else None
    )
    payload = build(
        fixture_dir=args.fixture_dir,
        token=os.environ.get("GITHUB_TOKEN"),
    )
    write_payload(payload, emit_events=args.emit_events, previous=previous)
    states = ", ".join(
        f"{x['id']}={x['status']}@{str(x.get('head_sha') or 'unbound')[:12]}"
        for x in payload["sources"]
    )
    print(f"MissionControl source ingestion: {states}")


if __name__ == "__main__":
    main()
