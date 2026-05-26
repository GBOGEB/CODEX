"""Extract simple theme counts from INCUBATOR tuple records."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.parse_chat_tuple import load_tuple_documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path for extracted theme counts.",
    )
    return parser.parse_args()


def extract_theme_counts() -> dict[str, int]:
    counts = Counter()
    for item in load_tuple_documents():
        counts[item["theme"]] += 1
    return dict(sorted(counts.items()))


def main() -> int:
    counts = extract_theme_counts()
    payload = json.dumps(counts, indent=2)
    args = parse_args()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
