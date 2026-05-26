from __future__ import annotations

from pathlib import Path

import yaml

from governance.WCAG_CONTRAST_CHECKER import DEFAULT_THEME, contrast_ratio


THEME_PATH = DEFAULT_THEME


def _load_warning_dark_theme(path: Path = THEME_PATH) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    dark = data["semantic_tokens"]["warning"]["dark"]
    return {
        "background": dark["bg"],
        "text": dark["fg"],
    }


class ContrastValidator:
    """Validates contrast ratios for semantic theme nodes against WCAG AA thresholds."""

    def __init__(self) -> None:
        self.target_invariants = {
            "warning": {
                "dark": _load_warning_dark_theme(),
            }
        }

    def validate_theme_node(self, background: str, text: str) -> dict[str, float | bool]:
        ratio = round(contrast_ratio(background, text), 2)
        return {
            "contrast_ratio": ratio,
            "wcag_aa_compliant": ratio >= 4.5,
        }
