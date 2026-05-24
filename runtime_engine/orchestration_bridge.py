from __future__ import annotations

from pathlib import Path
from subprocess import run

ROOT = Path(__file__).resolve().parents[1]

PIPELINE = [
    'telemetry_pipeline.py',
    'convergence_engine.py',
    'render_runtime_report.py',
    'plotly_wave_dashboard.py',
]


def execute_pipeline() -> None:
    for step in PIPELINE:
        run(
            ['python', str(ROOT / 'runtime_engine' / step)],
            check=True,
        )

        print(f'Executed: {step}')


if __name__ == '__main__':
    execute_pipeline()
    print('Runtime orchestration pipeline complete.')
