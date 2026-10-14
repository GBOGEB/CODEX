"""Offline source-contract regression tests; passing is not native CI admission."""
import unittest
from dataclasses import replace

from temporal_matrix import (
    Metric, admission_gate, comparable_delta, masked_first_difference, rebase_index
)

SHA0 = "a" * 40
SHA1 = "b" * 40


def metric(value, sha=SHA0, utc="2026-10-14T15:00:00Z"):
    return Metric(
        value=value, unit="Ruff finding occurrence", repository="GBOGEB/ABACUS",
        source_sha=sha, producer="ruff==0.17.0",
        config_digest="config:matched", scope_digest="scope:four-files",
        observed_at_utc=utc,
    )


def later(value):
    return metric(value, SHA1, "2026-10-14T15:36:00Z")


class TemporalContractTests(unittest.TestCase):
    def test_free_origin_rebase(self):
        self.assertEqual([rebase_index(x, -10) for x in (-10, 0, 1)], [0, 10, 11])

    def test_bool_is_not_integer_ordinal(self):
        with self.assertRaises(ValueError):
            rebase_index(True, 0)

    def test_native_scoped_ruff_finding_delta(self):
        self.assertEqual(comparable_delta(metric(11), later(0)), -11.0)

    def test_zero_is_not_unknown(self):
        self.assertEqual(comparable_delta(metric(0), later(0)), 0.0)

    def test_missing_measurement_stays_null(self):
        self.assertIsNone(comparable_delta(metric(None), later(0)))

    def test_changed_scope_blocks_comparison(self):
        self.assertIsNone(comparable_delta(metric(11), replace(later(0), scope_digest="other")))

    def test_changed_config_blocks_comparison(self):
        self.assertIsNone(comparable_delta(metric(11), replace(later(0), config_digest="other")))

    def test_changed_denominator_blocks_comparison(self):
        self.assertIsNone(comparable_delta(metric(11), replace(later(0), denominator=12)))

    def test_changed_repository_blocks_comparison(self):
        self.assertIsNone(comparable_delta(metric(11), replace(later(0), repository="GBOGEB/CODEX")))

    def test_same_source_sha_not_a_transition(self):
        self.assertIsNone(comparable_delta(metric(11), metric(0, utc="2026-10-14T15:36:00Z")))

    def test_reverse_chronology_rejected(self):
        self.assertIsNone(comparable_delta(later(0), metric(11)))

    def test_invalid_full_sha_rejected(self):
        with self.assertRaises(ValueError):
            metric(11, sha="a" * 7)

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            metric(11, utc="2026-10-14T15:00:00")

    def test_zero_denominator_rejected(self):
        with self.assertRaises(ValueError):
            replace(metric(11), denominator=0)

    def test_masked_matrix_preserves_null(self):
        self.assertEqual(
            masked_first_difference(
                [[11, None, 50], [0, None, 51]], [[True, False, False]]
            ), [[-11.0, None, None]]
        )

    def test_bad_mask_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            masked_first_difference([[1, 2], [0, 1]], [[True]])

    def test_gate_hold_on_unknown(self):
        all_true = {key: True for key in (
            "exact_head", "native_tests", "security", "independent_review",
            "effective_protection", "required_ci",
        )}
        self.assertEqual(admission_gate({**all_true, "effective_protection": None}), "HOLD")

    def test_gate_success_not_merge(self):
        all_true = {key: True for key in (
            "exact_head", "native_tests", "security", "independent_review",
            "effective_protection", "required_ci",
        )}
        self.assertEqual(admission_gate(all_true), "ELIGIBLE_FOR_SEPARATE_OWNER_DECISION")


if __name__ == "__main__":
    unittest.main()
