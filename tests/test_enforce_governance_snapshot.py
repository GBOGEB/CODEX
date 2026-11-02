"""Negative-control contract for exact-head governance enforcement."""
import unittest
from pathlib import Path

from scripts.enforce_governance_snapshot import validate

SHA = "a" * 40
REQUIRED = ["ruff", "tests", "security"]


def report(statuses=None, sha=SHA, verdict="passed"):
    statuses = statuses or ["passed", "passed", "passed"]
    return {
        "sha": sha, "status": verdict,
        "checks": [{"name": name, "status": state, "passed": state == "passed"}
                   for name, state in zip(REQUIRED, statuses)],
    }


class GovernanceVerdictTests(unittest.TestCase):
    def test_green(self):
        self.assertEqual(validate(report(), SHA, REQUIRED), [])

    def test_ruff_failure_fails(self):
        self.assertTrue(validate(report(["failed", "passed", "passed"], verdict="failed"), SHA, REQUIRED))

    def test_security_failure_fails(self):
        self.assertTrue(validate(report(["passed", "passed", "failed"], verdict="failed"), SHA, REQUIRED))

    def test_missing_required_fails(self):
        self.assertTrue(validate(report(), SHA, REQUIRED + ["manifest"]))

    def test_wrong_sha_fails(self):
        self.assertTrue(validate(report(sha="b" * 40), SHA, REQUIRED))

    def test_skipped_fails(self):
        self.assertTrue(validate(report(["passed", "skipped", "passed"], verdict="failed"), SHA, REQUIRED))

    def test_duplicate_names_fail(self):
        data = report()
        data["checks"].append(dict(data["checks"][0]))
        self.assertTrue(validate(data, SHA, REQUIRED))

    def test_missing_snapshot_fails(self):
        self.assertTrue(validate(None, SHA, REQUIRED))

    def test_effective_ci_snapshots_all_production_local_steps(self):
        """Prevent snapshot/test-canary drift from the CI production population."""
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        required = (
            "authority_integrity", "release_identity", "ssot_census",
            "ssot_schemas", "ruff", "tests", "build_pages",
            "tests_outside_testpaths", "tests_assets_governance",
            "mcp_sweep", "manifest", "globs", "stale", "links",
            "bridge_alignment", "render_linter", "dmaic_phase_map",
            "build_control", "backend_registry",
        )
        for name in required:
            with self.subTest(name=name):
                self.assertIn("--check " + name + "=${{ steps." + name + ".outcome }}", workflow)
        self.assertIn("--required " + " ".join(required), workflow)

    def test_cli_native_exit_positive_and_negative_canaries(self):
        """Exercise the real process-exit predicate, not only validate()."""
        import json
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        script = Path(__file__).resolve().parents[1] / "scripts/enforce_governance_snapshot.py"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "governance_snapshot.json"
            for label, row, expected in (
                ("green", report(), 0),
                ("ruff-red", report(["failed", "passed", "passed"], verdict="failed"), 1),
                ("security-red", report(["passed", "passed", "failed"], verdict="failed"), 1),
                ("stale-sha", report(sha="b" * 40), 1),
            ):
                with self.subTest(case=label):
                    target.write_text(json.dumps(row), encoding="utf-8")
                    proc = subprocess.run(
                        [sys.executable, str(script), "--report", str(target),
                         "--sha", SHA, "--required", *REQUIRED],
                        check=False, capture_output=True, text=True, timeout=15,
                    )
                    self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
            target.unlink()
            proc = subprocess.run(
                [sys.executable, str(script), "--report", str(target),
                 "--sha", SHA, "--required", *REQUIRED],
                check=False, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("missing or unreadable", proc.stdout)

    def test_artifact_upload_stays_after_verdict_and_always_runs(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml").read_text(
            encoding="utf-8"
        )
        emit = workflow.index("      - name: Emit governance snapshot")
        verdict = workflow.index("      - name: Verify governance snapshot before admission")
        upload = workflow.index("      - name: Upload CI governance artifacts")
        self.assertLess(emit, verdict)
        self.assertLess(verdict, upload)
        self.assertIn("if: always()", workflow[upload : upload + 100])

    def test_inconsistent_boolean_fails(self):
        data = report()
        data["checks"][0]["passed"] = False
        self.assertTrue(validate(data, SHA, REQUIRED))


if __name__ == "__main__":
    unittest.main()
