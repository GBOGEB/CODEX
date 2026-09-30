#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "mission_control" / "mycelium" / "log_events.json"
OUTPUT = ROOT / "mission_control" / "mycelium" / "log_analysis.json"
PAGES_OUTPUT = ROOT / "docs" / "data" / "missioncontrol_log_analysis.json"


def analyze(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {
            "schema_version": "0.1",
            "status": "WITHHELD",
            "reason": "no governed log events ingested",
            "nodes": {},
            "first_red": None,
            "recurrences": [],
        }

    by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    fingerprints: Counter[str] = Counter()
    for event in events:
        node_id = str(event.get("node_id") or "UNBOUND")
        by_node[node_id].append(event)
        if event.get("fingerprint"):
            fingerprints[str(event["fingerprint"])] += 1

    node_summaries: dict[str, Any] = {}
    failures: list[dict[str, Any]] = []
    for node_id, rows in by_node.items():
        passed = sum(1 for r in rows if str(r.get("status")).upper() in {"PASS", "SUCCESS", "GREEN"})
        failed = sum(1 for r in rows if str(r.get("status")).upper() in {"FAIL", "FAILURE", "RED"})
        parsed = sum(1 for r in rows if r.get("parsed", True))
        node_summaries[node_id] = {
            "status": "MEASURED",
            "expected_required_logs": len(rows),
            "parsed_required_logs": parsed,
            "passed": passed,
            "failed": failed,
            "health_pct": round(100.0 * passed / len(rows), 2) if rows else None,
        }
        failures.extend(r for r in rows if str(r.get("status")).upper() in {"FAIL", "FAILURE", "RED"})

    failures.sort(key=lambda r: str(r.get("at") or ""))
    recurrence = [
        {"fingerprint": fp, "count": count}
        for fp, count in fingerprints.most_common()
        if count > 1
    ]
    return {
        "schema_version": "0.1",
        "status": "MEASURED",
        "nodes": node_summaries,
        "first_red": failures[0] if failures else None,
        "recurrences": recurrence,
    }


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    result = analyze(payload.get("events", []))
    text = json.dumps(result, indent=2, sort_keys=False) + "\n"
    OUTPUT.write_text(text, encoding="utf-8")
    PAGES_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PAGES_OUTPUT.write_text(text, encoding="utf-8")
    print(f"MissionControl log analysis: {result['status']}")


if __name__ == "__main__":
    main()
