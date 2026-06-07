#!/usr/bin/env bash
set -euo pipefail

SSOT="${1:-contract_governance/ssot/abacus_contract_governance.yaml}"
OUT="${2:-snapshots/contract_governance}"
PYTEST_LOG="${PYTEST_LOG:-contract_governance_pytest.log}"
PYTEST_JSON="${PYTEST_JSON:-contract_governance_pytest_report.json}"

printf '::group::Contract governance dependency check\n'
python - <<'PY'
import importlib.metadata
import importlib.util
import re

required = [
    "pydantic",
    "ruamel.yaml",
    "jinja2",
    "openpyxl",
    "pytest",
    "pytest_jsonreport",
    "setuptools",
    "pip",
]
missing = []
for name in required:
    try:
        found = importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        found = False
    if not found:
        missing.append(name)
if missing:
    raise SystemExit(f"missing contract governance runtime dependencies: {', '.join(missing)}")

pip_version = importlib.metadata.version("pip")
pip_match = re.match(r"^(\d+)\.(\d+)", pip_version)
if not pip_match:
    raise SystemExit(f"unable to parse pip version for PEP 660 check: {pip_version}")
pip_parts = tuple(int(part) for part in pip_match.groups())
if pip_parts < (21, 3):
    raise SystemExit(
        "pip>=21.3 is required for PEP 660 editable installs; "
        f"found pip=={pip_version}"
    )
print(f"contract governance dependency check passed with pip=={pip_version}")
PY
printf '::endgroup::\n'

printf '::group::Contract governance tests (JSON-enforced no skips allowed)\n'
pytest tests/contract_governance \
    --strict-markers \
    --json-report \
    --json-report-file="$PYTEST_JSON" \
    -ra | tee "$PYTEST_LOG"
python - "$PYTEST_JSON" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
if not report_path.exists():
    raise SystemExit(f"pytest JSON report was not produced: {report_path}")

report = json.loads(report_path.read_text(encoding="utf-8"))
summary = report.get("summary", {})
tests = report.get("tests", [])
collected = summary.get("collected", len(tests))
try:
    collected = int(collected)
except (TypeError, ValueError) as exc:
    raise SystemExit(f"pytest JSON report has invalid collected count: {collected!r}") from exc

if collected <= 0:
    raise SystemExit("contract governance pytest gate failed: zero tests collected")

blocked_summary_keys = ("skipped", "xfailed", "xpassed")
blocked_summary = {
    key: int(summary.get(key, 0) or 0)
    for key in blocked_summary_keys
}
blocked_outcomes = {"skipped", "xfailed", "xpassed"}
blocked_tests = [
    f"{test.get('nodeid', '<unknown>')}={test.get('outcome', '<unknown>')}"
    for test in tests
    if test.get("outcome") in blocked_outcomes
]

if any(blocked_summary.values()) or blocked_tests:
    detail = ", ".join(f"{key}={value}" for key, value in blocked_summary.items())
    if blocked_tests:
        detail = f"{detail}; tests: {', '.join(blocked_tests)}"
    raise SystemExit(
        "contract governance pytest gate failed: skips/xfails/xpasses detected "
        f"({detail})"
    )

print(f"contract governance pytest JSON gate passed: collected={collected}")
PY
printf '::endgroup::\n'

printf '::group::Contract governance CLI build\n'
python -m codex.contract_governance.cli build --ssot "$SSOT" --out "$OUT"
printf '::endgroup::\n'

printf '::group::Contract governance CLI validate\n'
python -m codex.contract_governance.cli validate --ssot "$SSOT" --out "$OUT"
printf '::endgroup::\n'
