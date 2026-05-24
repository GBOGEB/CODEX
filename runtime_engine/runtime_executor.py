from __future__ import annotations

import json
from pathlib import Path
from subprocess import run

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runtime_output'
OUTPUT.mkdir(exist_ok=True)


def execute_convergence_runtime() -> dict:
    metrics_file = OUTPUT / 'convergence_metrics.json'

    run(
        ['python', str(ROOT / 'runtime_engine' / 'convergence_engine.py')],
        check=True,
    )

    return json.loads(metrics_file.read_text(encoding='utf-8'))


if __name__ == '__main__':
    runtime = execute_convergence_runtime()

    print('=== EXECUTABLE RUNTIME STATE ===')
    print(json.dumps(runtime['metrics'], indent=2))
