from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / 'docs' / 'wave_packages' / 'runtime'
OUT = RUNTIME / 'out'
PAGES = RUNTIME / 'pages'

STEPS = [
    ['runtime_bridge.py'],
    ['synchronization_engine.py'],
    ['metrics_maturity.py'],
    ['covariance_runtime.py'],
    ['abacus_feed_runtime.py'],
    ['statistics_pca_runtime.py'],
    ['render_markdown_runtime.py'],
    ['render_html_runtime.py'],
    ['topology_renderer.py'],
    ['plotly_runtime_dashboard.py'],
    ['pages_runtime.py'],
    ['self_healing_runtime.py'],
    ['deployment_readiness.py'],
]

EXPECTED_ARTIFACTS = [
    OUT / 'runtime_status.md',
    OUT / 'topology_runtime.mmd',
    OUT / 'statistics_pca_report.json',
    OUT / 'deployment_readiness.json',
    OUT / 'deployment_readiness.md',
    OUT / 'self_healing_runtime_report.json',
    PAGES / 'index.html',
    PAGES / 'plotly_runtime_dashboard.html',
    PAGES / 'plotly_runtime_dashboard.json',
    PAGES / 'runtime_bundle_index.html',
    PAGES / 'runtime_bundle_index.json',
]


def run_step(script: str) -> dict:
    command = [sys.executable, str(RUNTIME / script)]
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    finished = datetime.now(timezone.utc).isoformat()
    return {
        'script': script,
        'command': command,
        'returncode': result.returncode,
        'status': 'passed' if result.returncode == 0 else 'failed',
        'started': started,
        'finished': finished,
        'stdout_tail': result.stdout[-2000:],
        'stderr_tail': result.stderr[-2000:],
    }


def verify_artifacts() -> list[dict]:
    checks = []
    for artifact in EXPECTED_ARTIFACTS:
        exists = artifact.exists()
        checks.append({
            'path': str(artifact.relative_to(ROOT)),
            'exists': exists,
            'size_bytes': artifact.stat().st_size if exists else 0,
            'status': 'passed' if exists and artifact.stat().st_size > 0 else 'failed',
        })
    return checks


def build_summary(step_reports: list[dict], artifact_checks: list[dict]) -> dict:
    passed_steps = sum(1 for item in step_reports if item['status'] == 'passed')
    passed_artifacts = sum(1 for item in artifact_checks if item['status'] == 'passed')
    total = len(step_reports) + len(artifact_checks)
    passed = passed_steps + passed_artifacts
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'passed' if passed == total else 'failed',
        'completion_percent': round((passed / total) * 100, 2) if total else 0,
        'steps_passed': passed_steps,
        'steps_total': len(step_reports),
        'artifacts_passed': passed_artifacts,
        'artifacts_total': len(artifact_checks),
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Federation Bridge Build Report',
        '',
        f"Generated: `{report['summary']['timestamp']}`",
        f"Status: **{report['summary']['status']}**",
        f"Completion: **{report['summary']['completion_percent']}%**",
        '',
        '## Execution Steps',
        '',
        '| Script | Status | Return Code |',
        '|---|---|---:|',
    ]
    for step in report['steps']:
        lines.append(f"| {step['script']} | {step['status']} | {step['returncode']} |")
    lines.extend(['', '## Artifact Validation', '', '| Artifact | Status | Bytes |', '|---|---|---:|'])
    for artifact in report['artifacts']:
        lines.append(f"| {artifact['path']} | {artifact['status']} | {artifact['size_bytes']} |")
    lines.append('')
    return '\n'.join(lines)


def run_bridge(stop_on_failure: bool = False) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    step_reports = []
    for step in STEPS:
        report = run_step(step[0])
        step_reports.append(report)
        if stop_on_failure and report['status'] != 'passed':
            break
    artifact_checks = verify_artifacts()
    report = {
        'summary': build_summary(step_reports, artifact_checks),
        'steps': step_reports,
        'artifacts': artifact_checks,
    }
    (OUT / 'federation_bridge_build_report.json').write_text(
        json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8'
    )
    (OUT / 'federation_bridge_build_report.md').write_text(render_markdown(report), encoding='utf-8')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description='Run the full executable federation bridge')
    parser.add_argument('--stop-on-failure', action='store_true')
    args = parser.parse_args()
    report = run_bridge(stop_on_failure=args.stop_on_failure)
    print(json.dumps(report['summary'], indent=2, sort_keys=True))
    return 0 if report['summary']['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
