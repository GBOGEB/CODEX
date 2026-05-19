from __future__ import annotations

import re
import sys
from pathlib import Path

HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return int(value[0:2], 16) / 255, int(value[2:4], 16) / 255, int(value[4:6], 16) / 255


def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def parse_fg_bg_pairs(text: str) -> list[tuple[str, str, str]]:
    pairs: list[tuple[str, str, str]] = []
    token = "unknown"
    mode = "unknown"
    for line in text.splitlines():
        if re.match(r"^\s{2}[a-z_]+:\s*$", line):
            token = line.strip().rstrip(":")
        if re.match(r"^\s{4}(light|dark):", line):
            mode = line.strip().split(":", 1)[0]
            colors = HEX.findall(line)
            if len(colors) >= 2:
                pairs.append((f"{token}.{mode}", colors[0], colors[1]))
    return pairs


def main(path: str = "governance/SEMANTIC_THEME.yaml", minimum: float = 4.5) -> int:
    text = Path(path).read_text()
    errors = []
    for key, bg, fg in parse_fg_bg_pairs(text):
        ratio = contrast_ratio(bg, fg)
        if ratio < minimum:
            errors.append(f"{key}: contrast {ratio:.2f} < {minimum}")

    if errors:
        print("\n".join(f"FAIL: {e}" for e in errors))
        return 1
    print("PASS: all semantic token pairs satisfy WCAG threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
