"""The ruff ratchet passes at or below the baseline, fails above it, and is never a pass when unreadable."""
from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ruff_ratchet", ROOT / "scripts" / "ruff_ratchet.py")
ratchet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ratchet)


def fake_ruff(folder: Path, version: str, findings) -> str:
    """A stand-in ruff that prints a version and a fixed JSON report."""
    script = folder / "fake_ruff.py"
    payload = findings if isinstance(findings, str) else json.dumps(findings)
    script.write_text(
        "import sys\n"
        f"if '--version' in sys.argv: print('ruff {version}'); sys.exit(0)\n"
        f"sys.stdout.write({payload!r})\n",
        encoding="utf-8",
    )
    wrapper = folder / ("ruff.cmd" if os.name == "nt" else "ruff")
    if os.name == "nt":
        wrapper.write_text(f'@"{sys.executable}" "{script}" %*\n', encoding="utf-8")
    else:
        wrapper.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{script}" "$@"\n', encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
    return str(wrapper)


def finding(n: int) -> dict:
    return {"filename": f"scripts/f{n}.py", "code": "F401", "message": "unused import", "location": {"row": n}}


class RuffRatchet(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.baseline = self.dir / "baseline.json"
        self.baseline.write_text(json.dumps({"ruff_version": "0.16.6", "max_violations": 3,
                                             "args": [".", "--exclude", "tests"]}), encoding="utf-8")

    def check(self, version, findings):
        return ratchet.main(["--baseline", str(self.baseline), "--ruff", fake_ruff(self.dir, version, findings)])

    def test_at_or_below_the_baseline_passes(self):
        self.assertEqual(self.check("0.16.6", [finding(i) for i in range(3)]), 0)
        self.assertEqual(self.check("0.16.6", [finding(1)]), 0)

    def test_a_new_violation_fails(self):
        self.assertEqual(self.check("0.16.6", [finding(i) for i in range(4)]), ratchet.EXIT_ROSE)

    def test_another_ruff_version_is_unknown(self):
        self.assertEqual(self.check("0.16.9", []), ratchet.EXIT_UNKNOWN)

    def test_unreadable_output_is_unknown_never_a_pass(self):
        self.assertEqual(self.check("0.16.6", "not json"), ratchet.EXIT_UNKNOWN)

    def test_committed_baseline_matches_the_ci_pin(self):
        baseline = json.loads((ROOT / "ci" / "ruff_baseline.json").read_text(encoding="utf-8"))
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn(f'"ruff=={baseline["ruff_version"]}"', workflow)
        self.assertIn("python scripts/ruff_ratchet.py", workflow)
        self.assertGreater(baseline["max_violations"], 0)


if __name__ == "__main__":
    unittest.main()
