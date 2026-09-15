from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_all_pages_deployers_share_repository_concurrency_boundary() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_pages_deploy_concurrency.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
