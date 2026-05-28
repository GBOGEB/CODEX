from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
COV = OUT / 'covariance_execution_report.json'
SOLVER = OUT / 'ch15_solver_runtime.json'


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def build_report() -> dict:
    covariance = load(COV)
    solver = load(SOLVER)

    weights = covariance.get('trust_weights', {})
    uncertainty = covariance.get('uncertainty', {})
    cases = solver.get('cases', [])

    disagreement = max((case['uncertainty_fraction'] for case in cases), default=0.0)
    confidence = max(0.0, uncertainty.get('confidence_score', 0.0) - disagreement * 10.0)

    dominant_backend = max(weights.items(), key=lambda item: item[1])[0] if weights else 'unknown'

    trust_zones = []
    for case in cases:
        zone = 'high-trust'
        if case['uncertainty_fraction'] > 0.08:
            zone = 'guarded'
        if case['uncertainty_fraction'] > 0.15:
            zone = 'low-trust'
        trust_zones.append({
            'temperature_K': case['temperature_K'],
            'pressure_bar': case['pressure_bar'],
            'zone': zone,
        })

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'passed' if confidence > 40 else 'failed',
        'dominant_backend': dominant_backend,
        'confidence_score': round(confidence, 6),
        'backend_weights': weights,
        'trust_zones': trust_zones,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Execute trust arbitration runtime')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'trust_arbitration_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'runtime_confidence_matrix.json').write_text(json.dumps({'confidence_score': report['confidence_score'], 'backend_weights': report['backend_weights']}, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'solver_trust_zones.json').write_text(json.dumps(report['trust_zones'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'dominant_backend': report['dominant_backend']}, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
