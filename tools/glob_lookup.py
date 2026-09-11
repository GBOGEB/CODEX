#!/usr/bin/env python3
"""GLOB lookup CLI for the GBOGEB global hive.

GLOB is a read-only resolver. It does not schedule work or transfer authority.
It also exposes DMAIC-Control Return of Experience (REX) lookup.

Examples:
  python tools/glob_lookup.py --menu
  python tools/glob_lookup.py --action RED
  python tools/glob_lookup.py --status BG
  python tools/glob_lookup.py --node CODEX
  python tools/glob_lookup.py --lane governance
  python tools/glob_lookup.py --direction IN
  python tools/glob_lookup.py --rex REX-W112-006
  python tools/glob_lookup.py --rex-repo cryoplant-project
  python tools/glob_lookup.py --ask "show recurring failures"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GLOB_PATH = ROOT / "GLOB.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_glob() -> dict[str, Any]:
    return load_yaml(GLOB_PATH)


def resolve(root: Path, rel: str) -> dict[str, Any]:
    return load_yaml(root / rel)


def action_record(glob: dict[str, Any], moniker: str) -> dict[str, Any]:
    taxonomy = resolve(ROOT, glob["authority"]["action_taxonomy"])
    where_used = resolve(ROOT, glob["authority"]["action_where_used"])
    key = moniker.upper()
    record = taxonomy.get("action_monikers", {}).get(key)
    if not record:
        raise KeyError(f"Unknown action moniker: {moniker}")
    usage = where_used.get("records", {}).get(key, {})
    return {
        "kind": "action",
        "identity": key,
        **record,
        "first_use_case": usage.get("first_use_case", "See action where-used registry"),
    }


def status_record(glob: dict[str, Any], key: str) -> dict[str, Any]:
    k = key.upper()
    meanings = resolve(ROOT, glob["authority"]["action_taxonomy"])[
        "reserved_status_dimension_keys"
    ]["meanings"]
    if k not in meanings:
        raise KeyError(f"Unknown status dimension: {key}")
    return {
        "kind": "status",
        "identity": k,
        "title": meanings[k],
        "purpose": "Scheduler-facing mesh state dimension",
        "authority": glob["authority"]["status_contract"],
        "first_use_case": "Inspect current mesh state without selecting a task action.",
    }


def node_record(glob: dict[str, Any], query: str) -> dict[str, Any]:
    census = resolve(ROOT, glob["authority"]["global_census"])
    needle = query.lower()
    for node in census.get("nodes", []):
        hay = " ".join(str(node.get(k, "")) for k in ("id", "repo", "role")).lower()
        if needle in hay:
            return {
                "kind": "node",
                "identity": node.get("id", node.get("repo")),
                "title": node.get("repo"),
                "purpose": node.get("role"),
                "authority": node.get("authority", "See local mesh dock/SSOT"),
                "first_use_case": node.get("first_mesh_use_case", "See global census"),
                "global_state": node.get("global_state"),
                "local_ssot": node.get("local_ssot") or node.get("local_ssot_locators"),
            }
    raise KeyError(f"No node matching: {query}")


def lane_record(glob: dict[str, Any], lane: str) -> dict[str, Any]:
    key = lane.lower()
    record = glob.get("lanes", {}).get(key)
    if not record:
        raise KeyError(f"Unknown lane: {lane}")
    return {
        "kind": "lane",
        "identity": key,
        "title": f"{key.title()} lane",
        "purpose": "Global hive lane view",
        "authority": "Authority remains with referenced node/domain owners",
        "first_use_case": f"Filter the hive to {key} work and its directly connected context.",
        **record,
    }


def direction_record(glob: dict[str, Any], direction: str) -> dict[str, Any]:
    key = direction.upper()
    record = glob.get("colour_schedule", {}).get(key)
    if not record:
        raise KeyError(f"Unknown direction: {direction}")
    return {
        "kind": "direction",
        "identity": key,
        "title": key,
        "purpose": record.get("meaning"),
        "authority": "Transport/navigation semantic only; no authority transfer",
        "first_use_case": f"Filter graph edges by {key} direction.",
        **record,
    }


def _rex_repo_names(record: dict[str, Any]) -> list[str]:
    repo = record.get("repo", {})
    if isinstance(repo, str):
        return [repo]
    names: list[str] = []
    if isinstance(repo, dict):
        primary = repo.get("primary")
        if primary:
            names.append(str(primary))
        impacted = repo.get("impacted", [])
        if isinstance(impacted, list):
            names.extend(str(item) for item in impacted)
    return list(dict.fromkeys(names))


def _rex_count(record: dict[str, Any]) -> int:
    frequency = record.get("frequency", {})
    if not isinstance(frequency, dict):
        return 0
    try:
        return int(frequency.get("observed_count", 0))
    except (TypeError, ValueError):
        return 0


def _rex_stars(value: int) -> str:
    value = max(1, min(5, int(value)))
    return "★" * value + "☆" * (5 - value)


def load_rex_records(glob: dict[str, Any]) -> list[dict[str, Any]]:
    ledger = resolve(ROOT, glob["authority"]["rex_ledger"])
    records = ledger.get("records", [])
    return [record for record in records if isinstance(record, dict)]


def rex_record(glob: dict[str, Any], rex_id: str) -> dict[str, Any]:
    for record in load_rex_records(glob):
        if str(record.get("rex_id", "")).upper() == rex_id.upper():
            return {
                "kind": "rex",
                "identity": record.get("rex_id"),
                "title": record.get("signature"),
                "purpose": record.get("symptom"),
                "authority": record.get(
                    "authority_boundary",
                    "REX experience only; source/domain authority remains unchanged",
                ),
                "first_use_case": record.get("lesson"),
                "repo": _rex_repo_names(record),
                "severity_stars": record.get("severity_stars"),
                "severity_glyph": _rex_stars(int(record.get("severity_stars", 1))),
                "observed_count": _rex_count(record),
                "recurrence": record.get("recurrence"),
                "family": record.get("family"),
                "issue_kind": record.get("issue_kind"),
                "action_moniker": record.get("action_moniker"),
                "control_status": record.get("control_status"),
                "repair_method": record.get("repair_method"),
                "verification": record.get("verification"),
                "lesson": record.get("lesson"),
            }
    raise KeyError(f"Unknown REX id: {rex_id}")


def rex_group(
    glob: dict[str, Any],
    *,
    repo: str | None = None,
    recurring: bool = False,
    severity_stars: int | None = None,
    min_impacted_repo_count: int | None = None,
    control_status: str | list[str] | None = None,
    query: str | None = None,
    sort: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    records = load_rex_records(glob)
    if repo:
        needle = repo.lower()
        records = [
            record
            for record in records
            if any(needle in name.lower() for name in _rex_repo_names(record))
        ]
    if recurring:
        records = [record for record in records if record.get("recurrence") != "UNIQUE"]
    if severity_stars is not None:
        records = [
            record for record in records if int(record.get("severity_stars", 0)) == severity_stars
        ]
    if min_impacted_repo_count is not None:
        records = [
            record
            for record in records
            if int(record.get("frequency", {}).get("impacted_repo_count", 0))
            >= min_impacted_repo_count
        ]
    if control_status:
        allowed = {control_status} if isinstance(control_status, str) else set(control_status)
        allowed_upper = {str(value).upper() for value in allowed}
        records = [
            record
            for record in records
            if str(record.get("control_status", "")).upper() in allowed_upper
        ]
    if query:
        needle = query.lower()
        records = [
            record
            for record in records
            if needle in json.dumps(record, ensure_ascii=False, sort_keys=True).lower()
        ]
    if sort == "observed_count_desc":
        records.sort(key=_rex_count, reverse=True)
    else:
        records.sort(
            key=lambda record: (int(record.get("severity_stars", 0)), _rex_count(record)),
            reverse=True,
        )
    records = records[: max(0, limit)]
    compact = [
        {
            "rex_id": record.get("rex_id"),
            "repo": _rex_repo_names(record),
            "severity": _rex_stars(int(record.get("severity_stars", 1))),
            "count": _rex_count(record),
            "recurrence": record.get("recurrence"),
            "family": record.get("family"),
            "status": record.get("control_status"),
            "action": record.get("action_moniker"),
            "signature": record.get("signature"),
        }
        for record in records
    ]
    return {
        "kind": "rex_group",
        "identity": "REX",
        "title": "DMAIC Control Return of Experience",
        "purpose": "Reusable measured error/failure/problem experience",
        "authority": "Lookup/control signal only; no engineering authority transfer",
        "first_use_case": "Recognize recurrence before repeating a known failure path.",
        "record_count": len(compact),
        "records": compact,
    }


def menu(glob: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "menu",
        "identity": "GLOB",
        "title": glob["name"],
        "purpose": glob["purpose"],
        "authority": glob["authority"]["global_index_owner"],
        "first_use_case": glob["first_use_case"],
        "actions": glob["action_namespace"]["monikers"],
        "views": list(glob["navigation"]["views"]),
        "rex": glob.get("rex_namespace"),
        "ask_examples": [item["ask"] for item in glob["what_can_you_ask"]],
    }


def ask_record(glob: dict[str, Any], question: str) -> dict[str, Any]:
    normalized = " ".join(question.lower().split()).rstrip("?")
    if normalized in {"what can you do", "what can i ask", "help", "menu"}:
        return menu(glob)
    for item in glob.get("what_can_you_ask", []):
        target = " ".join(str(item.get("ask", "")).lower().split()).rstrip("?")
        if normalized != target:
            continue
        if item.get("resolves_to") == "rex_snippet":
            return rex_group(
                glob,
                repo=item.get("repo"),
                recurring=bool(item.get("recurring", False)),
                severity_stars=item.get("severity_stars"),
                min_impacted_repo_count=item.get("min_impacted_repo_count"),
                control_status=item.get("control_status"),
                query=item.get("query"),
                sort=item.get("sort"),
            )
        if item.get("moniker"):
            return action_record(glob, item["moniker"])
        if item.get("filter") in glob.get("colour_schedule", {}):
            return direction_record(glob, item["filter"])
        if item.get("inspect"):
            return {
                "kind": "status_group",
                "identity": "+".join(item["inspect"]),
                "title": item["ask"],
                "purpose": "Inspect status dimensions together",
                "authority": glob["authority"]["status_contract"],
                "first_use_case": "Answer the requested state question without inventing an action.",
                "status": [status_record(glob, key) for key in item["inspect"]],
            }
    upper = question.strip().upper()
    if upper in glob["action_namespace"]["monikers"]:
        return action_record(glob, upper)
    if upper in glob["status_namespace"]["reserved_keys"]:
        return status_record(glob, upper)
    if upper.startswith("REX-"):
        return rex_record(glob, upper)
    raise KeyError(f"No direct GLOB resolver for question: {question}")


def compact_lines(record: dict[str, Any], max_lines: int = 12) -> list[str]:
    preferred = [
        ("kind", "Kind"),
        ("title", "Title"),
        ("identity", "ID"),
        ("purpose", "Purpose"),
        ("authority", "Authority"),
        ("default_band", "Band"),
        ("inspects_status", "Status"),
        ("severity_glyph", "Severity"),
        ("observed_count", "Count"),
        ("recurrence", "Recurrence"),
        ("control_status", "Control"),
        ("action_moniker", "Action"),
        ("direction", "Direction"),
        ("global_state", "State"),
        ("local_ssot", "SSOT"),
        ("records", "Records"),
        ("first_use_case", "First use"),
        ("ask_examples", "Ask"),
    ]
    lines: list[str] = []
    for key, label in preferred:
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        text = " ".join(str(value).split())
        lines.append(f"{label}: {text}")
        if len(lines) >= max_lines:
            break
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only GLOB hive lookup")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--menu", action="store_true")
    group.add_argument("--action")
    group.add_argument("--status")
    group.add_argument("--node")
    group.add_argument("--lane")
    group.add_argument("--direction")
    group.add_argument("--rex")
    group.add_argument("--rex-repo")
    group.add_argument("--ask")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    glob = load_glob()
    try:
        if args.action:
            record = action_record(glob, args.action)
        elif args.status:
            record = status_record(glob, args.status)
        elif args.node:
            record = node_record(glob, args.node)
        elif args.lane:
            record = lane_record(glob, args.lane)
        elif args.direction:
            record = direction_record(glob, args.direction)
        elif args.rex:
            record = rex_record(glob, args.rex)
        elif args.rex_repo:
            record = rex_group(glob, repo=args.rex_repo)
        elif args.ask:
            record = ask_record(glob, args.ask)
        else:
            record = menu(glob)
    except KeyError as exc:
        print(str(exc))
        return 2

    if args.as_json:
        print(json.dumps(record, indent=2, ensure_ascii=False, default=str))
    else:
        max_lines = int(glob.get("popup_snippet_contract", {}).get("max_lines", 12))
        print("\n".join(compact_lines(record, max_lines=max_lines)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
