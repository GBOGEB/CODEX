from __future__ import annotations

import argparse
import json
import re
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


def _normalize_node(value: str) -> str:
    """Convert node labels to lowercase snake_case tokens for matching.

    Non-alphanumeric characters are collapsed into underscores so labels from
    different topology sections can be matched with the same token scheme.
    """
    return re.sub(r'[^a-z0-9]+', '_', str(value).lower()).strip('_')


def _extract_structured_nodes(topology: dict) -> set[str]:
    """Collect normalized node identifiers from structured topology sections."""
    nodes: set[str] = set()
    for item in topology.get('forward_recursion', []):
        if isinstance(item, str):
            nodes.add(_normalize_node(item))
    for item in topology.get('backward_recursion', []):
        if isinstance(item, str):
            nodes.add(_normalize_node(item))
    bridge = topology.get('bridge_federation', {})
    if isinstance(bridge, dict):
        for key in bridge:
            nodes.add(_normalize_node(key))
    return nodes


def reconcile() -> dict:
    if not TOPOLOGY.exists():
        return {'status': 'missing-topology'}

    topology = json.loads(TOPOLOGY.read_text(encoding='utf-8'))
    if not isinstance(topology, dict):
        return {'status': 'invalid-topology', 'detail': f'Expected dictionary, got {type(topology).__name__}'}

    structured_nodes = _extract_structured_nodes(topology)
    missing = [node for node in REQUIRED_NODES if node not in structured_nodes]

    reconciled = []
    persisted = False
    if missing:
        topology.setdefault('reconciled_nodes', [])
        recorded_nodes = set(topology['reconciled_nodes'])
        for node in missing:
            if node not in recorded_nodes:
                topology['reconciled_nodes'].append(node)
                recorded_nodes.add(node)
                reconciled.append(node)
        if reconciled:
            TOPOLOGY.write_text(json.dumps(topology, indent=2) + '\n', encoding='utf-8')
            persisted = True

    if persisted:
        status = 'reconciled-persisted'
    elif missing:
        status = 'reconciled-already-recorded'
    else:
        status = 'already-consistent'

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'missing_nodes': missing,
        'reconciled_nodes': reconciled,
        'persisted_topology': persisted,
        'structured_nodes': sorted(structured_nodes),
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
