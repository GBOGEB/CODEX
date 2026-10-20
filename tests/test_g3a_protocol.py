"""Negative/positive controls for governed three-step receipt reconciliation."""

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "g3a_protocol.py"
SPEC = importlib.util.spec_from_file_location("g3a_protocol", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
SHA_D = "d" * 40
POLICY = "e" * 64


def plan():
    return {
        "schema": mod.PLAN_SCHEMA,
        "mission_id": "G3A-sample",
        "mode": "G3A",
        "repository": "GBOGEB/ABACUS",
        "wave_id": "W1",
        "objective": "Reduce source-bound first-red uncertainty",
        "source_sha": SHA_A,
        "policy_sha256": POLICY,
        "step_budget": 3,
        "execution_mode": "sequential_pulses",
        "max_read_scouts": 4,
        "max_write_workers": 2,
        "allowed_actions": ["inspect", "test", "edit_owned", "collect_receipt"],
        "stop_on": sorted(mod.MANDATORY_STOPS),
        "steps": [
            {"pulse_id": "P1", "intent": "Measure"},
            {"pulse_id": "P2", "intent": "Improve"},
            {"pulse_id": "P3", "intent": "Verify"},
        ],
        "parallel_slices": [
            {"owner": "docs", "write_paths": ["docs/ci/"]},
            {"owner": "tests", "write_paths": ["tests/test_g3a.py"]},
        ],
    }


def receipt(pulse, before, after, result="MEASURED"):
    return {
        "schema": mod.PULSE_SCHEMA,
        "mission_id": "G3A-sample",
        "pulse_id": pulse,
        "input_sha": before,
        "output_sha": after,
        "policy_sha256": POLICY,
        "result": result,
        "actions": ["inspect", "test"],
        "independent_admission": False,
        "checks": [
            {"name": "native smoke", "status": "PASS",
             "evidence_ref": "https://github.com/GBOGEB/ABACUS/actions/runs/1"}
        ],
        "major_blocker": None,
    }


class G3AProtocolTests(unittest.TestCase):
    def test_three_evaluated_not_admitted(self):
        rows = [
            receipt("P1", SHA_A, SHA_B),
            receipt("P2", SHA_B, SHA_C),
            receipt("P3", SHA_C, SHA_D),
        ]
        report = mod.reconcile(plan(), rows)
        self.assertEqual(report["evaluated_pulses"], 3)
        self.assertEqual(report["last_reconciled_sha"], SHA_D)
        self.assertEqual(report["source_linked_measured_pulses"], 3)
        self.assertTrue(report["target_evaluated"])
        self.assertEqual(report["merge_admission"], "HOLD")
        self.assertEqual(report["independently_accepted_pulses"], 0)

    def test_partial_reconcile(self):
        report = mod.reconcile(plan(), [receipt("P1", SHA_A, SHA_B)])
        self.assertEqual(report["next_pulse"], "P2")
        self.assertFalse(report["target_evaluated"])

    def test_moving_head_stops(self):
        report = mod.reconcile(
            plan(), [receipt("P1", SHA_A, SHA_B), receipt("P2", SHA_C, SHA_D)]
        )
        self.assertEqual(report["stop_reason"], "HEAD_DRIFT")
        self.assertEqual(report["last_reconciled_sha"], SHA_B)

    def test_policy_drift_stops(self):
        row = receipt("P1", SHA_A, SHA_B)
        row["policy_sha256"] = "f" * 64
        self.assertEqual(mod.reconcile(plan(), [row])["stop_reason"], "POLICY_DRIFT")

    def test_major_blocker_stops(self):
        row = receipt("P1", SHA_A, SHA_A, result="HOLD")
        row["major_blocker"] = "P0_P1_SECURITY"
        report = mod.reconcile(plan(), [row, receipt("P2", SHA_A, SHA_B)])
        self.assertEqual(report["evaluated_pulses"], 1)
        self.assertEqual(report["stop_reason"], "P0_P1_SECURITY")

    def test_missing_receipts_are_not_pass(self):
        report = mod.reconcile(plan(), [])
        self.assertEqual(report["evaluated_pulses"], 0)
        self.assertIsNone(report["stop_reason"])
        self.assertEqual(report["merge_admission"], "HOLD")

    def test_merge_permission_is_forbidden(self):
        p = plan()
        p["allowed_actions"].append("merge")
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            mod.validate_plan(p)

    def test_missing_hard_stop_is_forbidden(self):
        p = plan()
        p["stop_on"].remove("MISSING_PROOF")
        with self.assertRaisesRegex(ValueError, "mandatory"):
            mod.validate_plan(p)

    def test_overlapping_slice_paths_rejected(self):
        p = plan()
        p["parallel_slices"][1]["write_paths"] = ["docs/ci/report.md"]
        with self.assertRaisesRegex(ValueError, "collision"):
            mod.validate_plan(p)

    def test_unsafe_path_rejected(self):
        p = plan()
        p["parallel_slices"][1]["write_paths"] = ["../secrets"]
        with self.assertRaisesRegex(ValueError, "unsafe"):
            mod.validate_plan(p)

    def test_alias_path_collision_rejected(self):
        p = plan()
        p["parallel_slices"][1]["write_paths"] = ["./docs/ci/"]
        with self.assertRaisesRegex(ValueError, "unsafe"):
            mod.validate_plan(p)

    def test_excessive_write_fanout_rejected(self):
        p = plan()
        p["max_write_workers"] = 1
        with self.assertRaisesRegex(ValueError, "write budget"):
            mod.validate_plan(p)

    def test_unverified_success_rejected(self):
        row = receipt("P1", SHA_A, SHA_B)
        row["checks"] = [{"name": "not actually run", "status": "NOT_RUN"}]
        with self.assertRaisesRegex(ValueError, "MEASURED requires"):
            mod.reconcile(plan(), [row])

    def test_missing_evidence_reference_rejected(self):
        row = receipt("P1", SHA_A, SHA_B)
        del row["checks"][0]["evidence_ref"]
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            mod.reconcile(plan(), [row])

    def test_synthetic_independent_admission_rejected(self):
        row = receipt("P1", SHA_A, SHA_B)
        row["independent_admission"] = True
        with self.assertRaisesRegex(ValueError, "cannot assert"):
            mod.reconcile(plan(), [row])

    def test_out_of_order_pulses_rejected(self):
        with self.assertRaisesRegex(ValueError, "foreign mission or pulse"):
            mod.reconcile(plan(), [receipt("P2", SHA_A, SHA_B)])

    def test_fourth_pulse_rejected(self):
        with self.assertRaisesRegex(ValueError, "at most three"):
            mod.reconcile(plan(), [
                receipt("P1", SHA_A, SHA_B), receipt("P2", SHA_B, SHA_C),
                receipt("P3", SHA_C, SHA_D), receipt("P4", SHA_D, SHA_D),
            ])

    def test_forged_policy_digest_rejected(self):
        p = plan()
        p["policy_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "canonical lowercase"):
            mod.validate_plan(p)


    def test_mixed_terminal_and_pending_checks_cannot_claim_measured(self):
        for bad_status in ("FAIL", "HOLD", "NOT_RUN"):
            with self.subTest(status=bad_status):
                row = receipt("P1", SHA_A, SHA_B)
                row["checks"].append({
                    "name": "independent security",
                    "status": bad_status,
                    "evidence_ref": "https://github.com/GBOGEB/ABACUS/actions/runs/2",
                })
                with self.assertRaisesRegex(ValueError, "all checks PASS"):
                    mod.reconcile(plan(), [row])

    def test_zero_checks_cannot_claim_measured(self):
        row = receipt("P1", SHA_A, SHA_B)
        row["checks"] = []
        with self.assertRaisesRegex(ValueError, "all checks PASS"):
            mod.reconcile(plan(), [row])

    def test_homogeneous_two_pass_checks_still_measure_without_admission(self):
        row = receipt("P1", SHA_A, SHA_B)
        row["checks"].append({
            "name": "second native check",
            "status": "PASS",
            "evidence_ref": "https://github.com/GBOGEB/ABACUS/actions/runs/3",
        })
        report = mod.reconcile(plan(), [row])
        self.assertEqual(report["source_linked_measured_pulses"], 1)
        self.assertEqual(report["merge_admission"], "HOLD")


if __name__ == "__main__":
    unittest.main()
