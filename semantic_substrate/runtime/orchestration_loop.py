from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Iterable

from semantic_substrate.engines.delta_extractor import generate_delta_stub

VALIDATOR = ROOT / 'semantic_substrate' / 'validators' / 'validate_semantic_substrate.py'


def _changed_files() -> list[str]:
    """Return tracked files changed in git working tree."""
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        files.append(line[3:])
    return files


def _run_validator() -> int:
    return subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=False).returncode


def run_orchestration(changed_files: Iterable[str] | None = None) -> dict:
    files = list(changed_files) if changed_files is not None else _changed_files()
    delta = generate_delta_stub(files)

    validation_code = _run_validator()
    return {
        'validator_exit_code': validation_code,
        'delta': delta,
        'status': 'ok' if validation_code == 0 else 'failed',
    }


if __name__ == '__main__':
    print(run_orchestration())
