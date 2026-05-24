#!/usr/bin/env python3
import json
from pathlib import Path


class ContrastValidator:
    def __init__(self, theme_path="semantic_substrate/themes.json"):
        theme_file = Path(theme_path)
        self.target_invariants = json.loads(theme_file.read_text(encoding="utf-8"))

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def _linearize(channel):
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    def _luminance(self, hex_color):
        r, g, b = self._hex_to_rgb(hex_color)
        r_l, g_l, b_l = self._linearize(r), self._linearize(g), self._linearize(b)
        return 0.2126 * r_l + 0.7152 * g_l + 0.0722 * b_l

    def validate_theme_node(self, background, text):
        l_bg = self._luminance(background)
        l_text = self._luminance(text)
        lighter = max(l_bg, l_text)
        darker = min(l_bg, l_text)
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        return {
            "contrast_ratio": round(contrast_ratio, 2),
            "passes_wcag_aa": contrast_ratio >= 4.5,
        }
