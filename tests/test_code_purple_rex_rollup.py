"""Fail-closed evidence, ranking and telemetry tests for CODE PURPLE REX."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "scripts" / "code_purple_rex_rollup.py"
SPEC = importlib.util.spec_from_file_location("code_purple_rex_rollup", FILE)
assert SPEC is not None and SPEC.loader is not None
rex = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rex)


class CandidateREXRollupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = rex.SOURCE.read_bytes()
        cls.data = yaml.safe_load(cls.raw)

    def test_eight_observed_signatures_are_candidate_not_global_credit(self):
        report = rex.make_rollup(self.data, self.raw)
        self.assertEqual(report["metrics"]["candidate_rex_signatures"], 8)
        self.assertEqual(report["metrics"]["open_or_deferred_candidate_signatures"], 4)
        self.assertEqual(report["metrics"]["repaired_not_yet_verified"], 3)
        self.assertEqual(report["metrics"]["verified_or_controlled_candidate_signatures"], 0)
        self.assertEqual(report["metrics"]["source_declared_verified_or_controlled_signatures"], 1)
        self.assertEqual(report["metrics"]["verification_pending_candidate_signatures"], 1)
        self.assertEqual(report["metrics"]["candidate_rex_control_status"]["VERIFICATION_PENDING"], 1)
        claimed = next(r for r in report["ranked_rex_candidates"]
                       if r["source_claimed_control_status"] == "VERIFIED")
        self.assertEqual(claimed["control_status"], "VERIFICATION_PENDING")
        self.assertIn("WITHHELD", claimed["verification_result"])
        self.assertEqual(report["admission"]["glob_rex_promotion"], "PENDING_INDEPENDENT_REVIEW")
        self.assertFalse(report["admission"]["authority_transfer"])

    def test_top_7_14_21_are_capacity_views_not_distinct_measurement_windows(self):
        report = rex.make_rollup(self.data, self.raw)
        self.assertEqual(report["top7_14_21"]["7"]["populated"], 7)
        self.assertEqual(report["top7_14_21"]["14"]["populated"], 8)
        self.assertEqual(report["top7_14_21"]["21"]["unfilled_slots"], 13)
        self.assertEqual(report["top7_14_21"]["7"]["records"][0],
                         "REX-ABACUS-20261012-001")
        self.assertEqual(report["top7_14_21"]["7"]["records"][1],
                         "REX-ABACUS-20261012-002")

    def test_heterogeneous_frequency_units_are_not_summed(self):
        report = rex.make_rollup(self.data, self.raw)
        metrics = report["metrics"]
        self.assertIsNone(metrics["frequency_total"])
        self.assertEqual(metrics["frequency_by_incompatible_unit"]["lint_violations_in_one_failed_job"], 25)
        self.assertEqual(metrics["frequency_total_state"], "WITHHELD_HETEROGENEOUS_UNITS")

    def test_current_health_coverage_bd_and_launch_unknown_not_zero(self):
        m = rex.make_rollup(self.data, self.raw)["metrics"]
        for field in ("bd_queue_open", "bd_queue_closed", "actual_root_cause_queue_open",
                      "actual_root_cause_queue_closed", "authenticated_crew_launches",
                      "current_main_coverage_pct", "current_diff_coverage_pct",
                      "current_pr_broad_coverage_pct", "measured_pca_score"):
            self.assertIsNone(m[field], field)
        self.assertEqual(m["missing_value_state"], "UNKNOWN_NOT_ZERO")

    def test_historical_baselines_not_merged_into_current_readings(self):
        r = rex.make_rollup(self.data, self.raw)
        self.assertEqual(r["historical_coverage_baselines"]["main_2026_10_11"]["value_pct"], 36.85)
        self.assertEqual(r["historical_coverage_baselines"]["pr_diff_2026_10_12"]["value_pct"], 51)
        self.assertIsNone(r["historical_coverage_baselines"]["comparable_current_delta"])

    def test_duplicate_signature_or_id_rejected(self):
        d = deepcopy(self.data)
        d["records"][1]["signature"] = d["records"][0]["signature"]
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)
        d = deepcopy(self.data)
        d["records"][1]["rex_id"] = d["records"][0]["rex_id"]
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)

    def test_invalid_sha_and_security_promotion_rejected(self):
        d = deepcopy(self.data)
        d["repo_state"]["head_sha"] = "ff1dbad"
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)
        d = deepcopy(self.data)
        d["repo_state"]["security_review_admission"] = "PASS"
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)
        d = deepcopy(self.data)
        d["return_contract"]["authority_transfer"] = True
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)

    def test_no_fake_verified_without_pass(self):
        d = deepcopy(self.data)
        d["records"][0]["control_status"] = "VERIFIED"
        d["summary"]["open_or_deferred"] -= 1
        d["summary"]["verified_or_controlled"] += 1
        d["summary"]["five_star_open"] -= 1
        with self.assertRaisesRegex(ValueError, "PASS"):
            rex.make_rollup(d, self.raw)

    def test_evidence_url_and_nonzero_count_required(self):
        d = deepcopy(self.data)
        d["records"][0]["verification"]["source_url"] = "http://example.org/unsafe"
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)
        d = deepcopy(self.data)
        d["records"][0]["frequency"]["observed_count"] = 0
        with self.assertRaises(ValueError):
            rex.make_rollup(d, self.raw)

    def test_determinism_and_canonical_bytes_required(self):
        a = rex.make_rollup(self.data, self.raw)
        b = rex.make_rollup(self.data, self.raw)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        changed_bytes = self.raw + b"\n# provenance-comment\n"
        with self.assertRaisesRegex(ValueError, "canonical"):
            rex.make_rollup(self.data, changed_bytes)

    def test_alternative_source_even_identical_bytes_is_rejected(self):
        data, raw = rex.load_canonical_source(rex.SOURCE)
        self.assertEqual(data, self.data)
        self.assertEqual(raw, self.raw)
        with tempfile.TemporaryDirectory() as folder:
            alternative = Path(folder) / "forged_return.yaml"
            alternative.write_bytes(self.raw)
            with self.assertRaisesRegex(ValueError, "noncanonical"):
                rex.load_canonical_source(alternative)

    def test_unreviewed_security_pass_cannot_upgrade_to_verified(self):
        forged = deepcopy(self.data)
        first = forged["records"][0]
        first["control_status"] = "VERIFIED"
        first["verification"]["result"] = "PASS_I_SAY_SO"
        first["verification"]["green_head_sha"] = "a" * 40
        first["verification"]["green_run_id"] = 1
        forged["summary"]["open_or_deferred"] -= 1
        forged["summary"]["five_star_open"] -= 1
        forged["summary"]["verified_or_controlled"] += 1
        self.assertEqual(rex.effective_control_status(first), "VERIFICATION_PENDING")
        with self.assertRaisesRegex(ValueError, "canonical"):
            rex.make_rollup(forged, self.raw)

    def test_artifact_name_is_exact_checked_out_head_not_merge_ref(self):
        workflow = (ROOT / ".github/workflows/code-purple-rex-control.yml").read_text(
            encoding="utf-8"
        )
        head_expr = "github.event.pull_request.head.sha || github.sha"
        self.assertIn("name: code-purple-rex-candidate-${{ " + head_expr + " }}", workflow)
        self.assertNotIn("name: code-purple-rex-candidate-${{ github.sha }}", workflow)

    def test_read_only_cli_materialize_then_check_without_repo_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "source.json"
            payload = rex.make_rollup(self.data, self.raw)
            output.write_text(json.dumps(payload, sort_keys=True, indent=2,
                                         ensure_ascii=False) + "\n", encoding="utf-8")
            self.assertEqual(json.loads(output.read_text())["schema"], rex.SCHEMA)


if __name__ == "__main__":
    unittest.main()
