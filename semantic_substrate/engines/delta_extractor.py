import datetime as dt
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / 'semantic_substrate' / 'semantic_delta_ledger.yaml'


def classify_change(path: str):
    if path.endswith('.yaml'):
        return 'semantic-config'
    if path.endswith('.md'):
        return 'documentation'
    if path.endswith('.py'):
        return 'runtime'
    return 'unknown'


def generate_delta_stub(changed_files):
    return {
        'summary': 'Auto-generated semantic delta candidate',
        'files': [
            {
                'path': item,
                'classification': classify_change(item),
            }
            for item in changed_files
        ],
    }


def _load_ledger(path: Path = LEDGER) -> dict:
    if not path.exists():
        return {'version': '0.1.0', 'deltas': []}
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {'version': '0.1.0', 'deltas': []}


def _next_delta_id(existing_deltas: list[dict]) -> str:
    if not existing_deltas:
        return 'DELTA-0001'
    numeric_ids = []
    for item in existing_deltas:
        delta_id = item.get('id', '')
        if delta_id.startswith('DELTA-'):
            suffix = delta_id.removeprefix('DELTA-')
            if suffix.isdigit():
                numeric_ids.append(int(suffix))
    return f'DELTA-{(max(numeric_ids, default=0) + 1):04d}'


def generate_delta_entry(
    changed_files,
    from_state='STATE-0000',
    to_state='STATE-0001',
    date: str | None = None,
):
    delta = generate_delta_stub(changed_files)
    added = [item['path'] for item in delta['files']]
    return {
        'id': None,
        'date': date or dt.date.today().isoformat(),
        'from_state': from_state,
        'to_state': to_state,
        'summary': delta['summary'],
        'added': added,
        'modified': [],
        'removed': [],
        'impact': {
            'reconstructability': 'medium',
            'lineage_visibility': 'medium',
            'governance_readiness': 'medium',
        },
        'files': delta['files'],
    }


def append_delta_to_ledger(entry: dict, path: Path = LEDGER) -> dict:
    ledger = _load_ledger(path)
    deltas = list(ledger.get('deltas', []))
    materialized = dict(entry)
    materialized['id'] = materialized.get('id') or _next_delta_id(deltas)
    deltas.append(materialized)
    ledger['deltas'] = deltas
    with open(path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(ledger, handle, sort_keys=False)
    return materialized


if __name__ == '__main__':
    sample = [
        'semantic_substrate/invariants.yaml',
        'semantic_substrate/validators/validate_semantic_substrate.py',
    ]

    print(generate_delta_stub(sample))
