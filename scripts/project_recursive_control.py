"""Project measured Mycelium state back into current / mid / long control horizons.

This is the read-only half of the recursive control loop (KPI RCH-04): measured
outputs (the KPI report, the executable-value control observation and a pinned
federated convergence receipt) are ranked into derived priority horizons and
compared with the hand-maintained horizons in control_events.json. Nothing is
applied: control_events.json is never written, and bounded apply stays disabled.

The output is deterministic (no wall-clock timestamps), so it can be committed and checked:

    python scripts/project_recursive_control.py          # write the projection
    python scripts/project_recursive_control.py --check  # exit 1 if the committed projection is stale
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = Path("mission_control") / "mycelium"
KPI_REPORT = Path("docs") / "data" / "mycelium_kpi_measurement.json"
VALUE_OBSERVATION = MC / "executable_value_control_observation.json"
CONTROL_EVENTS = MC / "control_events.json"
APPLY_POLICY = MC / "bounded_apply_policy.yaml"
FEDERATED_INPUTS = MC / "recursive_control" / "federated_inputs.yaml"
OUTPUT = MC / "recursive_control_projection.json"
PAGES_OUTPUT = Path("docs") / "data" / "missioncontrol_recursive_control_projection.json"

HORIZONS = ("current", "mid", "long")
RULES = (
    {"id": "RC-01", "horizon": "current",
     "rule": "A federated cross-check that FAILs: evidence disagrees, so nothing downstream of it can be trusted."},
    {"id": "RC-02", "horizon": "current",
     "rule": "A local KPI cross-check that FAILs: two Mycelium producers disagree on the same fact."},
    {"id": "RC-03", "horizon": "current",
     "rule": "Federated repositories whose plateau is STARVED and that notify: no fresh comparable measurement exists."},
    {"id": "RC-04", "horizon": "mid",
     "rule": "The executable-value next control action, when it is not PRESERVE_CONTROL."},
    {"id": "RC-05", "horizon": "mid",
     "rule": "A RED KPI that names an unlock action."},
    {"id": "RC-06", "horizon": "long",
     "rule": "A RED KPI without an unlock action (the unlock still has to be designed)."},
    {"id": "RC-07", "horizon": "long",
     "rule": "An AMBER KPI that names an unlock action."},
)


class ProjectionError(Exception):
    """An input is missing, malformed or does not match its pin."""


def _fingerprint(path: Path) -> str:
    # Normalise CRLF so a Windows working copy fingerprints like CI.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load(path: Path) -> Any:
    if not path.is_file():
        raise ProjectionError(f"missing input: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)


def _require(mapping: Any, key: str, where: str) -> Any:
    if not isinstance(mapping, dict) or key not in mapping:
        raise ProjectionError(f"{where}: missing field {key!r}")
    return mapping[key]


def load_inputs(root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load every input; federated inputs only when their pinned digest matches."""
    data: dict[str, Any] = {}
    meta: list[dict[str, Any]] = []
    for alias, rel in (("kpi_report", KPI_REPORT), ("value_observation", VALUE_OBSERVATION),
                       ("control_events", CONTROL_EVENTS), ("apply_policy", APPLY_POLICY)):
        data[alias] = _load(root / rel)
        meta.append({"alias": alias, "origin": "LOCAL", "path": rel.as_posix(),
                     "sha256": _fingerprint(root / rel)})

    pins = _load(root / FEDERATED_INPUTS)
    for pin in _require(pins, "inputs", FEDERATED_INPUTS.as_posix()):
        local = root / _require(pin, "local_path", "federated pin")
        payload = _load(local)
        digest = _fingerprint(local)
        if digest != pin["sha256"]:
            raise ProjectionError(f"{pin['alias']}: sha256 {digest} does not match pin {pin['sha256']}")
        if payload.get("schema_version") != pin["expected_schema_version"] \
                or payload.get("programme") != pin["expected_programme"]:
            raise ProjectionError(f"{pin['alias']}: unexpected schema_version/programme")
        data[pin["alias"]] = payload
        meta.append({"alias": pin["alias"], "origin": "FEDERATED", "path": pin["local_path"],
                     "sha256": digest, "repository": pin["repository"], "revision": pin["revision"],
                     "source_path": pin["source_path"]})
    return data, meta


def _item(item_id: str, rule: str, lane: str, state: str, reason: str,
          sources: list[dict[str, str]], unlock: str | None = None) -> dict[str, Any]:
    item = {"id": item_id, "rule": rule, "lane": lane, "state": state, "reason": reason, "sources": sources}
    if unlock:
        item["unlock"] = unlock
    return item


def derive_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply RC-01..RC-07 in order. Every item cites the input and JSON pointer it came from."""
    items: list[dict[str, Any]] = []
    fed = data.get("hub_convergence")
    if fed is None:
        raise ProjectionError("federated input hub_convergence not loaded")

    for i, check in enumerate(_require(fed, "crosschecks", "hub_convergence")):
        if check.get("result") == "FAIL":
            items.append(_item(
                f"FEDERATED_{check['id'].upper()}", "RC-01", "FEDERATION", "EVIDENCE_CONFLICT",
                check["detail"], [{"input": "hub_convergence", "pointer": f"/crosschecks/{i}"}]))

    kpi = data["kpi_report"]
    for i, check in enumerate(_require(kpi, "checks", "kpi_report")):
        if check.get("status") == "FAIL":
            items.append(_item(
                f"KPI_CHECK_{check['id']}", "RC-02", "MYCELIUM_MEASUREMENT", "PRODUCER_DISAGREEMENT",
                check.get("reason") or check.get("name") or check["id"],
                [{"input": "kpi_report", "pointer": f"/checks/{i}"}]))

    starved = []
    for repo, receipt in sorted(_require(fed, "repos", "hub_convergence").items()):
        if receipt["plateau"]["state"] == "STARVED" and receipt["notify"]:
            starved.append(repo)
    if starved:
        items.append(_item(
            "FEDERATED_FRESH_MEASUREMENT", "RC-03", "FEDERATION", "STARVED",
            f"no fresh comparable measurement for {', '.join(starved)}; plateau cannot be derived",
            [{"input": "hub_convergence", "pointer": f"/repos/{repo}/plateau"} for repo in starved]))

    action = _require(data["value_observation"], "next_control_action", "value_observation")
    if action != "PRESERVE_CONTROL":
        items.append(_item(
            action, "RC-04", "MYCELIUM_EXECUTION", "QUEUED",
            f"{data['value_observation']['unregistered_asset_count']} unregistered assets, "
            f"{data['value_observation']['tested_orphan_count']} tested orphans",
            [{"input": "value_observation", "pointer": "/next_control_action"}]))

    kpis = {k["id"]: (i, k) for i, k in enumerate(_require(kpi, "kpis", "kpi_report"))}
    red = [k["id"] for k in _require(kpi, "red_kpis", "kpi_report")]
    unlocks = {k["id"]: k.get("unlock") for k in kpi["red_kpis"]}
    for rule, wanted in (("RC-05", True), ("RC-06", False)):
        for kpi_id in red:
            if bool(unlocks.get(kpi_id)) is wanted:
                i, k = kpis[kpi_id]
                items.append(_item(
                    f"KPI_{kpi_id}", rule, f"MYCELIUM_{k['dimension'].upper()}", "RED",
                    f"{k['name']}: {k['value']} against target {k['target']}",
                    [{"input": "kpi_report", "pointer": f"/kpis/{i}"}], unlocks.get(kpi_id)))
    for kpi_id, (i, k) in sorted(kpis.items()):
        unlock = k.get("unlock")
        if k.get("band") == "AMBER" and unlock:
            items.append(_item(
                f"KPI_{kpi_id}", "RC-07", f"MYCELIUM_{k['dimension'].upper()}", "AMBER",
                f"{k['name']}: {k['value']} against target {k['target']}",
                [{"input": "kpi_report", "pointer": f"/kpis/{i}"}], unlock))
    return items


def rank(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    horizon_of = {r["id"]: r["horizon"] for r in RULES}
    horizons: dict[str, list[dict[str, Any]]] = {h: [] for h in HORIZONS}
    for item in items:  # already in rule order, then source order
        horizons[horizon_of[item["rule"]]].append(item)
    for entries in horizons.values():
        for n, item in enumerate(entries, start=1):
            item["rank"] = n
    return horizons


def horizon_delta(derived: dict[str, list[dict[str, Any]]], events: dict[str, Any]) -> dict[str, Any]:
    manual = _require(events, "horizons", "control_events")
    manual_ids = {e["id"] for h in HORIZONS for e in manual.get(h, [])}
    derived_ids = {e["id"] for h in HORIZONS for e in derived[h]}
    return {
        "control_events_snapshot_at": events.get("snapshot_at"),
        "derived_only": sorted(derived_ids - manual_ids),
        "shared": sorted(derived_ids & manual_ids),
        # steering events are authoritative; the projection never drops them
        "manual_only_retained": sorted(manual_ids - derived_ids),
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    data, meta = load_inputs(root)
    horizons = rank(derive_items(data))
    mutation_enabled = bool(data["apply_policy"].get("mutation_enabled"))
    return {
        "schema_version": "0.1",
        "projection_id": "MYCELIUM_RECURSIVE_CONTROL_PROJECTION",
        "kpi": "RCH-04",
        "authority_class": "DERIVED_CONTROL_PROJECTION",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "mutation": False,
        "apply_state": "ENABLED_NOT_USED" if mutation_enabled else "WITHHELD_BOUNDED_APPLY_DISABLED",
        "control_events_written": False,
        "inputs": meta,
        "rules": list(RULES),
        "horizons": horizons,
        "delta_vs_control_events": horizon_delta(horizons, data["control_events"]),
        "summary": {h: len(horizons[h]) for h in HORIZONS},
    }


def render(projection: dict[str, Any]) -> str:
    return json.dumps(projection, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed projection is stale")
    args = parser.parse_args(argv)
    try:
        payload = render(build(ROOT))
    except ProjectionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    targets = (ROOT / OUTPUT, ROOT / PAGES_OUTPUT)
    if args.check:
        stale = [t.relative_to(ROOT).as_posix() for t in targets
                 if not t.is_file() or t.read_text(encoding="utf-8").replace("\r\n", "\n") != payload]
        if stale:
            print(f"STALE: {', '.join(stale)}; run `python scripts/project_recursive_control.py`", file=sys.stderr)
            return 1
        return 0
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8", newline="\n")
    projection = json.loads(payload)
    print("Recursive control projection: "
          + " / ".join(f"{h} {projection['summary'][h]}" for h in HORIZONS)
          + f" / {len(projection['delta_vs_control_events']['derived_only'])} derived-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
