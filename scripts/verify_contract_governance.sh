#!/usr/bin/env bash
set -euo pipefail

SSOT="${1:-contract_governance/ssot/abacus_contract_governance.yaml}"
OUT="${2:-snapshots/contract_governance}"
PYTEST_LOG="${PYTEST_LOG:-contract_governance_pytest.log}"

printf '::group::Contract governance dependency check\n'
python - <<'PY'
import importlib.util

required = ["pydantic", "ruamel.yaml", "jinja2", "openpyxl", "pytest"]
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
print("contract governance dependency check passed")
PY
printf '::endgroup::\n'

printf '::group::Contract governance tests (no skips allowed)\n'
pytest tests/contract_governance -ra | tee "$PYTEST_LOG"
if grep -Eiq '(^|[[:space:]])(skipped|xfailed|xpassed)([[:space:]]|,|$)|no tests ran|collected 0 items' "$PYTEST_LOG"; then
    echo "contract governance pytest gate failed: skips/xfails/xpasses or zero tests detected" >&2
    exit 1
fi
printf '::endgroup::\n'

printf '::group::Contract governance CLI build\n'
python -m codex.contract_governance.cli build --ssot "$SSOT" --out "$OUT"
printf '::endgroup::\n'

printf '::group::Contract governance CLI validate\n'
python -m codex.contract_governance.cli validate --ssot "$SSOT" --out "$OUT"
printf '::endgroup::\n'
