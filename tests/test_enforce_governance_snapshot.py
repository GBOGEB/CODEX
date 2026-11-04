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
            "build_control", "backend_registry", "security_scan",
        )
        for name in required:
            with self.subTest(name=name):
                result = (
                    "${{ needs.security_scan.result }}"
                    if name == "security_scan"
                    else "${{ steps." + name + ".outcome }}"
                )
                self.assertIn("--check " + name + "=" + result, workflow)
        self.assertIn("--required " + " ".join(required), workflow)
        self.assertIn("uses: ./.github/workflows/security-scan.yml", workflow)
        self.assertIn("needs: security_scan", workflow)
        security_workflow = (
            Path(__file__).resolve().parents[1] / ".github/workflows/security-scan.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("  workflow_call:", security_workflow)

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

    def test_snapshot_exact_head_is_bound_not_synthetic_pr_merge(self):
        """PR checkout, emitter, and verifier must all use PR head identity."""
        root = Path(__file__).resolve().parents[1]
        ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        head = "${{ github.event.pull_request.head.sha || github.sha }}"
        self.assertIn("ref: " + head, ci)
        self.assertIn("EXPECTED_SOURCE_SHA: " + head, ci)
        self.assertIn("EXPECTED_SHA: " + head, ci)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_SHA"', ci)
        self.assertIn('emit_governance_snapshot.py --sha "$EXPECTED_SOURCE_SHA"', ci)

    def test_emitter_explicit_head_overrides_github_merge_sha(self):
        """CLI emitter receives the tested source identity and rejects fake SHA."""
        import json
        import os
        import subprocess
        import sys
        import tempfile
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts/emit_governance_snapshot.py"
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            env = dict(os.environ, GITHUB_SHA="b" * 40)
            good = subprocess.run(
                [sys.executable, str(script), "--sha", SHA,
                 "--check", "ruff=success", "--out", str(report_path)],
                capture_output=True, text=True, env=env, check=False, timeout=15)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            saved = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["sha"], SHA)
            self.assertEqual(saved["status"], "passed")
            bad = subprocess.run(
                [sys.executable, str(script), "--sha", "not-a-sha",
                 "--check", "ruff=success", "--out", str(report_path)],
                capture_output=True, text=True, env=env, check=False, timeout=15)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["sha"], SHA)

    def test_security_scan_keeps_python39_on_supported_explicit_ubuntu(self):
        """A rolling ubuntu-latest image loses Python 3.9 in setup-python."""
        file = (Path(__file__).resolve().parents[1] / ".github/workflows/security-scan.yml")
        workflow = file.read_text(encoding="utf-8")
        self.assertIn("os: [ubuntu-24.04, windows-latest, macos-latest]", workflow)
        self.assertIn("python-version: ['3.9', '3.10', '3.11', '3.12']", workflow)
        self.assertIn("workflow_call:", workflow)

    def test_playwright_html_qa_keeps_native_chromium_supported(self):
        """Fail if rolling Ubuntu updates break mandatory browser installation."""
        workflow = (
            Path(__file__).resolve().parents[1] / ".github/workflows/site-html-qa.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertIn("python -m playwright install --with-deps chromium", workflow)
        self.assertIn("python tools/qa/html_qa.py --check", workflow)
        self.assertIn("MANIFEST.json", workflow)
        self.assertIn("name: Site HTML QA", workflow)

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
