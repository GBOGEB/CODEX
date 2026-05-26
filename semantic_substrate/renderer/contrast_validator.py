#!/usr/bin/env python3
"""WCAG contrast validation utility for G8 lifecycle checks."""

from __future__ import annotations


class ContrastValidator:
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
        value = hex_color.strip().lstrip("#")
        if len(value) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        try:
            return tuple(int(value[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        except ValueError as exc:
            raise ValueError(f"Invalid hex color: {hex_color}") from exc

    @staticmethod
    def _linearize(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    @classmethod
    def _relative_luminance(cls, hex_color: str) -> float:
        r, g, b = cls._hex_to_rgb(hex_color)
        rl, gl, bl = cls._linearize(r), cls._linearize(g), cls._linearize(b)
        return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

    @classmethod
    def validate_theme_node(cls, background: str, text: str) -> dict:
        bg_l = cls._relative_luminance(background)
        text_l = cls._relative_luminance(text)
        lightest, darkest = max(bg_l, text_l), min(bg_l, text_l)
        ratio = (lightest + 0.05) / (darkest + 0.05)
        return {
            "background": background,
            "text": text,
            "contrast_ratio": round(ratio, 2),
            "contrast_ratio_raw": ratio,
            "passes_wcag_aa": ratio >= 4.5,
            "passes_wcag_aaa": ratio >= 7.0,
        }
