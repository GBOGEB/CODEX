from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"

DEFAULT_METRICS = {
    "topology_persistence": 90,
    "synchronization_runtime": 91,
    "bridge_orchestration": 88,
    "pages_continuity": 84,
    "runtime_observability": 85,
    "covariance_runtime": 68,
    "abacus_ingestion": 64,
    "self_healing_runtime": 48,
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Plotly Runtime Dashboard</title>
<script src=\"{plotly_cdn}\"></script>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
.grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
.tile {{ border:1px solid #ccc; border-radius:8px; padding:1rem; }}
.value {{ font-size:2rem; font-weight:bold; }}
#bar_chart, #radar_chart {{ width:100%; height:500px; }}
</style>
</head>
<body>
<h1>Executable Federation Runtime Dashboard</h1>
<p>Generated: {timestamp}</p>
<div class=\"grid\">{tiles}</div>
<div id=\"bar_chart\"></div>
<div id=\"radar_chart\"></div>
<script>
const labels = {labels};
const values = {values};

Plotly.newPlot('bar_chart', [{{
  x: labels,
  y: values,
  type: 'bar'
}}], {{
  title: 'Runtime Capability Scores',
  yaxis: {{ range: [0, 100] }}
}});

Plotly.newPlot('radar_chart', [{{
  type: 'scatterpolar',
  r: values,
  theta: labels,
  fill: 'toself'
}}], {{
  polar: {{ radialaxis: {{ visible: true, range: [0, 100] }} }},
  title: 'Federation Runtime Maturity Radar'
}});
</script>
</body>
</html>
"""


def load_metrics(path: str | None):
    if path is None:
        return DEFAULT_METRICS
    return json.loads(Path(path).read_text(encoding='utf-8'))


def build_tiles(metrics: dict) -> str:
    html = []
    for key, value in metrics.items():
        html.append(
            f"<div class='tile'><h3>{key.replace('_', ' ')}</h3><div class='value'>{value}</div></div>"
        )
    return ''.join(html)


def render_dashboard(metrics: dict) -> str:
    labels = list(metrics.keys())
    values = list(metrics.values())
    return HTML_TEMPLATE.format(
        plotly_cdn=PLOTLY_CDN,
        timestamp=datetime.now(timezone.utc).isoformat(),
        tiles=build_tiles(metrics),
        labels=json.dumps(labels),
        values=json.dumps(values),
    )


def main():
    parser = argparse.ArgumentParser(description='Generate Plotly runtime dashboard')
    parser.add_argument('--input')
    parser.add_argument('--out', default='docs/wave_packages/runtime/pages/plotly_runtime_dashboard.html')
    args = parser.parse_args()

    metrics = load_metrics(args.input)
    html = render_dashboard(metrics)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')

    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'plotly-dashboard-generated',
        'output': str(out),
        'metric_count': len(metrics),
        'average_score': round(sum(metrics.values()) / len(metrics), 2),
    }

    json_out = out.with_suffix('.json')
    json_out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
