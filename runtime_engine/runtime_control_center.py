from __future__ import annotations

import json
import sys
from pathlib import Path
from subprocess import run, CalledProcessError
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_engine.pipeline_config import PIPELINE_STEPS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs' / 'runtime_engine'

STATUS = {
    'SUCCESS': [],
    'FAILED': [],
}


def execute_pipeline(script_name: str) -> bool:
    try:
        result = run(
            [sys.executable, str(ROOT / 'runtime_engine' / script_name)],
            check=True,
            capture_output=True,
            text=True,
        )
        STATUS['SUCCESS'].append(script_name)
        return True

    except (CalledProcessError, OSError) as e:
        STATUS['FAILED'].append({
            'script': script_name,
            'error': str(e),
            'stderr': getattr(e, 'stderr', ''),
        })
        return False


def build_execution_summary() -> dict:
    total_pipelines = len(PIPELINE_STEPS)
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'executed': STATUS['SUCCESS'],
        'failed': STATUS['FAILED'],
        'success_rate': round(
            len(STATUS['SUCCESS']) / max(total_pipelines, 1),
            2,
        ),
        'runtime_state': 'PARTIAL_OPERATIONAL',
    }


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    for pipeline in PIPELINE_STEPS:
        execute_pipeline(pipeline)

    summary = build_execution_summary()

    output = OUTPUT / 'runtime_execution_summary.json'
    output.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print(json.dumps(summary, indent=2))
