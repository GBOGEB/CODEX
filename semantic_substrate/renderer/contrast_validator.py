from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / 'PIPELINE' / 'REPORTS'
_THEME_PATH = ROOT / 'themes' / 'semantic_cards.yaml'


@dataclass
class ContrastCheck:
    foreground: str
    background: str
    ratio: float
    required: float
    passes: bool


class WCAGContrastValidator:
    def _normalize(self, color: str) -> str:
        value = color.strip().lstrip('#')
        if len(value) != 6:
            raise ValueError(f'Invalid hex color: {color}')
        int(value, 16)
        return value.lower()

    def _linearize(self, value: int) -> float:
        channel = value / 255.0
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    def luminance(self, color: str) -> float:
        value = self._normalize(color)

        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)

        return (
            0.2126 * self._linearize(r)
            + 0.7152 * self._linearize(g)
            + 0.0722 * self._linearize(b)
        )

    def ratio(self, foreground: str, background: str) -> float:
        fg = self.luminance(foreground)
        bg = self.luminance(background)

        lighter = max(fg, bg)
        darker = min(fg, bg)

        return round((lighter + 0.05) / (darker + 0.05), 2)

    def validate(self, foreground: str, background: str, minimum: float = 4.5) -> ContrastCheck:
        ratio = self.ratio(foreground, background)

        return ContrastCheck(
            foreground=foreground,
            background=background,
            ratio=ratio,
            required=minimum,
            passes=ratio >= minimum,
        )

    def validate_dark_warning_card(self) -> ContrastCheck:
        return self.validate(
            foreground='#FFE9A3',
            background='#4A3110',
            minimum=4.5,
        )


class ContrastValidator:
    """Theme-aware WCAG contrast validator.

    Loads governed token values from themes/semantic_cards.yaml and
    exposes validate_theme_node() for per-node accessibility checks.
    """

    MIN_AA_RATIO: float = 4.5
    MIN_AAA_RATIO: float = 7.0

    def __init__(self) -> None:
        with _THEME_PATH.open('r', encoding='utf-8') as fh:
            data = yaml.safe_load(fh)
        cards = data['semantic_cards']
        self.target_invariants: dict = {
            token: {
                mode: {'background': spec['background'], 'text': spec['text']}
                for mode, spec in modes.items()
            }
            for token, modes in cards.items()
        }

    @staticmethod
    def _normalize_hex(color: str) -> str:
        v = color.strip()
        if not v.startswith('#'):
            raise ValueError(f"Unsupported hex color '{color}'")
        body = v[1:]
        if len(body) == 3:
            body = ''.join(ch * 2 for ch in body)
        if len(body) == 8:
            raise ValueError(
                f"8-digit hex (RGBA) not supported for contrast calculation: '{color}'. "
                'Use 6-digit hex (RGB) only.'
            )
        if len(body) != 6:
            raise ValueError(f"Unsupported hex color '{color}'")
        try:
            int(body, 16)  # validate hex digits
        except ValueError:
            raise ValueError(f"Unsupported hex color '{color}'")
        return '#' + body.lower()

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[float, float, float]:
        value = color.strip()
        if not value.startswith("#") or len(value) != 7:
            raise ValueError(f"Unsupported hex color '{color}'")
        hex_value = value[1:]
        try:
            int(hex_value, 16)
        except ValueError as exc:
            raise ValueError(f"Unsupported hex color '{color}'") from exc
        return (
            int(hex_value[0:2], 16) / 255,
            int(hex_value[2:4], 16) / 255,
            int(hex_value[4:6], 16) / 255,
        )

    @staticmethod
    def _linearize(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    def _relative_luminance(self, color: str) -> float:
        normalized = self._normalize_hex(color)
        r, g, b = (
            int(normalized[i:i + 2], 16) / 255
            for i in (1, 3, 5)
        )
        return 0.2126 * self._linearize(r) + 0.7152 * self._linearize(g) + 0.0722 * self._linearize(b)

    def calculate_relative_luminance(self, color: str) -> float:
        return self._relative_luminance(color)

    def validate_theme_node(self, background: str, foreground: str) -> dict:
        """Return a dict with contrast_ratio, AA/AAA compliance, and action_required."""
        l_bg = self.calculate_relative_luminance(background)
        l_fg = self.calculate_relative_luminance(foreground)
        lighter, darker = max(l_bg, l_fg), min(l_bg, l_fg)
        ratio = round((lighter + 0.05) / (darker + 0.05), 2)
        aa = ratio >= self.MIN_AA_RATIO
        aaa = ratio >= self.MIN_AAA_RATIO
        return {
            'contrast_ratio': ratio,
            'passes_wcag_aa': aa,
            'passes_wcag_aaa': aaa,
            'wcag_aa_compliant': aa,
            'wcag_aaa_compliant': aaa,
            'action_required': not aa,
        }


def export_report(check: ContrastCheck):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output = REPORT_DIR / 'contrast_validation_report.json'
    output.write_text(json.dumps(asdict(check), indent=2), encoding='utf-8')


if __name__ == '__main__':
    validator = WCAGContrastValidator()
    result = validator.validate_dark_warning_card()

    export_report(result)

    print(json.dumps(asdict(result), indent=2))

    if not result.passes:
        raise SystemExit(1)
