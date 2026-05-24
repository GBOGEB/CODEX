from __future__ import annotations

import json
from pathlib import Path
from subprocess import run
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runtime_output'
OUTPUT.mkdir(exist_ok=True)

PIPELINES = [
    'telemetry_pipeline.py',
    'convergence_engine.py',
    'render_runtime_report.py',
    'plotly_wave_dashboard.py',
]

STATUS = {
    'SUCCESS': [],
    'FAILED': [],
}


def execute_pipeline(script_name: str) -> bool:
    try:
        run(
            ['python', str(ROOT / 'runtime_engine' / script_name)],
            check=True,
        )
        STATUS['SUCCESS'].append(script_name)
        return True

    except Exception:
        STATUS['FAILED'].append(script_name)
        return False


def build_execution_summary() -> dict:
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'executed': STATUS['SUCCESS'],
        'failed': STATUS['FAILED'],
        'success_rate': round(
            len(STATUS['SUCCESS']) / max(len(PIPELINES), 1),
            2,
        ),
        'runtime_state': 'PARTIAL_OPERATIONAL',
    }


if __name__ == '__main__':
    for pipeline in PIPELINES:
        execute_pipeline(pipeline)

    summary = build_execution_summary()

    output = OUTPUT / 'runtime_execution_summary.json'
    output.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print(json.dumps(summary, indent=2))
