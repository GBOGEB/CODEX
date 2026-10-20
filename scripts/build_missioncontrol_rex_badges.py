#!/usr/bin/env python3
"""Materialize the omnipresent REX badge projection for the Mycelium page.

Reads the REX observability contract (``ui`` section), the global REX ledger
and the MissionControl surfaces the page renders, and writes one canonical
JSON plus its Pages mirror. Matching is exact only: an item is SEEN_EXACT when
its text names a ledger ``rex_id`` or full ``signature``; otherwise the lookup
result is NEVER_SEEN. Similarity is not computed, so SEEN_SIMILAR is never
claimed. Missing ledger values are UNKNOWN, never zero.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
CONTRACT = MC / "rex_observability_contract.yaml"
LEDGER = ROOT / "federation" / "rex" / "GLOBAL_REX_LEDGER_v1.yaml"
CONTROL_PLANE = MC / "control_plane_projection.json"
CONTROL_EVENTS = MC / "control_events.json"
OUTPUT = MC / "rex_badges.json"
PAGES_OUTPUT = ROOT / "docs" / "data" / "missioncontrol_rex_badges.json"
LEDGER_URL = (
    "https://github.com/GBOGEB/CODEX/blob/main/federation/rex/GLOBAL_REX_LEDGER_v1.yaml"
)
UNKNOWN = "UNKNOWN"

# Page surfaces that exist in docs/missioncontrol_mycelium.html today.
RENDERED_SURFACES = ("active_atom", "blocker", "first_red")


def _known(value: Any) -> Any:
    if value is None or value == "" or value == []:
        return UNKNOWN
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    frequency = record.get("frequency") or {}
    count = frequency.get("observed_count")
    repair = record.get("repair_method")
    moniker = record.get("action_moniker")
    return {
        "rex_id": record["rex_id"],
        "signature": _known(record.get("signature")),
        "family": _known(record.get("family")),
        "seen_before": True,
        "recurrence_count": count if isinstance(count, int) else UNKNOWN,
        "recurrence_unit": _known(frequency.get("unit")),
        "recurrence_class": _known(record.get("recurrence")),
        "last_seen": _known(
            str(record["last_seen"]) if record.get("last_seen") is not None else None
        ),
        "prior_fix": _known(" · ".join(str(x).strip() for x in (moniker, repair) if x)),
        "control_guard": _known(record.get("control_guard")),
        "control_status": _known(record.get("control_status")),
        "rex_link": LEDGER_URL,
    }


def match_index(records: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    index: dict[str, dict[str, list[str]]] = {
        "signature": {},
        "family": {},
        "lookup_tag": {},
    }
    for record in records:
        rex_id = record["rex_id"]
        if record.get("signature"):
            index["signature"].setdefault(str(record["signature"]), []).append(rex_id)
        if record.get("family"):
            index["family"].setdefault(str(record["family"]), []).append(rex_id)
        for tag in record.get("lookup_tags") or []:
            index["lookup_tag"].setdefault(str(tag), []).append(rex_id)
    return {kind: dict(sorted(rows.items())) for kind, rows in index.items()}


def exact_matches(text: str, records: list[dict[str, Any]]) -> list[str]:
    haystack = text.casefold()
    hits = []
    for record in records:
        needles = [record["rex_id"], record.get("signature")]
        if any(n and str(n).casefold() in haystack for n in needles):
            hits.append(record["rex_id"])
    return hits


def badge(
    surface: str, item_id: str, texts: list[Any], records: list[dict[str, Any]]
) -> dict[str, Any]:
    text = " ".join(str(t) for t in texts if t)
    hits = exact_matches(text, records)
    return {
        "surface": surface,
        "item_id": item_id,
        "decision_hint": "SEEN_EXACT" if hits else "NEVER_SEEN",
        "rex_ids": hits,
        "basis": "exact rex_id or signature named by the item"
        if hits
        else "no ledger rex_id or signature named by the item; similarity not computed",
    }


def surface_items(
    control: dict[str, Any], events: dict[str, Any]
) -> list[tuple[str, str, list[Any]]]:
    items: list[tuple[str, str, list[Any]]] = []
    for lane in control.get("lanes", []):
        lane_id = str(lane.get("id"))
        if lane.get("current_atom"):
            items.append(("active_atom", lane_id, [lane.get("current_atom")]))
        if lane.get("blocker"):
            items.append(("blocker", lane_id, [lane.get("blocker")]))
    for event in events.get("events", []):
        if event.get("type") == "FIRST_RED":
            items.append(
                (
                    "first_red",
                    str(event.get("id")),
                    [event.get("summary"), event.get("content_ref")],
                )
            )
    return items


def build(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    control: dict[str, Any],
    events: dict[str, Any],
) -> dict[str, Any]:
    ui = contract.get("ui") or {}
    records = sorted(ledger.get("records") or [], key=lambda r: r["rex_id"])
    show_on = list(ui.get("show_on") or [])
    window = ledger.get("measurement_window") or {}
    badges = [badge(*item, records) for item in surface_items(control, events)]
    return {
        "schema_version": "0.1",
        "contract": "missioncontrol-rex-observability/1.0",
        "omnipresent_badge": ui.get("omnipresent_badge") is True,
        "compact_fields": list(ui.get("compact_fields") or []),
        "ledger": {
            "path": str(LEDGER.relative_to(ROOT)),
            "schema": _known(ledger.get("schema")),
            "measurement_window": _known(window.get("label")),
            "measured_on": _known(window.get("date")),
            "record_count": len(records),
        },
        "surfaces": {
            "rendered": [s for s in show_on if s in RENDERED_SURFACES],
            "not_on_this_page": [s for s in show_on if s not in RENDERED_SURFACES],
        },
        "similarity": "NOT_COMPUTED",
        "records": {r["rex_id"]: compact_record(r) for r in records},
        "match_index": match_index(records),
        "badges": badges,
        "authority_transfer": False,
    }


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    payload = build(
        _load_yaml(CONTRACT),
        _load_yaml(LEDGER),
        _load_json(CONTROL_PLANE),
        _load_json(CONTROL_EVENTS),
    )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    for path in (OUTPUT, PAGES_OUTPUT):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    seen = sum(1 for b in payload["badges"] if b["decision_hint"] != "NEVER_SEEN")
    print(
        f"MissionControl REX badges: {len(payload['badges'])} items, {seen} seen before"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
