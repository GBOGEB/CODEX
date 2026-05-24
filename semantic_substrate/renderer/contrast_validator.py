#!/usr/bin/env python3
import json
from pathlib import Path


class ContrastValidator:
    def __init__(self, theme_path: str | Path | None = None):
        if theme_path is None:
            theme_file = Path(__file__).resolve().parent.parent / "themes.json"
        else:
            theme_file = Path(theme_path)
        self.target_invariants = json.loads(theme_file.read_text(encoding="utf-8"))

    @staticmethod
    def _normalize_hex(hex_color: str) -> str:
        value = hex_color.strip()
        if not value.startswith("#"):
            raise ValueError(f"Invalid color '{value}': expected format '#RRGGBB' or '#RGB'.")
        hex_part = value[1:]
        if len(hex_part) == 3 and all(ch in "0123456789abcdefABCDEF" for ch in hex_part):
            return "#" + "".join(ch * 2 for ch in hex_part)
        if len(hex_part) == 6 and all(ch in "0123456789abcdefABCDEF" for ch in hex_part):
            return value
        if len(hex_part) == 8:
            raise ValueError(f"Invalid color '{value}': 8-digit hex (#RRGGBBAA) is not supported.")
        raise ValueError(f"Invalid color '{value}': expected format '#RRGGBB' or '#RGB'.")

    @classmethod
    def _hex_to_rgb(cls, hex_color: str):
        normalized = cls._normalize_hex(hex_color)
        hex_color = normalized.lstrip("#")
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
