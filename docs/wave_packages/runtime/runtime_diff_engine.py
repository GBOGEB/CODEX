from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
HISTORY = OUT / 'runtime_history.json'


def load_history() -> list[dict]:
    if not HISTORY.exists():
        return []
    return json.loads(HISTORY.read_text(encoding='utf-8'))


def build_diff(history: list[dict]) -> dict:
    if len(history) < 2:
        return {
            'status': 'insufficient-history',
            'history_length': len(history),
        }

    previous = history[-2]
    current = history[-1]

    diffs = {}
    for key in current:
        if key in ['timestamp', 'wave']:
            continue
        if isinstance(current[key], (int, float)) and isinstance(previous.get(key), (int, float)):
            diffs[key] = {
                'previous': previous[key],
                'current': current[key],
                'delta': round(current[key] - previous[key], 6),
                'trend': 'up' if current[key] > previous[key] else 'down' if current[key] < previous[key] else 'flat',
            }

    regressions = [
        key for key, value in diffs.items()
        if value['delta'] < 0
    ]

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'diff-generated',
        'previous_wave': previous.get('wave'),
        'current_wave': current.get('wave'),
        'diffs': diffs,
        'regression_count': len(regressions),
        'regressions': regressions,
    }


def render_html(report: dict) -> str:
    rows = []
    for key, value in report.get('diffs', {}).items():
        rows.append(
            f'<tr><td>{key}</td><td>{value["previous"]}</td><td>{value["current"]}</td><td>{value["delta"]}</td><td>{value["trend"]}</td></tr>'
        )

    return f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Runtime Diff Dashboard</title></head>
<body>
<h1>Runtime Diff Dashboard</h1>
<p>Regression count: {report.get('regression_count', 0)}</p>
<table border="1" cellpadding="6">
<tr><th>Metric</th><th>Previous</th><th>Current</th><th>Delta</th><th>Trend</th></tr>
{''.join(rows)}
</table>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate runtime diffs and regression analysis')
    parser.parse_args()
    
    # Ensure output directory exists
    OUT.mkdir(parents=True, exist_ok=True)
    
    report = build_diff(load_history())
    (OUT / 'runtime_diff.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'runtime_diff_dashboard.html').write_text(render_html(report), encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
