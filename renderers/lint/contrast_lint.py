from __future__ import annotations

from dataclasses import dataclass

from src.renderers.theme_runtime import SemanticThemeRuntime


@dataclass
class ContrastIssue:
    component: str
    severity: str
    message: str


MIN_DARK_MODE_CONTRAST_RATIO = 7.0


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    hex_value = value.lstrip('#')
    return tuple(int(hex_value[index : index + 2], 16) / 255 for index in (0, 2, 4))


def _channel_luminance(channel: float) -> float:
    if channel <= 0.03928:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def _contrast_ratio(background: str, text: str) -> float:
    bg_channels = _hex_to_rgb(background)
    text_channels = _hex_to_rgb(text)
    bg_luminance = (
        0.2126 * _channel_luminance(bg_channels[0])
        + 0.7152 * _channel_luminance(bg_channels[1])
        + 0.0722 * _channel_luminance(bg_channels[2])
    )
    text_luminance = (
        0.2126 * _channel_luminance(text_channels[0])
        + 0.7152 * _channel_luminance(text_channels[1])
        + 0.0722 * _channel_luminance(text_channels[2])
    )
    lighter = max(bg_luminance, text_luminance)
    darker = min(bg_luminance, text_luminance)
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

    warning_theme = SemanticThemeRuntime().resolve('warning', 'dark')
    if warning_theme.background == warning_theme.text:
        issues.append(
            ContrastIssue(
                component='warning-card-dark-mode',
                severity='critical',
                message='Dark warning background and text colors must differ.',
            )
        )

    contrast_ratio = _contrast_ratio(warning_theme.background, warning_theme.text)
    if contrast_ratio < MIN_DARK_MODE_CONTRAST_RATIO:
        issues.append(
            ContrastIssue(
                component='warning-card-dark-mode',
                severity='critical',
                message=(
                    f'Dark warning contrast ratio {contrast_ratio:.2f} is below '
                    f'{MIN_DARK_MODE_CONTRAST_RATIO:.1f}:1.'
                ),
            )
        )

    return issues


if __name__ == '__main__':
    results = validate_warning_dark_mode()
    if results:
        for item in results:
            print(f'[{item.severity}] {item.component}: {item.message}')
    else:
        print('contrast governance checks passed')
