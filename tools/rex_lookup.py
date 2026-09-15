#!/usr/bin/env python3
"""Read-only GLOB/REX lookup for DMAIC Control-phase experience.

Examples:
  python tools/rex_lookup.py --repo GBOGEB/cryoplant-project
  python tools/rex_lookup.py --stars 5
  python tools/rex_lookup.py --recurring
  python tools/rex_lookup.py --family RUNTIME
  python tools/rex_lookup.py --status DEFERRED
  python tools/rex_lookup.py --top 5
  python tools/rex_lookup.py --id REX-W112-006
  python tools/rex_lookup.py --query semantic_readiness

This tool reads the governed REX taxonomy/ledger only. It does not mutate
issues, rerun workflows, schedule work, or confer engineering authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "federation" / "rex" / "GLOBAL_REX_LEDGER_v1.yaml"
TAXONOMY = ROOT / "federation" / "rex" / "GLOBAL_REX_TAXONOMY_v1.yaml"


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return value


def load_records() -> list[dict[str, Any]]:
    ledger = _load(LEDGER)
    records = ledger.get("records", [])
    if not isinstance(records, list):
        raise ValueError("REX ledger records must be a list")
    return [record for record in records if isinstance(record, dict)]


def severity_glyph(stars: int) -> str:
    stars = max(1, min(5, int(stars)))
    return "★" * stars + "☆" * (5 - stars)


def repo_names(record: dict[str, Any]) -> list[str]:
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


def observed_count(record: dict[str, Any]) -> int:
    frequency = record.get("frequency", {})
    if not isinstance(frequency, dict):
        return 0
    try:
        return int(frequency.get("observed_count", 0))
    except (TypeError, ValueError):
        return 0


def searchable_text(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True).lower()


def filter_records(
    records: list[dict[str, Any]],
    *,
    repo: str | None = None,
    stars: int | None = None,
    recurring: bool = False,
    family: str | None = None,
    status: str | None = None,
    action: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    result = records
    if repo:
        needle = repo.lower()
        result = [r for r in result if any(needle in name.lower() for name in repo_names(r))]
    if stars is not None:
        result = [r for r in result if int(r.get("severity_stars", 0)) == stars]
    if recurring:
        result = [r for r in result if str(r.get("recurrence", "UNKNOWN")) != "UNIQUE"]
    if family:
        result = [r for r in result if str(r.get("family", "")).upper() == family.upper()]
    if status:
        result = [r for r in result if str(r.get("control_status", "")).upper() == status.upper()]
    if action:
        result = [r for r in result if str(r.get("action_moniker", "")).upper() == action.upper()]
    if query:
        needle = query.lower()
        result = [r for r in result if needle in searchable_text(r)]
    return result


def rank_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda r: (int(r.get("severity_stars", 0)), observed_count(r)),
        reverse=True,
    )


def compact(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "rex_id": record.get("rex_id"),
        "repo": repo_names(record),
        "severity": severity_glyph(int(record.get("severity_stars", 1))),
        "observed_count": observed_count(record),
        "recurrence": record.get("recurrence"),
        "family": record.get("family"),
        "issue_kind": record.get("issue_kind"),
        "action": record.get("action_moniker"),
        "control_status": record.get("control_status"),
        "signature": record.get("signature"),
        "symptom": record.get("symptom"),
        "lesson": record.get("lesson"),
    }


def print_table(records: list[dict[str, Any]]) -> None:
    if not records:
        print("No matching REX records.")
        return
    headers = ["REX", "Repo", "Stars", "Count", "Recurrence", "Family", "Status", "Action"]
    rows: list[list[str]] = []
    for record in records:
        repos = repo_names(record)
        primary = repos[0] if repos else "-"
        rows.append([
            str(record.get("rex_id", "-")),
            primary.replace("GBOGEB/", ""),
            severity_glyph(int(record.get("severity_stars", 1))),
            str(observed_count(record)),
            str(record.get("recurrence", "UNKNOWN")),
            str(record.get("family", "-")),
            str(record.get("control_status", "-")),
            str(record.get("action_moniker", "-")),
        ])
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(row))))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GLOB REX Control-phase lookup")
    p.add_argument("--repo")
    p.add_argument("--stars", type=int, choices=range(1, 6))
    p.add_argument("--recurring", action="store_true")
    p.add_argument("--family")
    p.add_argument("--status")
    p.add_argument("--action")
    p.add_argument("--query")
    p.add_argument("--id")
    p.add_argument("--top", type=int)
    p.add_argument("--json", action="store_true", dest="as_json")
    return p


def main() -> int:
    args = parser().parse_args()
    records = load_records()
    if args.id:
        records = [r for r in records if r.get("rex_id") == args.id]
    records = filter_records(
        records,
        repo=args.repo,
        stars=args.stars,
        recurring=args.recurring,
        family=args.family,
        status=args.status,
        action=args.action,
        query=args.query,
    )
    records = rank_records(records)
    if args.top is not None:
        records = records[: max(0, args.top)]
    if args.as_json:
        print(json.dumps([compact(record) for record in records], indent=2, ensure_ascii=False))
    else:
        print_table(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
