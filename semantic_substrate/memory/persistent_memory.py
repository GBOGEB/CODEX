from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SESSION_MEMORY = ROOT / 'semantic_substrate' / 'memory' / 'session_memory.yaml'


def _default_memory() -> dict[str, Any]:
    return {'version': '0.1.0', 'sessions': []}


def load_memory(path: Path = SESSION_MEMORY) -> dict[str, Any]:
    if not path.exists():
        return _default_memory()
    with open(path, 'r', encoding='utf-8') as handle:
        payload = yaml.safe_load(handle) or {}
    sessions = payload.get('sessions', [])
    if not isinstance(sessions, list):
        sessions = []
    return {'version': payload.get('version', '0.1.0'), 'sessions': sessions}


def persist_session(
    snapshot: dict,
    delta: dict,
    drift_report: dict,
    recommended_next_actions: list[str],
    path: Path = SESSION_MEMORY,
) -> dict[str, Any]:
    memory = load_memory(path)
    sessions = list(memory.get('sessions', []))
    entry = {
        'session_id': snapshot.get('snapshot_id'),
        'recorded_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'replay_checkpoint': {
            'snapshot_id': snapshot.get('snapshot_id'),
            'delta_id': delta.get('id'),
            'to_state': delta.get('to_state'),
        },
        'drift': {
            'score': drift_report.get('drift_score', 0),
            'status': drift_report.get('debt_status', 'healthy'),
            'finding_count': drift_report.get('finding_count', 0),
        },
        'recommended_next_actions': list(recommended_next_actions),
    }
    sessions.append(entry)
    materialized = {'version': memory.get('version', '0.1.0'), 'sessions': sessions}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(materialized, handle, sort_keys=False)
    return entry
