"""Fail-closed exact-head GitHub observation tests."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "code_purple_live_observation", ROOT / "scripts/code_purple_live_observation.py"
)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
HEAD, MAIN = "a" * 40, "b" * 40


def check(sha=HEAD, conclusion="success", number=5):
    return {
        "head_sha": sha, "id": number, "name": "PR Feedback Gate",
        "status": "completed", "conclusion": conclusion,
        "details_url": "https://github.com/GBOGEB/ABACUS/runs/1",
    }


class LiveObservationTests(unittest.TestCase):
    def test_no_authentication_or_coverage_inferred_from_green(self):
        result = mod.collect(
            lambda path: {"total_count": 1, "check_runs": [check()]},
            HEAD, MAIN, "2026-10-12T10:00:00+00:00",
        )
        self.assertEqual(result["feedback_gate_observation"], "SUCCESS_OBSERVED_UNVERIFIED")
        self.assertEqual(result["check_status_counts"]["success"], 1)
        self.assertEqual(result["check_status_counts"]["failure"], 0)
        self.assertIsNone(result["first_red_step"])
        self.assertEqual(result["merge_admission"], "NOT_ASSERTED")
        for key in ("independent_security_review", "authenticated_worker_rex",
                    "main_coverage_pct", "pr_diff_coverage_pct",
                    "bd_queue_open", "root_causes_closed"):
            self.assertIsNone(result[key])

    def test_failed_check_counts_without_inferred_root_step(self):
        failure = check(conclusion="failure")
        result = mod.collect(
            lambda _: {"total_count": 1, "check_runs": [failure]},
            HEAD, MAIN, "now",
        )
        self.assertEqual(result["check_status_counts"]["failure"], 1)
        self.assertEqual(result["observed_failed_check_ids"], [5])
        self.assertIsNone(result["first_red_step"])

    def test_stale_green_does_not_override_pending_gate(self):
        pending = check(conclusion=None, number=6)
        pending["status"] = "in_progress"
        result = mod.collect(
            lambda _: {"total_count": 2, "check_runs": [check(), pending]},
            HEAD, MAIN, "now",
        )
        self.assertEqual(result["feedback_gate_observation"], "BLOCKED_OR_PENDING")
        self.assertEqual(result["check_status_counts"]["pending"], 1)

    def test_wrong_head_rejected(self):
        with self.assertRaisesRegex(ValueError, "different head"):
            mod.collect(lambda _: {"total_count": 1, "check_runs": [check(MAIN)]},
                        HEAD, MAIN, "now")

    def test_incomplete_page_is_unknown_not_zero(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            mod.collect(lambda _: {"total_count": 101, "check_runs": [check()]},
                        HEAD, MAIN, "now")

    def test_duplicate_check_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            mod.collect(lambda _: {"total_count": 2, "check_runs": [check(), check()]},
                        HEAD, MAIN, "now")

    def test_missing_required_gate_is_unknown(self):
        entry = check()
        entry["name"] = "Unrelated"
        result = mod.collect(lambda _: {"total_count": 1, "check_runs": [entry]},
                             HEAD, MAIN, "now")
        self.assertEqual(result["feedback_gate_observation"], "UNKNOWN")

    def test_invalid_sha_rejected_before_request(self):
        with self.assertRaises(ValueError):
            mod.collect(lambda _: self.fail("network should not execute"),
                        "short", MAIN, "now")

    def test_non_github_evidence_url_redacted(self):
        data = check()
        data["details_url"] = "https://evil.invalid/something"
        self.assertIsNone(mod.normalize_check(data, HEAD)["url"])


if __name__ == "__main__":
    unittest.main()
