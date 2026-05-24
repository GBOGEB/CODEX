from __future__ import annotations


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {hex_color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _to_linear(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    r_lin = _to_linear(r / 255.0)
    g_lin = _to_linear(g / 255.0)
    b_lin = _to_linear(b / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


class ContrastValidator:
    """Validates contrast ratios for semantic theme nodes against WCAG AA thresholds."""

    def __init__(self) -> None:
        self.target_invariants = {
            "warning": {
                "dark": {
                    "background": "#7c2d12",
                    "text": "#fef3c7",
                }
            }
        }

    def validate_theme_node(self, background: str, text: str) -> dict[str, float | bool]:
        l1 = _relative_luminance(background)
        l2 = _relative_luminance(text)
        lightest, darkest = max(l1, l2), min(l1, l2)
        contrast_ratio = round((lightest + 0.05) / (darkest + 0.05), 2)
        return {
            "contrast_ratio": contrast_ratio,
            "wcag_aa_compliant": contrast_ratio >= 4.5,
        }
