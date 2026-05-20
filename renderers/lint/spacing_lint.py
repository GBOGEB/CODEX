from __future__ import annotations

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


if __name__ == '__main__':
    print('spacing governance lint scaffold active')
