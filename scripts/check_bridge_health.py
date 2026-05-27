#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.bridge_adapter import BRIDGE_COMPONENT_PATHS, build_bridge_report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate CODEX/ABACUS bridge relevance and pipeline coverage."
    )
    parser.add_argument(
        "--component",
        choices=sorted(BRIDGE_COMPONENT_PATHS),
        default="codex",
        help="Bridge component to validate.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path to write the JSON validation report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = build_bridge_report(component=args.component)
    serialized = json.dumps(report, indent=2, sort_keys=True)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized + "\n", encoding="utf-8")

    print(serialized)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
