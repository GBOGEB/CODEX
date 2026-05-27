from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / 'docs' / 'wave_packages' / 'runtime'
OUT = RUNTIME / 'out'

SOURCES = {
    'solver': OUT / 'ch15_solver_runtime.json',
    'covariance': OUT / 'covariance_execution_report.json',
    'trust': OUT / 'trust_arbitration_report.json',
    'deployment': OUT / 'deployment_readiness.json',
    'reality': OUT / 'reality_tracker.json',
    'telemetry': OUT / 'telemetry_ingestion_report.json',
    'lockstep': OUT / 'runtime_dashboard_lockstep.json',
}


def load(path: Path) -> dict:
    if not path.exists():
        return {'status': 'missing'}
    return json.loads(path.read_text(encoding='utf-8'))


def build_bundle() -> dict:
    bundle = {name: load(path) for name, path in SOURCES.items()}

    maturity = {
        'solver_cases': len(bundle['solver'].get('cases', [])),
        'telemetry_events': bundle['telemetry'].get('event_count', 0),
        'render_parity': bundle['lockstep'].get('parity_score', 0),
        'deployment_completion': bundle['deployment'].get('completion_percent', 0),
        'reality_alignment': bundle['reality'].get('average_actual', 0),
    }

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'operational-cockpit-ready',
        'maturity': maturity,
        'sources': bundle,
    }


def render_html(bundle: dict) -> str:
    maturity = bundle['maturity']
    return f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>CH15 Operational Cockpit</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
</head>
<body>
  <h1>CH15 Operational Cockpit</h1>
  <div id="maturity_chart" style="width:100%;height:500px;"></div>
  <script>
    Plotly.newPlot('maturity_chart', [{'{'}
      x: {list(maturity.keys())},
      y: {list(maturity.values())},
      type: 'bar'
    {'}'}], {'{'}title: 'Federation Runtime Maturity'{'}'});
  </script>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate CH15 operational cockpit')
    parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    bundle = build_bundle()

    (OUT / 'ch15_runtime_bundle.json').write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + '\n',
        encoding='utf-8'
    )

    operational_matrix = {
        'sources': list(bundle['sources'].keys()),
        'maturity': bundle['maturity'],
    }

    (OUT / 'operational_runtime_matrix.json').write_text(
        json.dumps(operational_matrix, indent=2, sort_keys=True) + '\n',
        encoding='utf-8'
    )

    html = render_html(bundle)

    (OUT / 'ch15_operational_cockpit.html').write_text(
        html,
        encoding='utf-8'
    )

    print(json.dumps({
        'status': bundle['status'],
        'sources': len(bundle['sources']),
    }, indent=2))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
