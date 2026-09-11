#!/usr/bin/env python3
"""GLOB lookup CLI for the GBOGEB global hive.

GLOB is a read-only resolver. It does not schedule work or transfer authority.
Examples:
  python tools/glob_lookup.py --menu
  python tools/glob_lookup.py --action RED
  python tools/glob_lookup.py --status BG
  python tools/glob_lookup.py --node CODEX
  python tools/glob_lookup.py --lane governance
  python tools/glob_lookup.py --direction IN
  python tools/glob_lookup.py --ask "what can you do?"
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
    key = moniker.upper()
    record = taxonomy.get("action_monikers", {}).get(key)
    if not record:
        raise KeyError(f"Unknown action moniker: {moniker}")
    return {"kind": "action", "identity": key, **record}


def status_record(glob: dict[str, Any], key: str) -> dict[str, Any]:
    k = key.upper()
    meanings = resolve(ROOT, glob["authority"]["action_taxonomy"])["reserved_status_dimension_keys"]["meanings"]
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
        "ask_examples": [item["ask"] for item in glob["what_can_you_ask"]],
    }


def ask_record(glob: dict[str, Any], question: str) -> dict[str, Any]:
    normalized = " ".join(question.lower().split()).rstrip("?")
    if normalized in {"what can you do", "what can i ask", "help", "menu"}:
        return menu(glob)
    for item in glob.get("what_can_you_ask", []):
        target = " ".join(str(item.get("ask", "")).lower().split()).rstrip("?")
        if normalized == target:
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
        ("direction", "Direction"),
        ("global_state", "State"),
        ("local_ssot", "SSOT"),
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
