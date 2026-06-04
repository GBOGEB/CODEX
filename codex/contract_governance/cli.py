"""CLI for building and validating ABACUS governance artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import build_artifacts
from .io import load_ssot
from .validator import validate_generated


def main() -> int:
    parser = argparse.ArgumentParser(prog="contract-governance")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Generate internal and bidder artifacts")
    build.add_argument("--ssot", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="Validate generated artifacts")
    validate.add_argument("--ssot", type=Path, required=True)
    validate.add_argument("--out", type=Path, required=True)
    validate.add_argument("--tier", choices=["internal", "bidder"], action="append")

    args = parser.parse_args()
    ssot = load_ssot(args.ssot)
    if args.command == "build":
        for tier in ("internal", "bidder"):
            result = build_artifacts(ssot, args.out, tier)  # type: ignore[arg-type]
            print(f"built {tier}: {result['content_hash']}")
        return 0
    if args.command == "validate":
        for tier in args.tier or ["internal", "bidder"]:
            validate_generated(ssot, args.out, tier)  # type: ignore[arg-type]
            print(f"validated {tier}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
