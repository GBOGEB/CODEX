"""INCUBATOR → ABACUS RTM ingress bridge (W002 activation).

Reads validated tuples from ``outputs/incubator_export/``, maps their
``dmaic_phase`` field against the DMAIC phase schema defined in
``maps/dmaic_phase_map.yml``, and writes a traceability summary to
``docs/rtm/incubator_rtm_bridge.md``.

Usage::

    python scripts/bridge_rtm_ingress.py
    python scripts/bridge_rtm_ingress.py --export-dir outputs/incubator_export --out docs/rtm/incubator_rtm_bridge.md
    python scripts/bridge_rtm_ingress.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── Defaults ───────────────────────────────────────────────────────────────

DEFAULT_EXPORT_DIR = REPO_ROOT / "outputs" / "incubator_export"
DEFAULT_PHASE_MAP = REPO_ROOT / "maps" / "dmaic_phase_map.yml"
DEFAULT_OUT = REPO_ROOT / "docs" / "rtm" / "incubator_rtm_bridge.md"

# DMAIC phases in canonical order
DMAIC_PHASES = ("Define", "Measure", "Analyze", "Improve", "Control")


# ── Helpers ────────────────────────────────────────────────────────────────

def load_phase_map(path: Path) -> dict[str, str]:
    """Load the theme → DMAIC phase mapping from ``maps/dmaic_phase_map.yml``."""
    if not path.exists():
        raise FileNotFoundError(f"DMAIC phase map not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("theme_to_dmaic_phase", {})


def collect_tuples(
    export_dir: Path,
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Return ``(tuples, failures)`` from ``export_dir``.

    *tuples* — successfully parsed dicts with ``_source_file`` injected.
    *failures* — list of ``(relative_path, error_message)`` for files that
    could not be read or parsed.
    """
    tuples: list[dict[str, Any]] = []
    failures: list[tuple[str, str]] = []
    if not export_dir.exists():
        return tuples, failures
    for yml_file in sorted(export_dir.rglob("*.yml")):
        try:
            with yml_file.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            if isinstance(data, dict):
                data["_source_file"] = str(yml_file.relative_to(REPO_ROOT))
                tuples.append(data)
        except Exception as exc:  # noqa: BLE001 — tolerate malformed files
            rel = str(yml_file.relative_to(export_dir))
            failures.append((rel, str(exc)))
            print(f"WARNING: skipped {rel}: {exc}", file=sys.stderr)
    return tuples, failures


def validate_dmaic_phase(
    tuple_data: dict[str, Any],
    phase_map: dict[str, str],
) -> tuple[str, str]:
    """Return (resolved_phase, status) for a single tuple.

    Status values: ``"mapped"``, ``"direct"``, ``"unknown"``.
    """
    raw_phase: str = (tuple_data.get("dmaic_phase") or "").strip()
    theme: str = (tuple_data.get("theme") or "").strip()

    # Direct match against canonical phase names
    if raw_phase in DMAIC_PHASES:
        return raw_phase, "direct"

    # Lookup via theme → phase map
    if theme in phase_map:
        return phase_map[theme], "mapped"

    # Fallback: look up raw_phase in map
    if raw_phase in phase_map:
        return phase_map[raw_phase], "mapped"

    return raw_phase or "UNKNOWN", "unknown"


def render_report(
    tuples: list[dict[str, Any]],
    phase_map: dict[str, str],
    failures: list[tuple[str, str]] | None = None,
) -> str:
    """Render a Markdown traceability bridge report."""
    failures = failures or []
    lines: list[str] = [
        "# INCUBATOR → ABACUS RTM Bridge Report",
        "",
        "**Source:** `outputs/incubator_export/`  ",
        "**Phase map:** `maps/dmaic_phase_map.yml`  ",
        f"**Tuples processed:** {len(tuples)}",
        *(
            [f"**Parse failures:** {len(failures)}  ⚠️"]
            if failures
            else []
        ),
        "",
        "## Phase Distribution",
        "",
    ]

    # Tally
    phase_counts: dict[str, int] = {p: 0 for p in DMAIC_PHASES}
    unknown_count = 0
    rows: list[tuple[str, str, str, str]] = []

    for t in tuples:
        tid = t.get("tuple_id") or t.get("id") or t.get("_source_file", "(unknown)")
        theme = t.get("theme", "")
        resolved, status = validate_dmaic_phase(t, phase_map)
        if resolved in phase_counts:
            phase_counts[resolved] += 1
        else:
            unknown_count += 1
        rows.append((str(tid), theme, resolved, status))

    for phase, count in phase_counts.items():
        lines.append(f"- **{phase}**: {count}")
    if unknown_count:
        lines.append(f"- **UNKNOWN / unmapped**: {unknown_count}")

    lines += [
        "",
        "## Tuple Traceability",
        "",
        "| Tuple ID | Theme | Resolved Phase | Status |",
        "|---|---|---|---|",
    ]
    for tid, theme, phase, status in rows:
        lines.append(f"| `{tid}` | {theme} | {phase} | {status} |")

    if not rows:
        lines.append("| *(no tuples found in export directory)* | — | — | — |")

    lines += [
        "",
        "## W002 Activation Status",
        "",
        "- [x] Phase map loaded from `maps/dmaic_phase_map.yml`",
        f"- {'[x]' if tuples else '[ ]'} Tuples found in `outputs/incubator_export/`",
        "- [ ] Full DMAIC validation against ABACUS phase schema (pending W002 completion)",
    ]

    if failures:
        lines += [
            "",
            "## Parse Failures",
            "",
            "The following files could not be read or parsed:",
            "",
        ]
        for rel_path, err_msg in failures:
            lines.append(f"- `{rel_path}`: {err_msg}")

    lines += [
        "",
        "_Generated by `scripts/bridge_rtm_ingress.py`_",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="INCUBATOR → ABACUS RTM ingress bridge")
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Path to incubator_export directory (default: outputs/incubator_export/)",
    )
    parser.add_argument(
        "--phase-map",
        type=Path,
        default=DEFAULT_PHASE_MAP,
        help="Path to dmaic_phase_map.yml (default: maps/dmaic_phase_map.yml)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output Markdown path (default: docs/rtm/incubator_rtm_bridge.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report to stdout without writing to disk.",
    )
    args = parser.parse_args(argv)

    phase_map = load_phase_map(args.phase_map)
    tuples, failures = collect_tuples(args.export_dir)

    report = render_report(tuples, phase_map, failures)

    if args.dry_run:
        print(report)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote RTM bridge report → {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
