"""Red canaries for scripts/pytest_collect_floor.py.

Each case builds a throwaway suite in tmp_path and proves the guard goes red where it must.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.pytest_collect_floor import (
    EXIT_BELOW_FLOOR,
    EXIT_COLLECTION_ERROR,
    parse_collect_output,
)

GUARD = Path(__file__).resolve().parents[1] / "scripts" / "pytest_collect_floor.py"


def _guard(suite: Path, expected_min: int, *extra: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable, str(GUARD), "--label", "canary", "--min", str(expected_min), *extra,
        "--", str(suite), "--rootdir", str(suite), "-p", "no:cacheprovider",
    ]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=suite, check=False)


def _suite(tmp_path: Path, body: str) -> Path:
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "test_canary.py").write_text(body, encoding="utf-8")
    return suite


TWO_PASSING = "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n"


def test_floor_met_runs_suite_green(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, TWO_PASSING), 2)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"state": "COLLECTED"' in result.stdout
    assert "2 passed" in result.stdout


def test_canary_red_when_below_expected_min(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, TWO_PASSING), 3, "--no-run")
    assert result.returncode == EXIT_BELOW_FLOOR
    assert '"state": "BELOW_FLOOR"' in result.stdout


def test_canary_red_when_zero_collected(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, "X = 1\n"), 1, "--no-run")
    assert result.returncode == EXIT_BELOW_FLOOR
    assert '"collected": 0' in result.stdout


def test_canary_red_and_unknown_on_collection_error(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, "import module_that_does_not_exist_g_codex\n"), 1, "--no-run")
    assert result.returncode == EXIT_COLLECTION_ERROR
    assert '"collected": null' in result.stdout
    assert '"state": "UNKNOWN"' in result.stdout


def test_failing_suite_propagates_red(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, "def test_a():\n    assert False\n"), 1)
    assert result.returncode == 1


def test_floor_of_zero_is_refused(tmp_path: Path) -> None:
    result = _guard(_suite(tmp_path, TWO_PASSING), 0)
    assert result.returncode == 2


def test_parse_collect_output_shapes() -> None:
    assert parse_collect_output("a.py::t\n\n130 tests collected in 0.52s\n") == (130, 0)
    assert parse_collect_output("1 test collected in 0.01s") == (1, 0)
    assert parse_collect_output("no tests collected in 0.01s") == (0, 0)
    assert parse_collect_output("4 tests collected, 2 errors in 0.3s") == (4, 2)
    assert parse_collect_output("no tests collected, 1 error in 0.1s") == (0, 1)
    assert parse_collect_output("garbage") == (None, 0)
