"""Adversarial checks for false-green, stale binding and PR body preservation."""

import copy
import unittest

from qps_aht_control import (digest, evaluate, snapshot, update_pr_body,
                             validate_snapshot)


class ControlTests(unittest.TestCase):
    def result(self, counts, **kwargs):
        return evaluate(counts, coverage_complete=True, unresolved_reviews=0, **kwargs)

    def test_empty_is_unknown(self):
        result = self.result({})
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["observed"]["failure_rate"])

    def test_every_blocking_conclusion(self):
        for outcome in ("failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"):
            with self.subTest(outcome=outcome):
                self.assertEqual(self.result({outcome: 1})["status"], "THRESHOLD_BREACHED")

    def test_pending_does_not_enter_failure_denominator(self):
        result = self.result({"success": 2, "queued": 8})
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["observed"]["decisive"], 2)

    def test_below_alert_threshold_still_holds(self):
        self.assertEqual(self.result({"failure": 1}, threshold=2)["status"], "HOLD")

    def test_missing_review_or_coverage_is_unknown(self):
        self.assertEqual(evaluate({"success": 3})["status"], "UNKNOWN")
        self.assertEqual(evaluate({"success": 3}, coverage_complete=True)["status"], "UNKNOWN")

    def test_review_blocks(self):
        self.assertEqual(evaluate({"success": 3}, coverage_complete=True,
                                  unresolved_reviews=1)["status"], "HOLD")

    def test_skipped_neutral_unknown_do_not_clear(self):
        for kind in ("skipped", "neutral", "unknown"):
            self.assertEqual(self.result({"success": 1, kind: 1})["status"], "UNKNOWN")

    def test_clear_is_not_release(self):
        result = self.result({"success": 3})
        self.assertEqual(result["status"], "CHECKS_CLEAR")
        self.assertFalse(result["release_accepted"])

    def test_invalid_counts_and_thresholds(self):
        for counts in ({"success": -1}, {"success": True}, {"success": 1.1}, {"misspelled": 1}):
            with self.assertRaises(ValueError):
                self.result(counts)
        for threshold in (0, True, 1.5):
            with self.assertRaises(ValueError):
                self.result({}, threshold=threshold)

    def payload(self):
        return snapshot("GBOGEB/CODEX", "a" * 40, "2026-09-15T00:00:00Z",
                        {"success": 2}, coverage_complete=True, unresolved_reviews=0)

    def validate(self, payload, **overrides):
        options = dict(repository="GBOGEB/CODEX", head_sha="a" * 40,
                       expected_digest=digest(payload), now="2026-09-15T00:10:00Z")
        options.update(overrides)
        return validate_snapshot(payload, **options)

    def test_valid_roundtrip(self):
        self.assertEqual(self.validate(self.payload()), "CHECKS_CLEAR")

    def test_external_sha_and_repo_required(self):
        for options in ({"head_sha": "b" * 40}, {"repository": "GBOGEB/ABACUS"}):
            with self.assertRaises(ValueError):
                self.validate(self.payload(), **options)

    def test_detached_hash_binding(self):
        with self.assertRaises(ValueError):
            self.validate(self.payload(), expected_digest="0" * 64)

    def test_expired_and_future(self):
        for now in ("2026-09-16T00:00:00Z", "2026-09-14T00:00:00Z"):
            with self.assertRaises(ValueError):
                self.validate(self.payload(), now=now)

    def test_rehashed_tampering_is_rejected(self):
        for key, value in (("status", "ACCEPTED"), ("release_accepted", True), ("schema", "wrong")):
            payload = copy.deepcopy(self.payload())
            payload[key] = value
            with self.assertRaises(ValueError):
                self.validate(payload)

    def test_body_replacement_is_idempotent(self):
        original = "## Governance\nKeep this body, links and checklist.\n"
        first = update_pr_body(original, self.payload())
        self.assertTrue(first.endswith(original))
        self.assertEqual(update_pr_body(first, self.payload()), first)

    def test_malformed_markers_rejected(self):
        with self.assertRaises(ValueError):
            update_pr_body("<!-- qps-aht-control:start -->human content", self.payload())


if __name__ == "__main__":
    unittest.main()
