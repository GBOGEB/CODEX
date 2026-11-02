"""Collection-floor guard for pytest suites that CI runs outside ``testpaths``.

Usage::

    python scripts/pytest_collect_floor.py --label NAME --min N [--no-run] -- <pytest args>

1. Collects ``<pytest args>`` with ``--collect-only``.
2. Fails (exit 3) on any collection error. The count is then UNKNOWN, never 0.
3. Fails (exit 4) when zero tests are collected.
4. Fails (exit 4) when fewer than ``--min`` (EXPECTED_MIN) tests are collected.
5. Unless ``--no-run`` is given, runs pytest with the same args and returns its exit code.

Prints one JSON evidence line, prefixed ``COLLECT_FLOOR``, for the collection-parity ledger.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

EXIT_COLLECTION_ERROR = 3
EXIT_BELOW_FLOOR = 4

_COLLECTED = re.compile(r"(\d+) tests? collected")
_ERRORS = re.compile(r"(\d+) errors?\b")


def parse_collect_output(text: str) -> tuple[int | None, int]:
    """Return ``(collected, errors)`` from ``pytest --collect-only -q`` output.

    ``collected`` is None when the summary line is missing (UNKNOWN).
    """
    summary = ""
    for line in reversed(text.splitlines()):
        if "collected" in line or "no tests" in line:
            summary = line
            break
    errors_match = _ERRORS.search(summary)
    errors = int(errors_match.group(1)) if errors_match else 0
    if "no tests collected" in summary:
        return 0, errors
    collected_match = _COLLECTED.search(summary)
    if not collected_match:
        return None, errors
    return int(collected_match.group(1)), errors


def collect(pytest_args: list[str]) -> tuple[int | None, int, int, str]:
    cmd = [
        sys.executable, "-m", "pytest", "--collect-only", "-q",
        "-o", "addopts=", "-p", "no:cacheprovider", *pytest_args,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = proc.stdout + proc.stderr
    collected, errors = parse_collect_output(output)
    return collected, errors, proc.returncode, output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--label", required=True)
    parser.add_argument("--min", type=int, required=True, dest="expected_min")
    parser.add_argument("--no-run", action="store_true", help="only enforce the collection floor")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    pytest_args = args.pytest_args
    if pytest_args[:1] == ["--"]:
        pytest_args = pytest_args[1:]
    if not pytest_args:
        parser.error("pytest args are required after --")
    if args.expected_min < 1:
        parser.error("--min must be >= 1: a floor of 0 would let a zero-test run pass")

    collected, errors, rc, output = collect(pytest_args)
    if errors or collected is None or rc not in (0, 5):
        state = "UNKNOWN"
    elif collected == 0 or collected < args.expected_min:
        state = "BELOW_FLOOR"
    else:
        state = "COLLECTED"
    evidence = {
        "label": args.label,
        "collected": None if state == "UNKNOWN" else collected,
        "collection_errors": errors,
        "expected_min": args.expected_min,
        "state": state,
    }
    print("COLLECT_FLOOR " + json.dumps(evidence, sort_keys=True))

    if state == "UNKNOWN":
        print(output, file=sys.stderr)
        print(f"FAIL [{args.label}]: collection error; count is UNKNOWN, not 0", file=sys.stderr)
        return EXIT_COLLECTION_ERROR
    if state == "BELOW_FLOOR":
        print(
            f"FAIL [{args.label}]: collected {collected} < EXPECTED_MIN {args.expected_min}"
            " (zero collected is a failure)",
            file=sys.stderr,
        )
        return EXIT_BELOW_FLOOR
    print(f"OK [{args.label}]: collected {collected} >= EXPECTED_MIN {args.expected_min}")
    if args.no_run:
        return 0
    sys.stdout.flush()
    return subprocess.run([sys.executable, "-m", "pytest", *pytest_args], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
