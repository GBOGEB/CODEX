#!/usr/bin/env bash
set -euo pipefail

SSOT="${1:-contract_governance/ssot/abacus_contract_governance.yaml}"
OUT="${2:-snapshots/contract_governance}"

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

pytest tests/contract_governance -ra
python -m codex.contract_governance.cli build --ssot "$SSOT" --out "$OUT"
python -m codex.contract_governance.cli validate --ssot "$SSOT" --out "$OUT"
