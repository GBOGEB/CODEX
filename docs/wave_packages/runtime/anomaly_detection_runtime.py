from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
TELEMETRY = OUT / 'telemetry_ingestion_report.json'

THRESHOLDS = {
    'temperature_K': {'min': 2.0, 'max': 6.0},
    'pressure_bar': {'min': 0.8, 'max': 2.5},
    'mass_flow_g_s': {'min': 1.0, 'max': 200.0},
}


def load_telemetry() -> dict:
    if not TELEMETRY.exists():
        return {'events': [], 'summary': {}}
    return json.loads(TELEMETRY.read_text(encoding='utf-8'))


def analyze() -> dict:
    data = load_telemetry()
    anomalies = []
    forecasts = []

    for metric, summary in data.get('summary', {}).items():
        limits = THRESHOLDS.get(metric)
        if not limits:
            continue

        latest = float(summary['latest'])
        if latest < limits['min'] or latest > limits['max']:
            anomalies.append({
                'metric': metric,
                'latest': latest,
                'limits': limits,
                'severity': 'high',
            })

        trend = 'stable'
        if latest > (limits['max'] * 0.9):
            trend = 'approaching-upper-bound'
        elif latest < (limits['min'] * 1.1):
            trend = 'approaching-lower-bound'

        forecasts.append({
            'metric': metric,
            'trend': trend,
            'forecast_risk': 'medium' if trend != 'stable' else 'low',
        })

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'analysis-complete',
        'anomaly_count': len(anomalies),
        'forecast_count': len(forecasts),
        'anomalies': anomalies,
        'forecasts': forecasts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Analyze telemetry for anomalies and predictive drift')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = analyze()
    (OUT / 'anomaly_detection_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'anomaly_count': report['anomaly_count']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
