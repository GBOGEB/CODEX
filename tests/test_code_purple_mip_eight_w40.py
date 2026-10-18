"""MIP W40: native local eight-point method, anti-double-credit and path locks."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "mission_control/mycelium/five_axis/CBD_MIP_W40_EIGHT_SECTION_REGISTER.json"
PUBLIC = ROOT / "docs/data/code_purple_cbd_mip_w40.json"
SCRIPT = ROOT / "scripts/code_purple_mip_eight_w40.py"
SPEC = importlib.util.spec_from_file_location("code_purple_mip_eight_w40", SCRIPT)
assert SPEC and SPEC.loader
mip = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mip)
HEAD = "c" * 40


def seed():
    return json.loads(ORIGINAL.read_text(encoding="utf-8"))


class EightSectionMIP(unittest.TestCase):
    def test_sanitized_source_public_parity(self):
        self.assertEqual(ORIGINAL.read_bytes(), PUBLIC.read_bytes())
        self.assertNotIn(b"fc07545c3986181a1b837c0eb7ff9a8393fd4058", PUBLIC.read_bytes())

    def test_eight_sections_explicit_mip_expansion(self):
        x = mip.validate(seed())
        self.assertEqual([r["id"] for r in x["sections"]], list(range(1, 9)))
        self.assertEqual(x["method"]["expansion"], ["Modernize", "Innovate", "Perpetuate"])
        self.assertEqual(x["phase_gates"]["perpetuate"][:8], "WITHHELD")

    def test_native_matched_actual_gain_only_once(self):
        x=seed()
        receipt=mip.evaluate(x, candidate_head=HEAD,
                             raw_sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest())
        r=receipt["measured_existing_source"]
        self.assertEqual((r["new_branches"],r["new_statements"]),(15,34))
        self.assertEqual(r["distinct_source_files"],1)
        self.assertAlmostEqual(r["native_branches_per_workflow_elapsed_minute_proxy"],
                               round(60*15/156,3))
        self.assertIsNone(r["runner_busy_minutes"])
        self.assertIsNone(r["current_main_global_coverage_delta"])
        self.assertEqual(receipt["mip_programme_dov"],"WITHHELD")
        self.assertEqual(receipt["code_purple_merge_admission"],"HOLD")

    def test_false_main_zero_or_mip_green_rejected(self):
        for owner,key,value in (("governance","merge_admission","PASS"),
                                ("governance","auto_merge",True),
                                ("governance","security_waiver",True),
                                ("governance","remote_dispatch",True),
                                ("method","qualified_global_dov","PASS")):
            with self.subTest(owner=owner,key=key):
                x=seed();x[owner][key]=value
                with self.assertRaises(ValueError):mip.validate(x)

    def test_missing_or_forged_private_qps_rejected(self):
        x=seed();x["sources"]["QPS"]["main_sha"]="f"*40
        with self.assertRaisesRegex(ValueError,"PRIVATE_QPS"):mip.validate(x)

    def test_stale_coverage_and_denominator_drift_rejected(self):
        for field,value in (("branches",35),("eligible_branches",37),
                            ("statements",96),("eligible_statements",98)):
            with self.subTest(field=field):
                x=seed();x["native"]["source_w38"]["expanded"][field]=value
                with self.assertRaisesRegex(ValueError,"W38_MEASURED_INVARIANT"):
                    mip.validate(x)

    def test_broad_main_credit_is_not_from_module(self):
        x=seed();x["native"]["source_w38"]["global_main_delta"]=0.5
        with self.assertRaisesRegex(ValueError,"W38_NATIVE_SCOPE"):mip.validate(x)

    def test_route_without_actual_evaluation_never_authorizes_skip(self):
        x=seed();x["native"]["route_w38"]["productive_skip_count"]=13
        with self.assertRaisesRegex(ValueError,"ROUTE_UNPROVEN_SUPPRESSION"):
            mip.validate(x)

    def test_cross_repo_same_path_allowed_but_not_owner(self):
        x=seed()
        x["parallel_lanes"][2]["paths"]=["ci/governance/feedback_route_yield_w38.py"]
        self.assertTrue(mip.validate(x))

    def test_same_repo_exact_and_prefix_overlap_rejected(self):
        for file in ("ci/governance/feedback_route_yield_w38.py",
                     "ci/governance", "ci/governance/feedback_route_yield_w38.py/inside"):
            with self.subTest(path=file):
                x=seed();x["parallel_lanes"][1]["paths"]=[file]
                with self.assertRaisesRegex(ValueError,"PATH_COLLISION"):
                    mip.validate(x)

    def test_unsafe_paths_and_duplicates_rejected(self):
        for path in ("../outside", "/absolute", "docs//x", "docs/./x"):
            with self.subTest(path=path):
                x=seed();x["parallel_lanes"][0]["paths"][0]=path
                with self.assertRaisesRegex(ValueError,"UNSAFE"):mip.validate(x)
        x=seed();x["parallel_lanes"][0]["paths"].append(x["parallel_lanes"][0]["paths"][0])
        with self.assertRaisesRegex(ValueError,"INVALID_LANE_PATHS"):mip.validate(x)

    def test_extra_item_and_duplicate_section_rejected(self):
        x=seed();x["sections"][6]["id"]=6
        with self.assertRaisesRegex(ValueError,"EIGHT_SECTION_POPULATION"):
            mip.validate(x)
        x=seed();x["sections"].append(copy.deepcopy(x["sections"][0]))
        with self.assertRaisesRegex(ValueError,"EIGHT_SECTION_POPULATION"):mip.validate(x)

    def test_decision_and_action_contract(self):
        x=seed();x["sections"][1]["decision"]="AUTO_MERGE"
        with self.assertRaisesRegex(ValueError,"MIP_SECTION_INCOMPLETE"):mip.validate(x)
        x=seed();x["sections"][2]["next"]=""
        with self.assertRaisesRegex(ValueError,"MIP_SECTION_INCOMPLETE"):mip.validate(x)

    def test_frozen_path_sets_are_not_active_runner_leases(self):
        receipt=mip.evaluate(seed(),candidate_head=HEAD,raw_sha256="a"*64)
        self.assertTrue(receipt["source_path_disjoint"])
        self.assertEqual(receipt["path_disjoint_evidence_class"],
                         "FROZEN_PR_DIFF_NOT_A_LEASE")
        self.assertFalse(receipt["live_current_pr_diff_verified"])
        self.assertIsNone(receipt["actual_free_worker_capacity"])
        modified=seed()
        modified["parallel_lanes"][0]["path_evidence_class"]="VERIFIED_LEASE"
        with self.assertRaisesRegex(ValueError,"PATH_SNAPSHOT_NOT_RUNNER_LOCK"):
            mip.validate(modified)
    def test_untrusted_candidate_head_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNPINNED_CANDIDATE_HEAD"):
            mip.evaluate(seed(),candidate_head="short",raw_sha256="a"*64)

    def test_native_cli_offline_eight_item_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            outfile=Path(d)/"summary.json"
            from unittest import mock
            with mock.patch("sys.argv", ["mip", "--register", str(ORIGINAL),
                                        "--candidate-head", HEAD,
                                        "--out",str(outfile)]):
                mip.main()
            payload=json.loads(outfile.read_text())
            self.assertEqual(payload["eight_section_denominator"],8)
            self.assertEqual(len(payload["decisions"]),8)
            self.assertFalse(payload["dispatch_permitted"])
            self.assertFalse(payload["authority_transfer"])
            self.assertEqual(payload["candidate_head"],HEAD)

    def test_read_only_source_avoids_opaque_magic_score(self):
        receipt=mip.evaluate(seed(),candidate_head=HEAD,raw_sha256="a"*64)
        self.assertNotIn("global_quality_score",receipt)
        self.assertNotIn("efficiency_percent",receipt)
        self.assertIsNone(receipt["actual_free_worker_capacity"])
        self.assertEqual(receipt["parallel_lanes_declared"],5)


if __name__=="__main__":
    unittest.main()
