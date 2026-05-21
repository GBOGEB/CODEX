from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


@dataclass
class SpacingIssue:
    component: str
    severity: str
    message: str


MIN_CARD_PADDING = 12
MIN_SECTION_SPACING = 16


def validate_card_padding(padding_px: int) -> list[SpacingIssue]:
    issues: list[SpacingIssue] = []

    if padding_px < MIN_CARD_PADDING:
        issues.append(
            SpacingIssue(
                component='card-padding',
                severity='warning',
                message=f'card padding below {MIN_CARD_PADDING}px',
            )
        )

    return issues


def validate_section_spacing(spacing_px: int) -> list[SpacingIssue]:
    issues: list[SpacingIssue] = []

    if spacing_px < MIN_SECTION_SPACING:
        issues.append(
            SpacingIssue(
                component='section-spacing',
                severity='warning',
                message=f'section spacing below {MIN_SECTION_SPACING}px',
            )
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description='Run spacing governance lint checks.')
    parser.add_argument('--card-padding', type=int, default=MIN_CARD_PADDING)
    parser.add_argument('--section-spacing', type=int, default=MIN_SECTION_SPACING)
    args = parser.parse_args()

    issues = [
        *validate_card_padding(args.card_padding),
        *validate_section_spacing(args.section_spacing),
    ]
    if issues:
        for item in issues:
            print(f'[{item.severity}] {item.component}: {item.message}', file=sys.stderr)
        return 1

    print('[info] spacing governance checks passed', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
