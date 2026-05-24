from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runtime_output'
OUTPUT.mkdir(exist_ok=True)

DMAIC = {
    'define': [70, 74, 78],
    'measure': [48, 56, 62],
    'analyze': [40, 51, 58],
    'improve': [18, 27, 41],
    'control': [10, 18, 34],
}


def build_dmaic_summary() -> dict:
    summary = {}

    for phase, values in DMAIC.items():
        summary[phase] = {
            'current': values[-1],
            'average': round(mean(values), 2),
            'delta': values[-1] - values[0],
        }

    return summary


if __name__ == '__main__':
    summary = build_dmaic_summary()

    output = OUTPUT / 'dmaic_runtime_summary.json'
    output.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print(json.dumps(summary, indent=2))
