from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContrastIssue:
    component: str
    severity: str
    message: str


DARK_WARNING_BACKGROUND = '#3B2A00'
DARK_WARNING_TEXT = '#FFE9A3'
MINIMUM_WCAG_CONTRAST = 4.5


def _normalize_hex(value: str) -> str:
    if not value.startswith('#'):
        raise ValueError(f"Unsupported hex color '{value}'")
    if len(value) == 4:
        return '#' + ''.join(ch * 2 for ch in value[1:])
    if len(value) == 7:
        return value
    if len(value) == 9:
        raise ValueError(
            f"8-digit hex (RGBA) not supported for contrast calculation: '{value}'. "
            'Use 6-digit hex (RGB) only.'
        )
    raise ValueError(f"Unsupported hex color '{value}'")


def _contrast_ratio(a: str, b: str) -> float:
    def _hex_to_rgb(value: str) -> tuple[float, float, float]:
        rgb = _normalize_hex(value)[1:]
        return int(rgb[0:2], 16) / 255, int(rgb[2:4], 16) / 255, int(rgb[4:6], 16) / 255

    def _linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    def _luminance(hex_color: str) -> float:
        red, green, blue = _hex_to_rgb(hex_color)
        return 0.2126 * _linear(red) + 0.7152 * _linear(green) + 0.0722 * _linear(blue)

    lighter = max(_luminance(a), _luminance(b))
    darker = min(_luminance(a), _luminance(b))
    return (lighter + 0.05) / (darker + 0.05)


def validate_warning_dark_mode() -> list[ContrastIssue]:
    """Basic semantic-theme governance validation scaffold.

    Future implementation should:
    - calculate WCAG contrast ratios
    - validate runtime semantic transforms
    - validate PDF-export visibility
    - validate snapshot readability
    """

    issues: list[ContrastIssue] = []
    try:
        ratio = _contrast_ratio(DARK_WARNING_BACKGROUND, DARK_WARNING_TEXT)
    except ValueError as exc:
        issues.append(
            ContrastIssue(
                component='warning-card-dark-mode',
                severity='critical',
                message=f'Contrast input invalid: {exc}',
            )
        )
        return issues

    if ratio < MINIMUM_WCAG_CONTRAST:
        issues.append(
            ContrastIssue(
                component='warning-card-dark-mode',
                severity='critical',
                message=(
                    f'Contrast ratio {ratio:.2f} is below WCAG minimum '
                    f'{MINIMUM_WCAG_CONTRAST:.1f}.'
                ),
            )
        )

    return issues


def main() -> int:
    """Run contrast lint checks and return process exit code (0 pass, 1 fail)."""
    results = validate_warning_dark_mode()
    if results:
        for item in results:
            print(f'[{item.severity}] {item.component}: {item.message}')
        return 1

    print('contrast governance checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
