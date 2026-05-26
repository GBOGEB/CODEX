from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / 'PIPELINE' / 'REPORTS'


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
