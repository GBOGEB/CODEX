#!/usr/bin/env python3
"""WCAG contrast validation utilities for G7 synthesis flows."""

from __future__ import annotations


class ContrastValidator:
    """Validate contrast for semantic theme nodes using WCAG ratio rules."""

    def __init__(self) -> None:
        self.target_invariants = {
            "warning": {
                "dark": {
                    "background": "#4A3110",
                    "text": "#FFE9A3",
                }
            }
        }

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[float, float, float]:
        hex_color = value.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {value}")
        return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def _linearize(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    def _relative_luminance(self, value: str) -> float:
        r, g, b = self._hex_to_rgb(value)
        r_l = self._linearize(r)
        g_l = self._linearize(g)
        b_l = self._linearize(b)
        return 0.2126 * r_l + 0.7152 * g_l + 0.0722 * b_l

    def validate_theme_node(self, background: str, text: str) -> dict[str, float | bool]:
        l_bg = self._relative_luminance(background)
        l_fg = self._relative_luminance(text)
        l_light, l_dark = max(l_bg, l_fg), min(l_bg, l_fg)
        ratio = (l_light + 0.05) / (l_dark + 0.05)
        return {
            "contrast_ratio": round(ratio, 2),
            "passes_wcag_aa": ratio >= 4.5,
        }
