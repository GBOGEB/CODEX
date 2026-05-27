from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

DEFAULT_EVENTS = [
    {'source': 'ABACUS', 'wave': 'A76', 'timestamp': '2026-01-01T00:00:00Z', 'metric': 'temperature_K', 'value': 4.5},
    {'source': 'ABACUS', 'wave': 'A76', 'timestamp': '2026-01-01T00:01:00Z', 'metric': 'pressure_bar', 'value': 1.2},
    {'source': 'ABACUS', 'wave': 'A76', 'timestamp': '2026-01-01T00:02:00Z', 'metric': 'mass_flow_g_s', 'value': 42.0},
]


def load_events(path: str | None) -> list[dict]:
    if path is None:
        return DEFAULT_EVENTS
    p = Path(path)
    if p.suffix.lower() == '.json':
        data = json.loads(p.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else data.get('events', [])
    if p.suffix.lower() == '.csv':
        with p.open(newline='', encoding='utf-8') as fh:
            return list(csv.DictReader(fh))
    raise ValueError(f'Unsupported telemetry format: {p.suffix}')


def normalize_event(event: dict) -> dict:
    required = ['source', 'wave', 'timestamp', 'metric', 'value']
    missing = [key for key in required if key not in event]
    if missing:
        raise ValueError(f'Missing telemetry keys: {missing}')
    return {
        'source': str(event['source']),
        'wave': str(event['wave']),
        'timestamp': str(event['timestamp']),
        'metric': str(event['metric']),
        'value': float(event['value']),
    }


def ingest(path: str | None = None) -> dict:
    normalized = [normalize_event(event) for event in load_events(path)]
    metrics: dict[str, list[float]] = {}
    for event in normalized:
        metrics.setdefault(event['metric'], []).append(event['value'])
    summary = {
        metric: {
            'count': len(values),
            'latest': values[-1],
            'min': min(values),
            'max': max(values),
            'average': round(sum(values) / len(values), 6),
        }
        for metric, values in metrics.items()
    }
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'telemetry-ingested',
        'event_count': len(normalized),
        'metric_count': len(summary),
        'events': normalized,
        'summary': summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Ingest telemetry JSON/CSV into federation runtime format')
    parser.add_argument('--input')
    parser.add_argument('--out', default='docs/wave_packages/runtime/out/telemetry_ingestion_report.json')
    args = parser.parse_args()
    report = ingest(args.input)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'event_count': report['event_count']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
