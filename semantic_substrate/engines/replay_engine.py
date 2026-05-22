from __future__ import annotations

import hashlib
import json
from pathlib import Path
import yaml

from semantic_substrate.engines.tuple_registry_engine import TupleRegistryEngine

ROOT = Path(__file__).resolve().parents[2]
STATE_SNAPSHOTS = ROOT / 'semantic_substrate' / 'state_snapshots.yaml'


class ReplayEngine:
    def __init__(self, snapshots_path: Path = STATE_SNAPSHOTS):
        self.snapshots_path = snapshots_path
        self.tuple_registry = TupleRegistryEngine()

    def load_snapshots(self) -> list[dict]:
        if not self.snapshots_path.exists():
            return []
        with open(self.snapshots_path, 'r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle) or {}
        return list(data.get('snapshots', []))

    def get_snapshot(self, snapshot_id: str | None = None) -> dict | None:
        snapshots = self.load_snapshots()
        if not snapshots:
            return None
        if snapshot_id is None:
            return snapshots[-1]
        for snapshot in snapshots:
            if snapshot.get('snapshot_id') == snapshot_id:
                return snapshot
        return None

    def replay(self, snapshot_id: str | None = None) -> dict:
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot is None:
            return {'status': 'failed', 'error': 'No state snapshots found', 'state': None}

        tuples = sorted(
            self.tuple_registry.registry.get('tuples', []),
            key=lambda item: item.get('tuple_id', ''),
        )
        tuple_lineage = {
            item['tuple_id']: self.tuple_registry.lineage(item['tuple_id'])
            for item in tuples
            if item.get('tuple_id')
        }

        state = {
            'snapshot_id': snapshot.get('snapshot_id'),
            'active_branches': sorted(snapshot.get('active_branches', [])),
            'active_invariants': sorted(snapshot.get('active_invariants', [])),
            'unresolved_semantic_debt': sorted(snapshot.get('unresolved_semantic_debt', [])),
            'next_actions': snapshot.get('next_actions', []),
            'tuple_lineage': tuple_lineage,
        }
        state_json = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return {
            'status': 'ok',
            'error': None,
            'state': state,
            'state_hash': hashlib.sha256(state_json.encode('utf-8')).hexdigest(),
        }
