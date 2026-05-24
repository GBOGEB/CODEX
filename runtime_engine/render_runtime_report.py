from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runtime_output'
REPORT = OUTPUT / 'runtime_report.md'
METRICS = OUTPUT / 'convergence_metrics.json'


def render_report() -> None:
    payload = json.loads(METRICS.read_text(encoding='utf-8'))

    lines = [
        '# Runtime Convergence Report',
        '',
        '## Metrics',
    ]

    for key, value in payload['metrics'].items():
        lines.append(f'- {key}: {value}')

    lines.extend([
        '',
        '## Waves',
    ])

    for wave in payload['waves']:
        lines.append(
            f"- {wave['wave']} :: completion={wave['completion']} delta={wave['delta']}"
        )

    REPORT.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    render_report()
    print('Runtime report rendered.')
