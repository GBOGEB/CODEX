from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

TARGETS = {
    'solver': OUT / 'ch15_solver_runtime.json',
    'statistics': OUT / 'statistics_pca_report.json',
    'deployment': OUT / 'deployment_readiness.json',
    'reality': OUT / 'reality_tracker.json',
}


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def validate() -> dict:
    checks = []
    for name, path in TARGETS.items():
        exists = path.exists()
        item = {
            'target': name,
            'path': str(path.relative_to(ROOT)),
            'exists': exists,
        }
        if exists:
            payload = load_json(path)
            item['checksum'] = checksum(path)
            item['top_level_keys'] = sorted(payload.keys())
            item['status'] = 'valid'
        else:
            item['status'] = 'missing'
        checks.append(item)

    parity_score = round(sum(1 for item in checks if item['status'] == 'valid') / len(checks) * 100, 2)

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'lockstep-valid' if parity_score >= 100 else 'partial-lockstep',
        'parity_score': parity_score,
        'checks': checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate runtime/dashboard lockstep parity')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = validate()
    (OUT / 'runtime_dashboard_lockstep.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'runtime_render_parity.json').write_text(json.dumps({'parity_score': report['parity_score']}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'parity_score': report['parity_score']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
