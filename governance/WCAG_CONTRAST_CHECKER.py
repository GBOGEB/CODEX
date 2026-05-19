from __future__ import annotations

import argparse
import re
from pathlib import Path

HEX = r"#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})"
BG = re.compile(rf"bg:\s*['\"]?({HEX})['\"]?")
FG = re.compile(rf"fg:\s*['\"]?({HEX})['\"]?")
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_THEME = SCRIPT_DIR / "SEMANTIC_THEME.yaml"


def _normalize_hex(value: str) -> str:
    value = value.lower()
    if len(value) == 4:
        return "#" + "".join(ch * 2 for ch in value[1:])
    if len(value) == 7:
        return value
    if len(value) == 9:
        return value[:7]
    raise ValueError(f"Unsupported hex color '{value}'")


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = _normalize_hex(value).lstrip("#")
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
    pending: dict[str, dict[str, str]] = {}
    emitted: set[str] = set()
    for line in text.splitlines():
        if re.match(r"^\s{2}[a-z_]+:\s*$", line):
            token = line.strip().rstrip(":")
        mode_match = re.match(r"^\s{4}(light|dark):\s*(.*)$", line)
        if mode_match:
            mode = mode_match.group(1)
            key = f"{token}.{mode}"
            pending.setdefault(key, {"bg": "", "fg": ""})
            line = mode_match.group(2)
        key = f"{token}.{mode}"
        if key not in pending:
            continue
        bg_match = BG.search(line)
        fg_match = FG.search(line)
        if bg_match:
            pending[key]["bg"] = bg_match.group(1)
        if fg_match:
            pending[key]["fg"] = fg_match.group(1)
        item = pending[key]
        if item["bg"] and item["fg"] and key not in emitted:
            pairs.append((key, item["bg"], item["fg"]))
            emitted.add(key)
    return pairs


def main(path: str = "governance/SEMANTIC_THEME.yaml", minimum: float = 4.5) -> int:
    text = Path(path).read_text(encoding="utf-8")
    errors = []
    pairs = parse_fg_bg_pairs(text)
    if not pairs:
        print(f"FAIL: no semantic token fg/bg pairs detected in {path}")
        return 1
    for key, bg, fg in pairs:
        ratio = contrast_ratio(bg, fg)
        if ratio < minimum:
            errors.append(f"{key}: contrast {ratio:.2f} < {minimum}")

    if errors:
        print("\n".join(f"FAIL: {e}" for e in errors))
        return 1
    print("PASS: all semantic token pairs satisfy WCAG threshold")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate WCAG contrast for semantic fg/bg token pairs.")
    parser.add_argument("path", nargs="?", default=str(DEFAULT_THEME), help="Path to semantic theme YAML.")
    parser.add_argument("minimum", nargs="?", type=float, default=4.5, help="Minimum WCAG contrast ratio.")
    args = parser.parse_args()
    raise SystemExit(main(args.path, args.minimum))
