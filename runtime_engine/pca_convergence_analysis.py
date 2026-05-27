from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs' / 'runtime_engine'

PCA_FACTORS = {
    'governance': 0.81,
    'validation': 0.74,
    'topology': 0.68,
    'runtime': 0.61,
    'entropy': 0.52,
}


def compute_pca_summary() -> dict:
    total = sum(PCA_FACTORS.values())

    normalized = {
        key: round(value / total, 3)
        for key, value in PCA_FACTORS.items()
    }

    dominant = max(PCA_FACTORS, key=PCA_FACTORS.get)

    return {
        'total_variance': round(total, 3),
        'normalized_factors': normalized,
        'dominant_factor': dominant,
        'convergence_state': 'STABILIZING',
    }


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    summary = compute_pca_summary()

    output = OUTPUT / 'pca_convergence_summary.json'
    output.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print(json.dumps(summary, indent=2))
