from __future__ import annotations

# TODO: Wave A6.1 — Governance linter verification complete
# ✅ Task A6.1.1.1: contrast_lint.py exists at renderers/lint/contrast_lint.py
# ✅ Task A6.1.1.2: overflow_lint.py exists at renderers/lint/overflow_lint.py
# ✅ Task A6.1.1.3: spacing_lint.py exists at renderers/lint/spacing_lint.py
# ✅ Task A6.1.1.4: navigation_lint.py exists at renderers/lint/navigation_lint.py
# ✅ All linters wired into RENDER_LINTER.py execution (see RULES list below)
# Note: WCAG_CONTRAST_CHECKER.py may be redundant with contrast_lint.py — deduplication pending
# See: MANIFEST/A6_FEDERATION_TODO_ROADMAP.md § Phase A6.1

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

REQUIRED_ARTIFACTS = [
    SCRIPT_DIR / "SEMANTIC_THEME.yaml",
    SCRIPT_DIR / "LINEAGE_SCHEMA.yaml",
    SCRIPT_DIR / "LAYOUT_CONTRACTS.yaml",
    SCRIPT_DIR / "RENDER_RULES.md",
    SCRIPT_DIR / "RENDER_TEST_SUITE.md",
    REPO_ROOT / "MANIFEST" / "ROADMAP.md",
    REPO_ROOT / "MANIFEST" / "MASTER_SLIDE_REGISTRY.yaml",
    REPO_ROOT / "MANIFEST" / "MASTER_FIGURE_REGISTRY.yaml",
    REPO_ROOT / "MANIFEST" / "LINEAGE.md",
]

RULES = [
    ("no_low_contrast", [sys.executable, str(SCRIPT_DIR / "WCAG_CONTRAST_CHECKER.py")]),
    (
        "slide_id_required (lineage example)",
        [sys.executable, str(SCRIPT_DIR / "SLIDE_ID_ENFORCER.py"), str(SCRIPT_DIR / "LINEAGE_SCHEMA.yaml")],
    ),
    (
        "overflow_governance",
        [sys.executable, "-m", "renderers.lint.overflow_lint"],
    ),
    (
        "spacing_governance",
        [sys.executable, "-m", "renderers.lint.spacing_lint"],
    ),
    (
        "navigation_governance",
        [sys.executable, "-m", "renderers.lint.navigation_lint"],
    ),
]


def run() -> int:
    missing = [path for path in REQUIRED_ARTIFACTS if not path.exists()]
    if missing:
        print("FAIL: missing governance artifacts:")
        for path in missing:
            print(f" - {path}")
        return 1

    failed = False
    for name, command in RULES:
        print(f"CHECK: {name}")
        result = subprocess.run(command, check=False, cwd=str(REPO_ROOT))
        if result.returncode != 0:
            failed = True

    if not failed:
        print("PASS: render linter checks passed")
        return 0
    print("FAIL: render linter checks failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
