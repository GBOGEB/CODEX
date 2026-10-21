"""Regression: native governance stale diagnostics must survive the artifact pipe.

Synthetic manifest/pages only. This does not change publication inventory or waive
the failure; pipeline exit status must remain nonzero on every first-red.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/full-stack-governance.yml"
CHECKER = ROOT / "scripts/check_stale.py"


class StaleArtifactCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        lines = [line.strip() for line in workflow.splitlines()
                 if "python scripts/check_stale.py" in line and "| tee " in line]
        if len(lines) != 1:
            raise AssertionError("stale checker must have one native artifact pipeline")
        cls.command = lines[0]
        if "2>&1 | tee" not in cls.command:
            raise AssertionError("stale stderr must be preserved before tee")
        if "set -euo pipefail" not in workflow:
            raise AssertionError("native pipeline must not mask the original first-red")

    def _run_case(self, *, declared, present):
        with tempfile.TemporaryDirectory(prefix="stale-qa-") as directory:
            base = Path(directory)
            (base / "scripts").mkdir()
            (base / "docs").mkdir()
            (base / "reports/abacus").mkdir(parents=True)
            shutil.copy2(CHECKER, base / "scripts/check_stale.py")
            (base / "MANIFEST.json").write_text(
                json.dumps({"published_pages": declared}), encoding="utf-8"
            )
            for item in present:
                dest = base / item
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("<!doctype html><title>synthetic</title>\n",
                                encoding="utf-8")
            env = dict(os.environ, component_dir="reports/abacus")
            completed = subprocess.run(
                ["bash", "-c", "set -euo pipefail\n" + self.command],
                cwd=base, env=env, capture_output=True, text=True,
                timeout=15, check=False,
            )
            uploaded = (base / "reports/abacus/stale.txt").read_text(encoding="utf-8")
            return completed, uploaded

    def test_clean_inventory_stays_green(self):
        run, artifact = self._run_case(
            declared=["docs/index.html"], present=["docs/index.html"]
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("stale check passed", artifact)

    def test_unregistered_atlas_first_red_is_captured_and_fails(self):
        run, artifact = self._run_case(
            declared=["docs/index.html"],
            present=["docs/index.html", "docs/method_atlas/index.html"],
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Untracked public entrypoints", artifact)
        self.assertIn("docs/method_atlas/index.html", artifact)

    def test_missing_declared_page_first_red_is_captured_and_fails(self):
        run, artifact = self._run_case(
            declared=["docs/index.html", "docs/missing.html"],
            present=["docs/index.html"],
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Missing published pages from manifest", artifact)
        self.assertIn("docs/missing.html", artifact)


if __name__ == "__main__":
    unittest.main()
