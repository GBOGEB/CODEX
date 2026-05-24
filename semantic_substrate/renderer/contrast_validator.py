#!/usr/bin/env python3

from src.renderers.theme_runtime import SemanticThemeRuntime


class ContrastValidator:
    def __init__(self):
        warning_dark = SemanticThemeRuntime().resolve("warning", "dark")
        self.target_invariants = {
            "warning": {
                "dark": {"background": warning_dark.background, "text": warning_dark.text}
            }
        }

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def _relative_luminance(rgb):
        def channel_transform(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = (channel_transform(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def validate_theme_node(self, background, text):
        bg_l = self._relative_luminance(self._hex_to_rgb(background))
        txt_l = self._relative_luminance(self._hex_to_rgb(text))
        lightest = max(bg_l, txt_l)
        darkest = min(bg_l, txt_l)
        contrast_ratio = (lightest + 0.05) / (darkest + 0.05)
        return {
            "background": background,
            "text": text,
            "contrast_ratio": round(contrast_ratio, 2),
            "passes_wcag_aa": contrast_ratio >= 4.5,
        }
