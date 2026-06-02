"""Validate that every YAML session tuple in incubator/ resolves to a DMAIC phase.

Usage:
    python scripts/validate_dmaic_phase_map.py [--incubator-dir PATH] [--phase-map PATH]

Exit codes:
    0 — all tuples resolved to a DMAIC phase (or incubator dir is empty)
    1 — one or more tuples could not be resolved, or required files are missing
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INCUBATOR_DIR = REPO_ROOT / "incubator"
DEFAULT_PHASE_MAP = REPO_ROOT / "maps" / "dmaic_phase_map.yml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _build_routing_index(phase_map: dict) -> dict[str, str]:
    """Return mapping of (category, theme) and fallback keys to DMAIC phase names."""
    index: dict[str, str] = {}
    phases = phase_map.get("dmaic_phases", {})
    for phase_name, phase_cfg in phases.items():
        for cat in phase_cfg.get("incubator_categories", []):
            for theme in phase_cfg.get("incubator_themes", []):
                index[(cat, theme)] = phase_name
        for cat in phase_cfg.get("incubator_categories", []):
            index.setdefault(("__cat__", cat), phase_name)
        for theme in phase_cfg.get("incubator_themes", []):
            index.setdefault(("__theme__", theme), phase_name)

    default_rule = phase_map.get("routing_rules", [])
    default_phase = None
    for rule in default_rule:
        if rule.get("action") == "assign_default_phase":
            default_phase = rule.get("default_phase")
    index["__default__"] = default_phase or "DEFINE"
    return index


def resolve_phase(category: str, theme: str, index: dict[str, str]) -> str:
    """Resolve a (category, theme) pair to a DMAIC phase using priority routing."""
    if (category, theme) in index:
        return index[(category, theme)]
    if ("__cat__", category) in index:
        return index[("__cat__", category)]
    if ("__theme__", theme) in index:
        return index[("__theme__", theme)]
    return index["__default__"]


def validate(
    incubator_dir: Path = DEFAULT_INCUBATOR_DIR,
    phase_map_path: Path = DEFAULT_PHASE_MAP,
    report_json: Path | None = None,
) -> int:
    if not phase_map_path.exists():
        print(f"FAIL: phase map not found: {phase_map_path}", file=sys.stderr)
        return 1

    phase_map = _load_yaml(phase_map_path)
    allowed_phases = set(phase_map.get("validation", {}).get("allowed_phases", []))
    if not allowed_phases:
        allowed_phases = set(phase_map.get("dmaic_phases", {}).keys())

    index = _build_routing_index(phase_map)

    tuple_files = sorted(incubator_dir.glob("*.yml")) + sorted(incubator_dir.glob("*.yaml"))
    schema_files = {"session_tuple_schema.yml", "session_tuple_schema.yaml"}
    tuple_files = [f for f in tuple_files if f.name not in schema_files]

    if not tuple_files:
        print(f"INFO: no session tuples found in {incubator_dir} — nothing to validate")
        if report_json is not None:
            report_json.parent.mkdir(parents=True, exist_ok=True)
            report_json.write_text(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "no-tuples",
                        "claimed_percent": 100,
                        "actual_percent": 100,
                        "convergence_delta": 0,
                        "totals": {
                            "tuples_total": 0,
                            "resolved_total": 0,
                            "unresolved_total": 0,
                        },
                        "results": [],
                        "errors": [],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        return 0

    errors: list[str] = []
    results: list[tuple[str, str, str, str]] = []

    for path in tuple_files:
        try:
            data = _load_yaml(path)
        except Exception as exc:
            errors.append(f"{path.name}: YAML parse error — {exc}")
            continue

        category = data.get("category", "")
        theme = data.get("theme", "")
        missing = [f for f in ("category", "theme") if not data.get(f)]
        if missing:
            errors.append(f"{path.name}: missing required fields: {missing}")
            continue

        phase = resolve_phase(category, theme, index)
        if allowed_phases and phase not in allowed_phases:
            errors.append(
                f"{path.name}: resolved to unknown phase '{phase}' "
                f"(allowed: {sorted(allowed_phases)})"
            )
            continue

        results.append((path.name, category, theme, phase))

    for name, cat, theme, phase in results:
        print(f"  OK  {name}: {cat}/{theme} → {phase}")

    tuples_total = len(tuple_files)
    resolved_total = len(results)
    unresolved_total = len(errors)
    claimed_percent = 100
    actual_percent = round((resolved_total / tuples_total) * 100, 2) if tuples_total else 100
    convergence_delta = round(actual_percent - claimed_percent, 2)

    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "failed" if errors else "passed",
                    "claimed_percent": claimed_percent,
                    "actual_percent": actual_percent,
                    "convergence_delta": convergence_delta,
                    "totals": {
                        "tuples_total": tuples_total,
                        "resolved_total": resolved_total,
                        "unresolved_total": unresolved_total,
                    },
                    "results": [
                        {
                            "file": name,
                            "category": cat,
                            "theme": theme,
                            "phase": phase,
                        }
                        for name, cat, theme, phase in results
                    ],
                    "errors": errors,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Wrote DMAIC phase evidence report → {report_json}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"PASS: {len(results)} tuple(s) resolved to DMAIC phases")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate INCUBATOR session tuples resolve to DMAIC phases."
    )
    parser.add_argument(
        "--incubator-dir",
        type=Path,
        default=DEFAULT_INCUBATOR_DIR,
        help="Directory containing session tuple YAML files.",
    )
    parser.add_argument(
        "--phase-map",
        type=Path,
        default=DEFAULT_PHASE_MAP,
        help="Path to maps/dmaic_phase_map.yml.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional output path for JSON claim-vs-actual DMAIC evidence report.",
    )
    args = parser.parse_args(argv)
    return validate(args.incubator_dir, args.phase_map, args.report_json)


if __name__ == "__main__":
    raise SystemExit(main())
