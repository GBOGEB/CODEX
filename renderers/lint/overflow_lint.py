from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


@dataclass
class OverflowIssue:
    component: str
    severity: str
    message: str


MAX_TITLE_LENGTH = 72
MAX_CARD_BODY_LINES = 18


def validate_title_length(title: str) -> list[OverflowIssue]:
    issues: list[OverflowIssue] = []

    if len(title) > MAX_TITLE_LENGTH:
        issues.append(
            OverflowIssue(
                component='title-overflow',
                severity='warning',
                message=f'title length exceeds {MAX_TITLE_LENGTH} characters',
            )
        )

    return issues


def validate_card_body_lines(lines: int) -> list[OverflowIssue]:
    issues: list[OverflowIssue] = []

    if lines > MAX_CARD_BODY_LINES:
        issues.append(
            OverflowIssue(
                component='card-overflow',
                severity='warning',
                message=f'card body exceeds {MAX_CARD_BODY_LINES} lines',
            )
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description='Run overflow governance lint checks.')
    parser.add_argument('--title', type=str, default='')
    parser.add_argument('--card-body-lines', type=int, default=0)
    args = parser.parse_args()

    issues = [
        *validate_title_length(args.title),
        *validate_card_body_lines(args.card_body_lines),
    ]
    if issues:
        for item in issues:
            print(f'[{item.severity}] {item.component}: {item.message}', file=sys.stderr)
        return 1

    print('[info] overflow governance checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
