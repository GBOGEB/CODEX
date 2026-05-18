from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'


def load_yaml(relative_path):
    with open(SEMANTIC / relative_path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def calculate_semantic_debt():
    snapshots = load_yaml('state_snapshots.yaml').get('snapshots', [])
    roe_items = load_yaml('roe_log.yaml').get('roe', [])
    deltas = load_yaml('semantic_delta_ledger.yaml').get('deltas', [])

    latest_snapshot = snapshots[-1] if snapshots else {}
    unresolved_debt = latest_snapshot.get('unresolved_semantic_debt', [])

    score = 0
    score += len(unresolved_debt) * 3
    score += len([item for item in roe_items if not item.get('promoted_to_invariants')]) * 4

    if not deltas:
        score += 5

    if score <= 10:
        band = 'healthy'
    elif score <= 25:
        band = 'warning'
    else:
        band = 'critical'

    return {
        'score': score,
        'band': band,
        'unresolved_debt_count': len(unresolved_debt),
        'roe_count': len(roe_items),
        'delta_count': len(deltas),
    }


if __name__ == '__main__':
    print(calculate_semantic_debt())
