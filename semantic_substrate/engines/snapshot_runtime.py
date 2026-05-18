from datetime import datetime
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'
SNAPSHOT_FILE = SEMANTIC / 'state_snapshots.yaml'


def load_snapshots():
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {'snapshots': []}


def generate_snapshot(active_branches, next_actions, semantic_debt):
    data = load_snapshots()
    snapshots = data.get('snapshots', [])

    next_index = len(snapshots) + 1
    snapshot_id = f'STATE-{next_index:04d}'

    snapshot = {
        'snapshot_id': snapshot_id,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active',
        'active_branches': active_branches,
        'next_actions': next_actions,
        'unresolved_semantic_debt': semantic_debt,
    }

    return snapshot


if __name__ == '__main__':
    sample = generate_snapshot(
        active_branches=['semantic_substrate'],
        next_actions=['implement runtime orchestration loop'],
        semantic_debt=['digital twin sync incomplete'],
    )

    print(sample)
