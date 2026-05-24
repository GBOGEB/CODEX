from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
PAGES = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'pages'

CHECKS = [
    {'id': 'bridge_cli', 'path': 'docs/wave_packages/runtime/federation_bridge_cli.py', 'weight': 12},
    {'id': 'ci_workflow', 'path': '.github/workflows/runtime_federation_ci.yml', 'weight': 12},
    {'id': 'plotly_dashboard', 'path': 'docs/wave_packages/runtime/pages/plotly_runtime_dashboard.html', 'weight': 10},
    {'id': 'pages_bundle', 'path': 'docs/wave_packages/runtime/pages/runtime_bundle_index.html', 'weight': 10},
    {'id': 'runtime_status_md', 'path': 'docs/wave_packages/runtime/out/runtime_status.md', 'weight': 8},
    {'id': 'statistics_pca', 'path': 'docs/wave_packages/runtime/out/statistics_pca_report.json', 'weight': 10},
    {'id': 'topology_graph', 'path': 'docs/wave_packages/runtime/out/topology_runtime.mmd', 'weight': 8},
    {'id': 'tests', 'path': 'tests/test_runtime_validation.py', 'weight': 10},
    {'id': 'manifest', 'path': 'MANIFEST.json', 'weight': 10},
    {'id': 'topology_runtime', 'path': 'docs/wave_packages/topology/topology_runtime.json', 'weight': 10},
]

TODO = [
    {'item': 'Confirm GitHub Pages repository settings publish docs/ or workflow artifact', 'status': 'external-config-required', 'priority': 'high'},
    {'item': 'Add real ABACUS feed source instead of default fixture payload', 'status': 'integration-required', 'priority': 'high'},
    {'item': 'Persist runtime history across CI runs', 'status': 'next-build', 'priority': 'high'},
    {'item': 'Add live Plotly hydration from generated JSON reports', 'status': 'partial', 'priority': 'medium'},
    {'item': 'Add automated link checking for generated Pages bundle', 'status': 'next-build', 'priority': 'medium'},
    {'item': 'Add branch protection/status check policy after CI is stable', 'status': 'external-config-required', 'priority': 'medium'},
    {'item': 'Add release/promotion gate from PR branch to main', 'status': 'next-build', 'priority': 'medium'},
]


def check_file(path: str) -> dict:
    full = ROOT / path
    exists = full.exists()
    size = full.stat().st_size if exists else 0
    return {'path': path, 'exists': exists, 'size_bytes': size, 'ok': exists and size > 0}


def build_report() -> dict:
    checked = []
    passed_weight = 0
    total_weight = 0
    for check in CHECKS:
        result = check_file(check['path'])
        result['id'] = check['id']
        result['weight'] = check['weight']
        total_weight += check['weight']
        if result['ok']:
            passed_weight += check['weight']
        checked.append(result)

    completion = round((passed_weight / total_weight) * 100, 2) if total_weight else 0
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'deployment-ready' if completion >= 95 else 'deployment-near-ready' if completion >= 80 else 'deployment-incomplete',
        'completion_percent': completion,
        'checks': checked,
        'todo': TODO,
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Deployment Readiness and TODO Tracker',
        '',
        f"Generated: `{report['timestamp']}`",
        f"Status: **{report['status']}**",
        f"Completion: **{report['completion_percent']}%**",
        '',
        '## Deployment Checks',
        '',
        '| ID | OK | Bytes | Path |',
        '|---|---|---:|---|',
    ]
    for check in report['checks']:
        lines.append(f"| {check['id']} | {check['ok']} | {check['size_bytes']} | `{check['path']}` |")
    lines.extend(['', '## Remaining TODOs', '', '| Priority | Status | Item |', '|---|---|---|'])
    for item in report['todo']:
        lines.append(f"| {item['priority']} | {item['status']} | {item['item']} |")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate deployment readiness and TODO report')
    parser.add_argument('--json-out', default='docs/wave_packages/runtime/out/deployment_readiness.json')
    parser.add_argument('--md-out', default='docs/wave_packages/runtime/out/deployment_readiness.md')
    args = parser.parse_args()
    report = build_report()
    json_out = ROOT / args.json_out
    md_out = ROOT / args.md_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    md_out.write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'completion_percent': report['completion_percent']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
