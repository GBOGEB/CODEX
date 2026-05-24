from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOPOLOGY = ROOT / 'docs' / 'wave_packages' / 'topology' / 'topology_runtime.json'
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

REQUIRED_NODES = [
    'runtime_bridge',
    'synchronization_engine',
    'plotly_runtime_dashboard',
    'pages_runtime',
]


def reconcile() -> dict:
    if not TOPOLOGY.exists():
        return {'status': 'missing-topology'}

    topology = json.loads(TOPOLOGY.read_text(encoding='utf-8'))
    serialized = json.dumps(topology)

    missing = [node for node in REQUIRED_NODES if node not in serialized]

    reconciled = []
    if missing:
        topology.setdefault('reconciled_nodes', [])
        for node in missing:
            topology['reconciled_nodes'].append(node)
            reconciled.append(node)

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'reconciled' if reconciled else 'already-consistent',
        'missing_nodes': missing,
        'reconciled_nodes': reconciled,
        'topology_keys': list(topology.keys()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Reconcile runtime topology continuity')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = reconcile()
    (OUT / 'topology_reconciliation_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'missing_nodes': report['missing_nodes']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
