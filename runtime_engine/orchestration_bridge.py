from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run

from .pipeline_config import PIPELINE_STEPS

PIPELINE = [
    'telemetry_pipeline.py',
    'plotly_wave_dashboard.py',
]


def execute_pipeline() -> None:
    for step in PIPELINE_STEPS:
        run(
            [sys.executable, str(ROOT / 'runtime_engine' / step)],
            check=True,
        )

        print(f'Executed: {step}')


if __name__ == '__main__':
    execute_pipeline()
    print('Runtime orchestration pipeline complete.')
