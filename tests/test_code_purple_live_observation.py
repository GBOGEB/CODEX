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
        "started_at": "2026-10-12T10:00:00Z",
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
        pending["started_at"] = "2026-10-12T11:00:00Z"
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

    def test_latest_success_overrides_older_cancelled_gate(self):
        older = check(conclusion="cancelled")
        newer = check(number=6)
        newer["started_at"] = "2026-10-12T11:00:00Z"
        result = mod.collect(
            lambda _: {"total_count": 2, "check_runs": [older, newer]},
            HEAD, MAIN, "now",
        )
        self.assertEqual(result["feedback_gate_observation"],
                         "SUCCESS_OBSERVED_UNVERIFIED")
        self.assertEqual(result["current_feedback_gate_check_id"], 6)
        self.assertEqual(result["check_status_counts"]["cancelled"], 1)

    def test_unordered_gate_timestamps_fail_closed(self):
        other = check(number=6)
        result = mod.collect(
            lambda _: {"total_count": 2, "check_runs": [check(), other]},
            HEAD, MAIN, "now",
        )
        self.assertEqual(result["feedback_gate_observation"],
                         "UNKNOWN_UNORDERED_GATE")
        self.assertIsNone(result["current_feedback_gate_check_id"])

    def test_all_terminal_conclusions_preserve_denominator(self):
        kinds = ["success", "failure", "cancelled", "skipped",
                 "timed_out", "neutral", "action_required",
                 "stale", "startup_failure", "unexpected_terminal", None]
        items = []
        for index, kind in enumerate(kinds):
            row = check(conclusion=kind, number=index + 1)
            row["name"] = "Unrelated"
            items.append(row)
        result = mod.collect(
            lambda _: {"total_count": len(items), "check_runs": items},
            HEAD, MAIN, "now",
        )
        counts = result["check_status_counts"]
        self.assertEqual(sum(counts.values()), len(kinds))
        self.assertEqual(counts["timed_out"], 1)
        self.assertEqual(counts["other"], 1)
        self.assertEqual(counts["pending"], 1)

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
