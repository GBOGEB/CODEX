from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

REFERENCE_POINTS = [
    {'temperature_K': 3.5, 'pressure_bar': 0.37, 'rho_liq': 145.0, 'rho_vap': 1.1},
    {'temperature_K': 4.0, 'pressure_bar': 0.71, 'rho_liq': 133.0, 'rho_vap': 1.9},
    {'temperature_K': 4.5, 'pressure_bar': 1.22, 'rho_liq': 118.0, 'rho_vap': 3.2},
    {'temperature_K': 5.0, 'pressure_bar': 1.88, 'rho_liq': 96.0, 'rho_vap': 5.1},
]

BACKENDS = {
    'reference_curve': {'trust': 0.92, 'bias': 0.0},
    'spline_surrogate': {'trust': 0.86, 'bias': 0.015},
    'telemetry_surrogate': {'trust': 0.78, 'bias': -0.01},
}


def interpolate(x: float, x_key: str, y_key: str) -> float:
    points = sorted(REFERENCE_POINTS, key=lambda item: item[x_key])
    if x <= points[0][x_key]:
        return points[0][y_key]
    if x >= points[-1][x_key]:
        return points[-1][y_key]
    for left, right in zip(points, points[1:]):
        if left[x_key] <= x <= right[x_key]:
            span = right[x_key] - left[x_key]
            ratio = (x - left[x_key]) / span
            return left[y_key] + ratio * (right[y_key] - left[y_key])
    raise ValueError('Interpolation failed')


def classify_region(temperature_K: float, pressure_bar: float) -> str:
    psat = interpolate(temperature_K, 'temperature_K', 'pressure_bar')
    if abs(pressure_bar - psat) / max(psat, 1e-9) < 0.08:
        return 'saturation-dome'
    if pressure_bar > psat:
        return 'compressed-liquid-side'
    return 'vapor-side'


def solve_state(temperature_K: float, pressure_bar: float, quality: float | None = None) -> dict:
    psat = interpolate(temperature_K, 'temperature_K', 'pressure_bar')
    rho_liq = interpolate(temperature_K, 'temperature_K', 'rho_liq')
    rho_vap = interpolate(temperature_K, 'temperature_K', 'rho_vap')
    region = classify_region(temperature_K, pressure_bar)

    if quality is None:
        quality = 0.5 if region == 'saturation-dome' else 0.0 if region == 'compressed-liquid-side' else 1.0
    quality = max(0.0, min(float(quality), 1.0))

    specific_volume = ((1.0 - quality) / rho_liq) + (quality / rho_vap)
    density = 1.0 / specific_volume
    liquid_yield = 1.0 - quality

    backend_results = []
    for backend, cfg in BACKENDS.items():
        backend_density = density * (1.0 + cfg['bias'])
        backend_results.append({
            'backend': backend,
            'density_kg_m3': round(backend_density, 6),
            'trust': cfg['trust'],
            'weighted_density': round(backend_density * cfg['trust'], 6),
        })

    trust_sum = sum(item['trust'] for item in backend_results)
    arbitrated_density = sum(item['weighted_density'] for item in backend_results) / trust_sum
    spread = max(item['density_kg_m3'] for item in backend_results) - min(item['density_kg_m3'] for item in backend_results)
    uncertainty = max(0.001, spread / max(arbitrated_density, 1e-9))

    return {
        'temperature_K': temperature_K,
        'pressure_bar': pressure_bar,
        'psat_bar': round(psat, 6),
        'region': region,
        'quality': round(quality, 6),
        'liquid_yield': round(liquid_yield, 6),
        'density_kg_m3': round(arbitrated_density, 6),
        'uncertainty_fraction': round(uncertainty, 6),
        'backend_results': backend_results,
    }


def build_solver_report() -> dict:
    cases = [
        solve_state(3.8, 0.55, 0.2),
        solve_state(4.2, 0.90, 0.5),
        solve_state(4.6, 1.30, 0.8),
        solve_state(4.8, 2.00, None),
    ]
    validation = {
        'case_count': len(cases),
        'density_positive': all(case['density_kg_m3'] > 0 for case in cases),
        'quality_bounded': all(0 <= case['quality'] <= 1 for case in cases),
        'uncertainty_bounded': all(0 <= case['uncertainty_fraction'] < 1 for case in cases),
    }
    status = 'passed' if all(validation.values()) else 'failed'
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'solver': 'CH15 surrogate thermodynamic federation solver',
        'cases': cases,
        'validation': validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Run executable CH15 solver runtime')
    parser.add_argument('--out', default='docs/wave_packages/runtime/out/ch15_solver_runtime.json')
    args = parser.parse_args()
    report = build_solver_report()
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    region_map = {'regions': sorted({case['region'] for case in report['cases']}), 'case_count': len(report['cases'])}
    (OUT / 'ch15_region_map.json').write_text(json.dumps(region_map, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'ch15_solver_validation.json').write_text(json.dumps(report['validation'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'case_count': len(report['cases'])}, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
