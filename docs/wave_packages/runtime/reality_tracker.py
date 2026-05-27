from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

CAPABILITIES = {
    'live_abacus_feed': {
        'claimed': 100,
        'actual': 52,
        'evidence': ['docs/wave_packages/runtime/abacus_feed_runtime.py'],
        'missing': ['external_feed_url_or_file', 'auth_config', 'production_source_contract'],
    },
    'streaming_telemetry': {
        'claimed': 100,
        'actual': 45,
        'evidence': [],
        'missing': ['polling_adapter', 'stream_state', 'telemetry_history'],
    },
    'autonomous_rebuild_orchestration': {
        'claimed': 100,
        'actual': 62,
        'evidence': ['docs/wave_packages/runtime/federation_bridge_cli.py', '.github/workflows/runtime_federation_ci.yml'],
        'missing': ['scheduled_trigger', 'condition_based_rebuild', 'rebuild_policy'],
    },
    'predictive_runtime_intelligence': {
        'claimed': 100,
        'actual': 50,
        'evidence': ['docs/wave_packages/runtime/statistics_pca_runtime.py'],
        'missing': ['anomaly_detection', 'forecasting', 'threshold_policy'],
    },
    'topology_auto_reconciliation': {
        'claimed': 100,
        'actual': 58,
        'evidence': ['docs/wave_packages/runtime/topology_renderer.py'],
        'missing': ['reconciliation_engine', 'repair_policy', 'manifest_topology_crosscheck'],
    },
    'live_plotly_hydration': {
        'claimed': 100,
        'actual': 65,
        'evidence': ['docs/wave_packages/runtime/plotly_runtime_dashboard.py'],
        'missing': ['runtime_json_loader', 'browser_side_hydration', 'timeline_refresh'],
    },
    'runtime_replay_controls': {
        'claimed': 100,
        'actual': 70,
        'evidence': ['docs/wave_packages/runtime/runtime_history_engine.py', 'docs/wave_packages/runtime/runtime_diff_engine.py'],
        'missing': ['interactive_replay_ui', 'snapshot_selector'],
    },
    'release_promotion_governance': {
        'claimed': 100,
        'actual': 55,
        'evidence': ['.github/workflows/pages_deploy_runtime.yml'],
        'missing': ['release_gate_workflow', 'threshold_blocking', 'promotion_report'],
    },
    'external_deployment_verification': {
        'claimed': 100,
        'actual': 48,
        'evidence': ['.github/workflows/pages_deploy_runtime.yml'],
        'missing': ['post_deploy_url_probe', 'link_checker', 'deployment_smoke_test'],
    },
}


def evidence_exists(paths: list[str]) -> list[dict]:
    results = []
    for path in paths:
        full = ROOT / path
        results.append({'path': path, 'exists': full.exists(), 'size_bytes': full.stat().st_size if full.exists() else 0})
    return results


def classify(actual: int) -> str:
    if actual >= 90:
        return 'REAL'
    if actual >= 75:
        return 'TANGIBLE'
    if actual >= 50:
        return 'PARTIAL'
    if actual > 0:
        return 'CLAIMED'
    return 'MISSING'


def build_report() -> dict:
    items = []
    for name, data in CAPABILITIES.items():
        actual = int(data['actual'])
        claimed = int(data['claimed'])
        items.append({
            'capability': name,
            'claimed': claimed,
            'actual': actual,
            'delta': actual - claimed,
            'classification': classify(actual),
            'evidence': evidence_exists(data['evidence']),
            'missing': data['missing'],
        })
    average_actual = round(sum(item['actual'] for item in items) / len(items), 2)
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'reality-tracked',
        'average_actual': average_actual,
        'items': items,
    }


def render_markdown(report: dict) -> str:
    lines = [
        '# Claimed vs Actual Reality Tracker',
        '',
        f"Generated: `{report['timestamp']}`",
        f"Average actual completion: **{report['average_actual']}%**",
        '',
        '| Capability | Claimed | Actual | Delta | Reality | Missing |',
        '|---|---:|---:|---:|---|---|',
    ]
    for item in report['items']:
        lines.append(
            f"| {item['capability']} | {item['claimed']} | {item['actual']} | {item['delta']} | {item['classification']} | {', '.join(item['missing'])} |"
        )
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Track claimed vs actual federation runtime state')
    parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / 'reality_tracker.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (OUT / 'reality_tracker.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'average_actual': report['average_actual']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
