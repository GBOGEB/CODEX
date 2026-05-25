from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run

ROOT = Path(__file__).resolve().parents[1]

# Import pipeline steps from shared config
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pipeline_config",
    ROOT / "runtime_engine" / "pipeline_config.py"
)
pipeline_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline_config)
PIPELINE_STEPS = pipeline_config.PIPELINE_STEPS


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
