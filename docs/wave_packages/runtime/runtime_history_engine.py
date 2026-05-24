from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
HISTORY = OUT / 'runtime_history.json'

SNAPSHOT_INPUTS = [
    OUT / 'federation_bridge_build_report.json',
    OUT / 'deployment_readiness.json',
    OUT / 'statistics_pca_report.json',
]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {'missing': str(path.relative_to(ROOT))}
    return json.loads(path.read_text(encoding='utf-8'))


def current_snapshot() -> dict:
    bridge = load_json(SNAPSHOT_INPUTS[0])
    deploy = load_json(SNAPSHOT_INPUTS[1])
    stats = load_json(SNAPSHOT_INPUTS[2])
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'wave': 'A72',
        'bridge_status': bridge.get('summary', {}).get('status', 'unknown'),
        'bridge_completion': bridge.get('summary', {}).get('completion_percent', 0),
        'deployment_status': deploy.get('status', 'unknown'),
        'deployment_completion': deploy.get('completion_percent', 0),
        'kpi_average_latest': stats.get('kpi_summary', {}).get('average_latest', 0),
        'pca_explained_variance': stats.get('pca', {}).get('explained_variance_ratio', 0),
    }


def load_history() -> list[dict]:
    if not HISTORY.exists():
        return []
    data = json.loads(HISTORY.read_text(encoding='utf-8'))
    return data if isinstance(data, list) else []


def append_snapshot() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    history = load_history()
    snapshot = current_snapshot()
    history.append(snapshot)
    HISTORY.write_text(json.dumps(history, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return {'status': 'history-updated', 'snapshot_count': len(history), 'latest': snapshot}


def main() -> int:
    parser = argparse.ArgumentParser(description='Persist and replay runtime history')
    parser.add_argument('--out', default=str(HISTORY))
    parser.parse_args()
    report = append_snapshot()
    (OUT / 'runtime_history_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
