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

    def test_inconsistent_boolean_fails(self):
        data = report()
        data["checks"][0]["passed"] = False
        self.assertTrue(validate(data, SHA, REQUIRED))


if __name__ == "__main__":
    unittest.main()
