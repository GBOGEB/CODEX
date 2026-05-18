from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Repo-local import must happen after the sys.path bootstrap above so this
# module remains directly executable from the repository checkout.
from semantic_substrate.engines.delta_extractor import generate_delta_stub

VALIDATOR = ROOT / 'semantic_substrate' / 'validators' / 'validate_semantic_substrate.py'


def _decode_git_bytes(value: bytes) -> str:
    return value.decode('utf-8', errors='replace')


def _parse_porcelain_z(output: bytes) -> list[str]:
    """Parse `git status --porcelain=v1 -z` output into changed paths.

    Rename and copy records are encoded as two NUL-delimited paths after the
    two-character status and separating space. For semantic delta purposes the
    destination path is the actual current changed file.
    """
    parts = [part for part in output.split(b'\0') if part]
    files: list[str] = []
    index = 0

    while index < len(parts):
        entry = parts[index]
        status = entry[:2].decode('ascii', errors='replace')
        path = entry[3:]

        if status.startswith(('R', 'C')):
            index += 1
            if index < len(parts):
                files.append(_decode_git_bytes(parts[index]))
            else:
                files.append(_decode_git_bytes(path))
        else:
            files.append(_decode_git_bytes(path))

        index += 1

    return files


def _changed_files() -> list[str]:
    """Return tracked files changed in the git working tree."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain=v1', '-z'],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=False,
        )
    except OSError as exc:
        raise RuntimeError(f'Unable to run git status: {exc}') from exc

    if result.returncode != 0:
        stderr = result.stderr.decode('utf-8', errors='replace').strip()
        raise RuntimeError(f'git status failed with exit code {result.returncode}: {stderr}')

    return _parse_porcelain_z(result.stdout)


def _run_validator() -> dict:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }


def run_orchestration(changed_files: Iterable[str] | None = None) -> dict:
    try:
        files = list(changed_files) if changed_files is not None else _changed_files()
        delta = generate_delta_stub(files)
    except RuntimeError as exc:
        return {
            'validator_exit_code': None,
            'validator_stdout': '',
            'validator_stderr': '',
            'delta': None,
            'status': 'failed',
            'error': str(exc),
        }

    validation = _run_validator()
    validation_code = validation['exit_code']
    return {
        'validator_exit_code': validation_code,
        'validator_stdout': validation['stdout'],
        'validator_stderr': validation['stderr'],
        'delta': delta,
        'status': 'ok' if validation_code == 0 else 'failed',
    }


if __name__ == '__main__':
    print(run_orchestration())
