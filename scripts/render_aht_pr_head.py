"""Render a validated exact-head snapshot into a preserved PR body, offline."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qps_aht_control import update_pr_body, validate_snapshot  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--now", required=True)
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.snapshot.read_text())
    validate_snapshot(payload, repository=args.repository, head_sha=args.head_sha,
                      expected_digest=args.sha256, now=args.now)
    args.output.write_text(update_pr_body(args.body.read_text(), payload), encoding="utf-8")


if __name__ == "__main__":
    main()
