from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs' / 'runtime_engine'
TELEMETRY = OUTPUT / 'telemetry.json'
HTML = OUTPUT / 'plotly_wave_dashboard.html'

HTML_TEMPLATE = """
<html>
<head>
<script src='https://cdn.plot.ly/plotly-2.30.0.min.js'></script>
</head>
<body>
<div id='chart'></div>
<script>
const trace1 = {
  x: __WAVES__,
  y: __SCORES__,
  type: 'scatter',
  mode: 'lines+markers',
  name: 'Architecture Score'
};

const trace2 = {
  x: __WAVES__,
  y: __COMPLETION__,
  type: 'bar',
  name: 'Completion %'
};

Plotly.newPlot('chart', [trace1, trace2], {
  title: 'TupleBridge Runtime Progression'
});
</script>
</body>
</html>
"""


def render_dashboard() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    if not TELEMETRY.exists():
        print(f'Error: Telemetry file not found at {TELEMETRY}', file=sys.stderr)
        print('Run: python -m runtime_engine.telemetry_pipeline', file=sys.stderr)
        sys.exit(1)
    
    payload = json.loads(TELEMETRY.read_text(encoding='utf-8'))

    waves = [w['wave'] for w in payload['waves']]
    scores = [w['score'] for w in payload['waves']]
    completion = [w['completion'] for w in payload['waves']]

    html = HTML_TEMPLATE
    html = html.replace('__WAVES__', json.dumps(waves))
    html = html.replace('__SCORES__', json.dumps(scores))
    html = html.replace('__COMPLETION__', json.dumps(completion))

    HTML.write_text(html, encoding='utf-8')

    print('Plotly dashboard generated.')


if __name__ == '__main__':
    render_dashboard()
