from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
SOLVER = OUT / 'ch15_solver_runtime.json'


def load_solver_cases() -> list[dict]:
    if not SOLVER.exists():
        return []
    data = json.loads(SOLVER.read_text(encoding='utf-8'))
    return data.get('cases', [])


def covariance(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - 1)


def build_matrix(cases: list[dict]) -> dict:
    labels = ['density_kg_m3', 'quality', 'uncertainty_fraction']
    columns = {label: [float(case[label]) for case in cases] for label in labels}
    matrix = []
    for a in labels:
        row = []
        for b in labels:
            row.append(round(covariance(columns[a], columns[b]), 8))
        matrix.append(row)
    return {'labels': labels, 'matrix': matrix}


def trust_weights(cases: list[dict]) -> dict:
    backend_scores: dict[str, list[float]] = {}
    for case in cases:
        for backend in case.get('backend_results', []):
            backend_scores.setdefault(backend['backend'], []).append(float(backend['trust']))
    averaged = {name: sum(values) / len(values) for name, values in backend_scores.items() if values}
    total = sum(averaged.values()) or 1.0
    return {name: round(value / total, 6) for name, value in averaged.items()}


def propagate_uncertainty(cases: list[dict]) -> dict:
    uncertainties = [float(case['uncertainty_fraction']) for case in cases]
    rms = math.sqrt(sum(value * value for value in uncertainties) / len(uncertainties)) if uncertainties else 0.0
    return {
        'case_count': len(cases),
        'max_uncertainty': round(max(uncertainties), 6) if uncertainties else 0.0,
        'rms_uncertainty': round(rms, 6),
        'confidence_score': round(max(0.0, 100.0 * (1.0 - rms)), 3),
    }


def build_report() -> dict:
    cases = load_solver_cases()
    cov = build_matrix(cases) if cases else {'labels': [], 'matrix': []}
    weights = trust_weights(cases)
    uncertainty = propagate_uncertainty(cases)
    status = 'passed' if cases and uncertainty['confidence_score'] > 50 else 'failed'
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'covariance_matrix': cov,
        'trust_weights': weights,
        'uncertainty': uncertainty,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Execute covariance propagation and trust weighting')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'covariance_execution_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'backend_covariance_matrix.json').write_text(json.dumps(report['covariance_matrix'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'trust_weighting_matrix.json').write_text(json.dumps(report['trust_weights'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'confidence_score': report['uncertainty']['confidence_score']}, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
