#!/usr/bin/env python3

class ContrastValidator:
    """
    G5 Hardened WCAG 2.1 Luminance and Relative Contrast Ratio Validation Engine.
    Enforces semantic theme safety constraints for the ABACUS_RENDER_PIPELINE.
    """

    def __init__(self):
        self.target_invariants = {
            "warning": {
                "dark": {
                    "background": "#4A3110",
                    "text": "#FFE9A3",
                }
            }
        }
        self.MIN_AA_RATIO = 4.5

    def _hex_to_srgb(self, hex_str: str) -> tuple[float, float, float]:
        """Converts hex color values to normalized sRGB components."""
        value = hex_str.lstrip("#")
        if len(value) != 6:
            raise ValueError(f"Invalid Hex format detected: {hex_str}")
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
            "contrast_ratio": round(ratio, 2),
            "wcag_aa_compliant": is_compliant,
            "action_required": not is_compliant,
        }
