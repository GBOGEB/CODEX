from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

FEDERATION_REPOS = {
    'GBOGEB/CODEX': {
        'role': 'source-of-truth runtime host',
        'required_contracts': [
            'runtime bridge',
            'property schemas',
            'telemetry ingestion',
            'plotly dashboards',
            'pages deployment',
            'release gate',
        ],
        'evidence': [
            'docs/wave_packages/runtime/federation_bridge_cli.py',
            'docs/wave_packages/runtime/property_schema_validator.py',
            'docs/wave_packages/runtime/telemetry_ingestion_runtime.py',
            'docs/wave_packages/runtime/plotly_runtime_dashboard.py',
            '.github/workflows/pages_deploy_runtime.yml',
            '.github/workflows/runtime_release_gate.yml',
        ],
    },
    'GBOGEB/codex-universal': {
        'role': 'downstream universal federation adapter',
        'required_contracts': [
            'federation consumer manifest',
            'runtime sync adapter',
            'schema compatibility check',
        ],
        'evidence': [],
    },
}


def check_evidence(paths: list[str]) -> list[dict]:
    checked = []
    for rel_path in paths:
        path = ROOT / rel_path
        checked.append({
            'path': rel_path,
            'exists': path.exists(),
            'size_bytes': path.stat().st_size if path.exists() else 0,
        })
    return checked


def build_report() -> dict:
    repos = []
    for repo, data in FEDERATION_REPOS.items():
        evidence = check_evidence(data['evidence'])
        required = len(data['required_contracts'])
        existing = sum(1 for item in evidence if item['exists'])
        if repo != 'GBOGEB/CODEX':
            coverage = 0
        else:
            coverage = round((existing / required) * 100, 2) if required else 0
        repos.append({
            'repository': repo,
            'role': data['role'],
            'required_contracts': data['required_contracts'],
            'evidence': evidence,
            'coverage_percent': coverage,
            'status': 'covered' if coverage >= 90 else 'requires-downstream-sync',
        })
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'cross-repo-coverage-tracked',
        'repositories': repos,
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Federation Repository Coverage',
        '',
        f"Generated: `{report['timestamp']}`",
        '',
        '| Repository | Role | Coverage | Status |',
        '|---|---|---:|---|',
    ]
    for repo in report['repositories']:
        lines.append(f"| {repo['repository']} | {repo['role']} | {repo['coverage_percent']} | {repo['status']} |")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Track cross-repo federation coverage')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'federation_repo_coverage.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'federation_repo_coverage.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'repo_count': len(report['repositories'])}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
