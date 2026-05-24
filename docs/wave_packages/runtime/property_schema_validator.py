from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

SCHEMES = {
    'feed': {
        'required': {'source': str, 'wave': str, 'timestamp': str, 'signals': dict},
        'numeric_dicts': ['signals'],
    },
    'topology': {
        'required': {'version': str, 'forward_recursion': list, 'backward_recursion': list},
        'min_lengths': {'forward_recursion': 2, 'backward_recursion': 2},
    },
    'statistics_pca': {
        'required': {'status': str, 'statistics': dict, 'covariance_matrix': dict, 'pca': dict, 'kpi_summary': dict},
        'required_nested': {'pca': ['explained_variance_ratio', 'loadings']},
    },
    'deployment': {
        'required': {'status': str, 'completion_percent': (int, float), 'checks': list, 'todo': list},
        'range': {'completion_percent': [0, 100]},
    },
    'reality': {
        'required': {'status': str, 'average_actual': (int, float), 'items': list},
        'range': {'average_actual': [0, 100]},
    },
    'bridge_build': {
        'required': {'summary': dict, 'steps': list, 'artifacts': list},
        'required_nested': {'summary': ['status', 'completion_percent']},
    },
}

DEFAULT_FILES = {
    'topology': 'docs/wave_packages/topology/topology_runtime.json',
    'statistics_pca': 'docs/wave_packages/runtime/out/statistics_pca_report.json',
    'deployment': 'docs/wave_packages/runtime/out/deployment_readiness.json',
    'reality': 'docs/wave_packages/runtime/out/reality_tracker.json',
    'bridge_build': 'docs/wave_packages/runtime/out/federation_bridge_build_report.json',
}


def type_name(expected: Any) -> str:
    if isinstance(expected, tuple):
        return ' or '.join(item.__name__ for item in expected)
    return expected.__name__


def validate_object(name: str, data: dict) -> dict:
    scheme = SCHEMES[name]
    errors = []

    for key, expected in scheme.get('required', {}).items():
        if key not in data:
            errors.append(f'missing required key: {key}')
            continue
        if not isinstance(data[key], expected):
            errors.append(f'key {key} expected {type_name(expected)}, got {type(data[key]).__name__}')

    for key, min_length in scheme.get('min_lengths', {}).items():
        if key in data and isinstance(data[key], list) and len(data[key]) < min_length:
            errors.append(f'key {key} requires at least {min_length} items')

    for key, bounds in scheme.get('range', {}).items():
        if key in data and isinstance(data[key], (int, float)):
            low, high = bounds
            if data[key] < low or data[key] > high:
                errors.append(f'key {key} outside range {low}..{high}')

    for parent, children in scheme.get('required_nested', {}).items():
        if parent not in data or not isinstance(data[parent], dict):
            continue
        for child in children:
            if child not in data[parent]:
                errors.append(f'missing nested key: {parent}.{child}')

    for key in scheme.get('numeric_dicts', []):
        if key in data and isinstance(data[key], dict):
            for signal, value in data[key].items():
                if not isinstance(value, (int, float)):
                    errors.append(f'{key}.{signal} must be numeric')

    return {
        'scheme': name,
        'status': 'passed' if not errors else 'failed',
        'errors': errors,
    }


def validate_file(name: str, rel_path: str) -> dict:
    path = ROOT / rel_path
    if not path.exists():
        return {'scheme': name, 'path': rel_path, 'status': 'missing', 'errors': ['file missing']}
    data = json.loads(path.read_text(encoding='utf-8'))
    result = validate_object(name, data)
    result['path'] = rel_path
    return result


def build_report() -> dict:
    checks = [validate_file(name, path) for name, path in DEFAULT_FILES.items()]
    passed = sum(1 for check in checks if check['status'] == 'passed')
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'passed' if passed == len(checks) else 'failed',
        'completion_percent': round((passed / len(checks)) * 100, 2) if checks else 0,
        'checks': checks,
        'schemes': list(SCHEMES.keys()),
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Federated Property Scheme Validation',
        '',
        f"Generated: `{report['timestamp']}`",
        f"Status: **{report['status']}**",
        f"Completion: **{report['completion_percent']}%**",
        '',
        '| Scheme | Status | Path | Errors |',
        '|---|---|---|---|',
    ]
    for check in report['checks']:
        lines.append(f"| {check['scheme']} | {check['status']} | `{check.get('path', '')}` | {'; '.join(check['errors'])} |")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate all federation property schemes')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'property_schema_validation.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'property_schema_validation.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'completion_percent': report['completion_percent']}, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
