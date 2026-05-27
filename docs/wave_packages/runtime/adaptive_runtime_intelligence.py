from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

INPUTS = {
    'telemetry': OUT / 'telemetry_ingestion_report.json',
    'anomaly': OUT / 'anomaly_detection_report.json',
    'covariance': OUT / 'covariance_execution_report.json',
    'trust': OUT / 'trust_arbitration_report.json',
    'history': OUT / 'runtime_history.json',
    'statistics': OUT / 'statistics_pca_report.json',
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def adaptive_thresholds(telemetry: dict) -> dict:
    thresholds = {}
    for metric, summary in telemetry.get('summary', {}).items():
        avg = float(summary.get('average', summary.get('latest', 0.0)))
        spread = max(float(summary.get('max', avg)) - float(summary.get('min', avg)), 0.0)
        margin = max(spread * 1.5, abs(avg) * 0.05, 0.001)
        thresholds[metric] = {
            'center': round(avg, 6),
            'lower': round(avg - margin, 6),
            'upper': round(avg + margin, 6),
            'margin': round(margin, 6),
        }
    return thresholds


def drift_learning(history: list[dict]) -> dict:
    if len(history) < 2:
        return {'status': 'insufficient-history', 'drift': {}}
    first = history[0]
    latest = history[-1]
    drift = {}
    for key in ['bridge_completion', 'deployment_completion', 'kpi_average_latest', 'pca_explained_variance']:
        if isinstance(first.get(key), (int, float)) and isinstance(latest.get(key), (int, float)):
            drift[key] = {
                'first': first[key],
                'latest': latest[key],
                'delta': round(latest[key] - first[key], 6),
            }
    return {'status': 'learned', 'drift': drift}


def maturity_prediction(statistics: dict, trust: dict, covariance: dict) -> dict:
    kpi = statistics.get('kpi_summary', {})
    base = float(kpi.get('average_latest', 0.0))
    confidence = float(trust.get('confidence_score', 0.0))
    uncertainty = covariance.get('uncertainty', {})
    penalty = float(uncertainty.get('rms_uncertainty', 0.0)) * 100.0
    predicted = max(0.0, min(100.0, (base * 0.55) + (confidence * 0.35) - (penalty * 0.10)))
    return {
        'base_kpi': round(base, 6),
        'trust_confidence': round(confidence, 6),
        'uncertainty_penalty': round(penalty, 6),
        'predicted_maturity': round(predicted, 6),
    }


def build_report() -> dict:
    telemetry = load_json(INPUTS['telemetry'], {'summary': {}})
    anomaly = load_json(INPUTS['anomaly'], {'anomaly_count': 0, 'forecasts': []})
    covariance = load_json(INPUTS['covariance'], {'uncertainty': {}})
    trust = load_json(INPUTS['trust'], {'confidence_score': 0})
    history = load_json(INPUTS['history'], [])
    statistics = load_json(INPUTS['statistics'], {'kpi_summary': {}})

    thresholds = adaptive_thresholds(telemetry)
    drift = drift_learning(history if isinstance(history, list) else [])
    prediction = maturity_prediction(statistics, trust, covariance)

    risk_score = min(100.0, anomaly.get('anomaly_count', 0) * 20.0 + max(0.0, 70.0 - prediction['predicted_maturity']))

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'adaptive-intelligence-complete',
        'adaptive_thresholds': thresholds,
        'drift_learning': drift,
        'maturity_prediction': prediction,
        'runtime_learning': {
            'forecast_count': len(anomaly.get('forecasts', [])),
            'risk_score': round(risk_score, 6),
            'risk_band': 'high' if risk_score >= 60 else 'medium' if risk_score >= 30 else 'low',
        },
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Adaptive Runtime Intelligence Report',
        '',
        f"Generated: `{report['timestamp']}`",
        f"Status: **{report['status']}**",
        '',
        '## Adaptive Thresholds',
        '',
        '| Metric | Lower | Center | Upper |',
        '|---|---:|---:|---:|',
    ]
    for metric, threshold in report['adaptive_thresholds'].items():
        lines.append(f"| {metric} | {threshold['lower']} | {threshold['center']} | {threshold['upper']} |")
    lines.extend(['', '## Maturity Prediction', ''])
    for key, value in report['maturity_prediction'].items():
        lines.append(f'- {key}: {value}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Run adaptive runtime intelligence')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'adaptive_runtime_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'runtime_learning_matrix.json').write_text(json.dumps(report['runtime_learning'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'maturity_prediction.json').write_text(json.dumps(report['maturity_prediction'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'drift_evolution_report.json').write_text(json.dumps(report['drift_learning'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'adaptive_runtime_report.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'risk_band': report['runtime_learning']['risk_band']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
