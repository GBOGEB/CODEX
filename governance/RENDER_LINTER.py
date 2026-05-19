from __future__ import annotations

import subprocess
import sys
from pathlib import Path


RULES = [
    "no_low_contrast",
    "slide_id_required",
]


def run() -> int:
    rc = 0
    theme = Path("governance/SEMANTIC_THEME.yaml")
    lineage = Path("governance/LINEAGE_SCHEMA.yaml")

    if not theme.exists() or not lineage.exists():
        print("FAIL: missing governance artifacts")
        return 1

    print("CHECK: no_low_contrast")
    r1 = subprocess.run([sys.executable, "governance/WCAG_CONTRAST_CHECKER.py"], check=False)
    rc |= r1.returncode

    print("CHECK: slide_id_required (lineage example)")
    r2 = subprocess.run(
        [sys.executable, "governance/SLIDE_ID_ENFORCER.py", "governance/LINEAGE_SCHEMA.yaml"], check=False
    )
    rc |= r2.returncode

    if rc == 0:
        print("PASS: render linter checks passed")
    else:
        print("FAIL: render linter checks failed")
    return rc


if __name__ == "__main__":
    raise SystemExit(run())
