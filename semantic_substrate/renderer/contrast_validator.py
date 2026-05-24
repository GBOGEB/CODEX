from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


@lru_cache(maxsize=1)
def _load_warning_dark_invariant() -> dict[str, str]:
    repo_root = Path(__file__).resolve().parent.parent.parent
    theme_path = repo_root / "themes" / "semantic_cards.yaml"
    with theme_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {theme_path}")
    semantic_cards = data.get("semantic_cards", {})
    warning_dark = semantic_cards.get("warning", {}).get("dark", {})
    return {
        "background": warning_dark["background"],
        "text": warning_dark["text"],
    }

class ContrastValidator:
    """
    G5 Hardened WCAG 2.1 Luminance and Relative Contrast Ratio Validation Engine.
    Enforces semantic theme safety constraints for the ABACUS_RENDER_PIPELINE.
    """

    MIN_AA_RATIO = 4.5

    def __init__(self) -> None:
        warning_dark = _load_warning_dark_invariant()
        self.target_invariants = {
            "warning": {
                "dark": {
                    "background": warning_dark["background"],
                    "text": warning_dark["text"],
                }
            }
        }

    def _normalize_hex(self, value: str) -> str:
        if not value.startswith("#"):
            raise ValueError(f"Unsupported hex color '{value}'")
        if len(value) == 4:
            return "#" + "".join(ch * 2 for ch in value[1:])
        if len(value) == 7:
            return value
        if len(value) == 9:
            raise ValueError(
                f"8-digit hex (RGBA) not supported for contrast calculation: '{value}'. "
                "Use 6-digit hex (RGB) only."
            )
        raise ValueError(f"Unsupported hex color '{value}'")

    def _hex_to_srgb(self, hex_str: str) -> tuple[float, float, float]:
        """Converts hex color values to normalized sRGB components."""
        value = self._normalize_hex(hex_str)[1:]
        return tuple(int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

    def calculate_relative_luminance(self, hex_color: str) -> float:
        """Calculates relative luminance using the WCAG formula."""
        r, g, b = self._hex_to_srgb(hex_color)
        components = []
        for channel in (r, g, b):
            if channel <= 0.03928:
                components.append(channel / 12.92)
            else:
                components.append(((channel + 0.055) / 1.055) ** 2.4)

        return (
            0.2126 * components[0]
            + 0.7152 * components[1]
            + 0.0722 * components[2]
        )

    def calculate_contrast_ratio(self, color1_hex: str, color2_hex: str) -> float:
        """Computes contrast ratio between two colors."""
        l1 = self.calculate_relative_luminance(color1_hex)
        l2 = self.calculate_relative_luminance(color2_hex)
        lightest = max(l1, l2)
        darkest = min(l1, l2)
        return (lightest + 0.05) / (darkest + 0.05)

    def validate_theme_node(self, background_hex: str, text_hex: str) -> dict:
        """Validates a text/background pair against WCAG AA."""
        ratio = self.calculate_contrast_ratio(background_hex, text_hex)
        is_compliant = ratio >= self.MIN_AA_RATIO
        return {
            "contrast_ratio": ratio,
            "contrast_ratio_rounded": round(ratio, 2),
            "wcag_aa_compliant": is_compliant,
            "action_required": not is_compliant,
        }
