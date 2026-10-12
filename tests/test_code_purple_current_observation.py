"""Negative/positive evidence tests; network calls are mocked."""
import importlib.util
import sys
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts/code_purple_current_observation.py"
spec = importlib.util.spec_from_file_location("code_purple_current_observation", path)
obs = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = obs
spec.loader.exec_module(obs)
A = "a" * 40
B = "b" * 40


class FakeGitHub:
    def __init__(self, *, drift=False, failure=False, hidden_rule=False):
        self.drift, self.failure, self.hidden_rule = drift, failure, hidden_rule
        self.refs = 0

    def __call__(self, path):
        if path.endswith("/git/ref/heads/main"):
            self.refs += 1
            return {"object": {"sha": B if self.drift and self.refs > 1 else A}}
        if "/pulls?state=open" in path:
            return []
        if "/pulls/" in path:
            return {"number": int(path.rsplit("/", 1)[1]),
                    "merged_at": "2026-10-12T16:30:00Z",
                    "merge_commit_sha": B, "body": "SENSITIVE_DO_NOT_PUBLISH"}
        if "/check-runs?" in path:
            checks = ([{"head_sha": A, "id": 15, "name": "Security Scan",
                        "conclusion": "failure", "html_url":
                        "https://github.com/GBOGEB/ABACUS/actions/runs/13",
                        "output": {"text": "PRIVATE"}}] if self.failure else [])
            return {"total_count": len(checks), "check_runs": checks}
        if path.endswith("/actions/jobs/15"):
            return {"id": 15, "run_id": 13, "steps": [
                {"number": 3, "name": "Enforce security roots",
                 "conclusion": "failure"},
                {"number": 4, "name": "Summarize red", "conclusion": "failure"},
            ]}
        if path.endswith("/rulesets/24494381"):
            if self.hidden_rule:
                raise RuntimeError("not authorized")
            return {"id": 24494381, "rules": [], "enforcement": "active"}
        raise AssertionError(path)


class ObservationTests(unittest.TestCase):
    def at(self, api):
        return obs.observe(api, lambda: "2026-10-12T16:40:00Z")

    def test_real_cohort_semantics_never_claim_admitted(self):
        item = self.at(FakeGitHub())
        cohort = item["historical_cohort_current_disposition"]
        self.assertEqual((cohort["merged_count"], cohort["denominator"]), (20, 20))
        self.assertIsNone(cohort["governed_merge_count"])
        self.assertEqual(item["current_prs"]["open_count"], 0)
        self.assertEqual(item["main_ruleset"]["rule_count"], 0)
        self.assertFalse(item["admission"]["security_waiver"])
        self.assertNotIn("SENSITIVE_DO_NOT_PUBLISH", str(item))

    def test_main_drift_is_fatal(self):
        with self.assertRaisesRegex(ValueError, "changed"):
            self.at(FakeGitHub(drift=True))

    def test_rule_denial_is_unknown_not_zero(self):
        item = self.at(FakeGitHub(hidden_rule=True))
        self.assertIsNone(item["main_ruleset"]["rule_count"])

    def test_job_red_is_not_a_verified_root_or_step(self):
        item = self.at(FakeGitHub(failure=True))
        checks = item["current_main_checks"]
        self.assertEqual(checks["status_counts"]["failure"], 1)
        self.assertIsNone(checks["verified_root_cause_count"])
        self.assertEqual(checks["failed_checks"][0]["first_red_step"]["step_number"], 3)
        self.assertEqual(checks["failed_checks"][0]["first_red_step"]["step_name"],
                         "Enforce security roots")
        self.assertEqual(checks["failed_checks"][0]["workflow_run_id"], 13)
        self.assertEqual(checks["failed_checks"][0]["root_cause_class"],
                         "UNKNOWN_NO_CAUSAL_PROOF")
        self.assertNotIn("PRIVATE", str(item))

    def test_bd_coverage_pca_nullable(self):
        item = self.at(FakeGitHub())
        self.assertTrue(all(v is None for k, v in item["unmeasured"].items()
                            if k != "state"))

    def test_unstable_check_total_is_unknown_not_zero(self):
        class Moving(FakeGitHub):
            def __call__(self, path):
                value = super().__call__(path)
                if "/check-runs?" in path:
                    return {"total_count": 1, "check_runs": []}
                return value
        result = self.at(Moving())
        checks = result["current_main_checks"]
        self.assertIsNone(checks["denominator"])
        self.assertIsNone(checks["status_counts"])
        self.assertEqual(checks["census_state"], "UNKNOWN_UNSTABLE_OR_BOUNDED_CENSUS")

    def test_large_check_census_is_unknown_not_false_failure(self):
        class Oversized(FakeGitHub):
            def __call__(self, path):
                result = super().__call__(path)
                if "/check-runs?" in path:
                    return {"total_count": 3000, "check_runs":
                            [{"head_sha": A, "id": n, "conclusion": "success"}
                             for n in range(100)]}
                return result

        item = self.at(Oversized())
        checks = item["current_main_checks"]
        self.assertIsNone(checks["denominator"])
        self.assertIsNone(checks["status_counts"])
        self.assertEqual(checks["census_state"],
                         "UNKNOWN_UNSTABLE_OR_BOUNDED_CENSUS")
        self.assertFalse(item["admission"]["authority_transfer"])

    def test_disallow_noncanonical_api_target(self):
        for p in ("/repos/GBOGEB/CODEX/issues/1", "/repos/GBOGEB/ABACUS/../user",
                  "/repos/GBOGEB/ABACUS/pulls/1\nAuthorization:bad"):
            with self.assertRaises(ValueError):
                obs.github_get(p)

    def test_check_head_mismatch_rejected(self):
        class Wrong(FakeGitHub):
            def __call__(self, path):
                data = super().__call__(path)
                if "/check-runs?" in path:
                    return {"total_count": 1, "check_runs":
                            [{"head_sha": B, "conclusion": "success"}]}
                return data
        with self.assertRaisesRegex(ValueError, "SHA not bound"):
            self.at(Wrong())

    def test_check_denominator_recovers_on_second_full_read(self):
        class Recover(FakeGitHub):
            def __init__(self):
                super().__init__()
                self.check_calls = 0

            def __call__(self, path):
                data = super().__call__(path)
                if "/check-runs?" in path:
                    self.check_calls += 1
                    if self.check_calls == 1:
                        return {"total_count": 1, "check_runs": []}
                return data

        api = Recover()
        result = self.at(api)
        self.assertEqual(api.check_calls, 2)
        self.assertEqual(result["current_main_checks"]["denominator"], 0)
        self.assertEqual(result["current_main_checks"]["census_state"],
                         "COMPLETE_AT_READBACK")


if __name__ == "__main__":
    unittest.main()
