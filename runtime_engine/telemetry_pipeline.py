from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runtime_output'

WAVES = [
    {'wave': 'W1', 'completion': 15, 'score': 48},
    {'wave': 'W2', 'completion': 20, 'score': 62},
    {'wave': 'W3', 'completion': 20, 'score': 74},
    {'wave': 'W4', 'completion': 20, 'score': 82},
    {'wave': 'W5', 'completion': 20, 'score': 87},
    {'wave': 'W6', 'completion': 12, 'score': 90},
    {'wave': 'W7', 'completion': 8, 'score': 92},
]

KPI_WEIGHTS = {
    'architecture': 0.30,
    'governance': 0.20,
    'validation': 0.15,
    'telemetry': 0.10,
    'federation': 0.10,
    'agents': 0.10,
    'entropy': 0.05,
}

DMAIC = {
    'define': 78,
    'measure': 62,
    'analyze': 58,
    'improve': 41,
    'control': 34,
}


def compute_wave_velocity() -> list[float]:
    deltas = []
    for previous, current in zip(WAVES, WAVES[1:]):
        deltas.append(current['score'] - previous['score'])
    return deltas


def compute_kpi_score() -> float:
    weighted = {
        'architecture': 72,
        'governance': 58,
        'validation': 54,
        'telemetry': 48,
        'federation': 45,
        'agents': 38,
        'entropy': 69,
    }

    return round(sum(weighted[k] * KPI_WEIGHTS[k] for k in KPI_WEIGHTS), 2)


def build_payload() -> dict:
    velocities = compute_wave_velocity()

    return {
        'waves': WAVES,
        'telemetry': {
            'average_completion': round(mean(w['completion'] for w in WAVES), 2),
            'average_score': round(mean(w['score'] for w in WAVES), 2),
            'wave_velocity': velocities,
            'velocity_average': round(mean(velocities), 2),
            'kpi_score': compute_kpi_score(),
            'dmaic': DMAIC,
            'pca': {
                'factor_1_governance': 0.81,
                'factor_2_validation': 0.74,
                'factor_3_topology': 0.68,
                'factor_4_runtime': 0.61,
                'factor_5_entropy': 0.52,
            },
        },
        'claimed_vs_actual': {
            'claimed': [
                'recursive governance',
                'autonomous validation',
                'runtime federation',
                'plotly telemetry',
            ],
            'actual': [
                'metrics export operational',
                'markdown rendering operational',
                'telemetry aggregation operational',
                'runtime orchestration partial',
            ],
            'missing_execution': [
                'live plotly rendering',
                'CI runtime execution',
                'real agent coordination',
                'federated synchronization runtime',
            ],
        },
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    payload = build_payload()

    out = OUTPUT / 'telemetry.json'
    out.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    print('Telemetry pipeline executed.')


if __name__ == '__main__':
    main()
