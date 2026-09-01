import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "feedback" / "qps_w08_keb_candidate_return_receipt.yaml"
REQUEST = ROOT / "feedback" / "qps_w08_lifecycle_coverage_semantic_request.yaml"


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class TestQpsW08KebCandidateReturnReceipt(unittest.TestCase):
    def test_receipt_is_candidate_only_and_child_owned_for_disposition(self):
        data = load(RECEIPT)
        self.assertEqual(data["candidate_state"], "CANDIDATE_ONLY")
        self.assertEqual(data["child_disposition"], "UNSET")
        controls = data["control_boundary"]
        self.assertFalse(controls["parent_credit_promotion_allowed"])
        self.assertTrue(controls["child_acceptance_required"])
        self.assertFalse(controls["missing_hash_inference_allowed"])
        self.assertEqual(controls["formal_completion_delta"], 0)
        self.assertEqual(controls["bidder_compliance_delta"], 0)

    def test_receipt_is_bound_to_merged_parent_and_current_peer_lineage(self):
        data = load(RECEIPT)
        self.assertEqual(data["source_parent_pr"], "GBOGEB/CODEX#330")
        self.assertEqual(
            data["source_parent_merge_sha"], "a8525f61102d00cbbe5a7cbe832ac1573a86783c"
        )
        self.assertEqual(data["peer_abacus_latest_merged_repair_pr"], "GBOGEB/ABACUS#805")
        self.assertEqual(
            data["peer_abacus_latest_merged_repair_sha"],
            "1ce4815b82beacc6d63de4fae31ad79be3d8e724",
        )
        self.assertEqual(data["peer_abacus_predecessor_repair_pr"], "GBOGEB/ABACUS#802")
        self.assertEqual(
            data["peer_abacus_predecessor_repair_sha"],
            "98ddbeeb6fa1e1e099e40893ee2ef7de0ba64501",
        )
        self.assertEqual(
            data["peer_abacus_historical_predecessor_pr"], "GBOGEB/ABACUS#795"
        )
        self.assertEqual(
            data["peer_abacus_historical_predecessor_sha"],
            "83f1680e5405c082b414343dbdcad20ab8c9eac9",
        )

    def test_incomplete_runtime_hash_binding_fails_closed(self):
        data = load(RECEIPT)
        binding = data["runtime_binding"]
        self.assertFalse(binding["complete"])
        self.assertIsNone(binding["final_runtime_run_id"])
        self.assertIsNone(binding["runtime_artifact_id"])
        self.assertIsNone(binding["runtime_artifact_sha256"])
        self.assertIsNone(binding["semantic_result_artifact_id"])
        self.assertIsNone(binding["semantic_result_sha256"])
        self.assertIsNone(binding["release_manifest_sha256"])
        self.assertEqual(data["handoff_gate"]["state"], "CLOSED")

    def test_semantic_request_tracks_current_abacus_repair_lineage(self):
        request = load(REQUEST)
        self.assertEqual(
            request["source_abacus_latest_merged_repair_pr"], "GBOGEB/ABACUS#805"
        )
        self.assertEqual(
            request["source_abacus_latest_merged_repair_sha"],
            "1ce4815b82beacc6d63de4fae31ad79be3d8e724",
        )
        self.assertEqual(
            request["source_abacus_predecessor_repair_pr"], "GBOGEB/ABACUS#802"
        )
        self.assertEqual(
            request["source_abacus_predecessor_repair_sha"],
            "98ddbeeb6fa1e1e099e40893ee2ef7de0ba64501",
        )
        self.assertEqual(
            request["source_abacus_historical_predecessor_pr"], "GBOGEB/ABACUS#795"
        )
        self.assertEqual(
            request["source_abacus_historical_predecessor_sha"],
            "83f1680e5405c082b414343dbdcad20ab8c9eac9",
        )
