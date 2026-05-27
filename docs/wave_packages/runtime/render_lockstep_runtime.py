from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / 'docs' / 'wave_packages' / 'runtime'
OUT = RUNTIME / 'out'
PAGES = RUNTIME / 'pages'

TARGETS = {
    'plotly_dashboard': PAGES / 'plotly_runtime_dashboard.html',
    'runtime_dashboard': OUT / 'runtime_dashboard_lockstep.json',
    'solver_runtime': OUT / 'ch15_solver_runtime.json',
    'covariance_runtime': OUT / 'covariance_execution_report.json',
    'trust_runtime': OUT / 'trust_arbitration_report.json',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def parity_score(items: list[dict]) -> float:
    valid = sum(1 for item in items if item['exists'])
    return round(valid / len(items) * 100, 2) if items else 0.0


def validate_targets() -> dict:
    checks = []
    for name, path in TARGETS.items():
        exists = path.exists()
        checks.append({
            'name': name,
            'path': str(path.relative_to(ROOT)),
            'exists': exists,
            'checksum': sha(path) if exists else None,
            'size_bytes': path.stat().st_size if exists else 0,
        })

    score = parity_score(checks)

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'lockstep-valid' if score >= 80 else 'lockstep-incomplete',
        'render_parity_score': score,
        'checks': checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate render/runtime lockstep federation')
    parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    report = validate_targets()

    (OUT / 'render_lockstep_report.json').write_text(
        json.dumps(report, indent=2, sort_keys=True) + '\n',
        encoding='utf-8'
    )

    matrix = {
        item['name']: {
            'checksum': item['checksum'],
            'exists': item['exists'],
            'size_bytes': item['size_bytes'],
        }
        for item in report['checks']
    }

    (OUT / 'render_checksum_matrix.json').write_text(
        json.dumps(matrix, indent=2, sort_keys=True) + '\n',
        encoding='utf-8'
    )

    (OUT / 'render_parity_score.json').write_text(
        json.dumps({'render_parity_score': report['render_parity_score']}, indent=2) + '\n',
        encoding='utf-8'
    )

    print(json.dumps({
        'status': report['status'],
        'render_parity_score': report['render_parity_score'],
    }, indent=2))

    return 0 if report['render_parity_score'] >= 80 else 1


if __name__ == '__main__':
    raise SystemExit(main())
