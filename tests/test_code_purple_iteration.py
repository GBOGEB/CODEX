"""Fail-closed tests for the advisory Code Purple iteration projector."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "scripts" / "code_purple_iteration.py"
SPEC = importlib.util.spec_from_file_location("code_purple_iteration", FILE)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
SHA_A = "a" * 40
SHA_B = "b" * 40


def sample():
    return {
        "repo": "GBOGEB/CODEX",
        "observed_head_sha": SHA_A,
        "current_head_sha": SHA_A,
        "checks": [{"name": "test", "status": "completed", "conclusion": "success", "completed_order": 1}],
        "required_checks": ["test"],
        "executed_steps": 3,
        "code_review_complete": True,
        "security_review_complete": True,
        "unresolved_threads": 0,
    }


class CodePurpleIterationTest(unittest.TestCase):
    def test_candidate_not_native_merge_credit(self):
        result = mod.project(sample())
        self.assertEqual(result["classification"], "ADMISSION_CANDIDATE")
        self.assertEqual(result["repository_native_admission"], "NOT_GRANTED")
        self.assertFalse(result["authority_transfer"])

    def test_stale_head_fail_closed(self):
        data = sample()
        data["current_head_sha"] = SHA_B
        self.assertEqual(mod.project(data)["next_action"], "REFRESH_EXACT_HEAD")

    def test_zero_step_not_pass(self):
        data = sample()
        data["executed_steps"] = 0
        self.assertEqual(mod.project(data)["classification"], "HOLD")

    def test_review_or_security_not_inferred(self):
        for key in ("code_review_complete", "security_review_complete"):
            with self.subTest(key=key):
                data = sample()
                data[key] = False
                self.assertEqual(mod.project(data)["classification"], "HOLD")

    def test_unresolved_thread_holds(self):
        data = sample()
        data["unresolved_threads"] = 1
        self.assertEqual(mod.project(data)["classification"], "HOLD")

    def test_skipped_or_neutral_not_green(self):
        for conclusion in ("skipped", "neutral", None):
            with self.subTest(conclusion=conclusion):
                data = sample()
                data["checks"][0]["conclusion"] = conclusion
                self.assertEqual(mod.project(data)["classification"], "HOLD")

    def test_first_material_completed_red_not_pending(self):
        data = sample()
        data["checks"] = [
            {"name": "pending", "status": "queued", "conclusion": None},
            {"name": "late", "status": "completed", "conclusion": "failure", "completed_order": 9},
            {"name": "first", "status": "completed", "conclusion": "failure", "completed_order": 2},
        ]
        data["required_checks"] = ["pending"]
        result = mod.project(data)
        self.assertEqual(result["classification"], "REPAIR_REENTRY")
        self.assertEqual(result["first_material_red"], "first")

    def test_unmaterial_red_ignored(self):
        data = sample()
        data["checks"].append({"name": "unrelated", "status": "completed", "conclusion": "failure", "material": False})
        self.assertEqual(mod.project(data)["classification"], "ADMISSION_CANDIDATE")

    def test_no_unnecessary_mip_or_propagation(self):
        data = sample()
        self.assertEqual(mod.project(data)["method_path"], ["3PR"])
        data["structural_gap_observed"] = True
        data["transaction_required"] = True
        data["local_dov_proven"] = True
        data["generalisation_gap_observed"] = True
        self.assertEqual(mod.project(data)["method_path"], ["3PR", "MIP", "3PC", "3P3"])

    def test_pay_forward_requires_consumer_proof(self):
        data = sample()
        data.update(
            pay_it_forward_requested=True, local_dov_proven=True,
            generalisation_gap_observed=True, sanitized=True,
            consumer_independent_proof=False, consumer_accepted=True,
        )
        self.assertEqual(mod.project(data)["pay_it_forward"], "CONSUMER_PENDING")

    def test_invalid_sha_or_duplicate_check_rejected(self):
        data = sample()
        data["observed_head_sha"] = "main"
        with self.assertRaises(ValueError):
            mod.project(data)
        data = sample()
        data["checks"].append(data["checks"][0].copy())
        with self.assertRaises(ValueError):
            mod.project(data)


if __name__ == "__main__":
    unittest.main()
