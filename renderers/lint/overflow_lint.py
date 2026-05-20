from __future__ import annotations

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


if __name__ == '__main__':
    print('overflow governance lint scaffold active')
