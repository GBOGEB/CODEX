import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "feedback" / "qps_w08_keb_candidate_return_receipt.yaml"
REQUEST = ROOT / "feedback" / "qps_w08_lifecycle_coverage_semantic_request.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "codex_semantic_runtime_ci.yml"


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

    def test_receipt_tracks_current_parent_and_peer_runtime_lineage(self):
        data = load(RECEIPT)
        self.assertEqual(data["source_parent_pr"], "GBOGEB/CODEX#337")
        self.assertEqual(
            data["source_parent_merge_sha"],
            "0dd4ff3e40e0ee03dcd8814b549aeb1e2ec00a40",
        )
        self.assertEqual(data["peer_abacus_latest_merged_repair_pr"], "GBOGEB/ABACUS#811")
        self.assertEqual(
            data["peer_abacus_latest_merged_repair_sha"],
            "22dd6be9ca3fb9c0d8df9c9f524ba43d4ac52c74",
        )

    def test_self_artifact_identity_is_explicitly_post_upload(self):
        data = load(RECEIPT)
        contract = data["binding_contract"]
        binding = data["runtime_binding"]
        self.assertEqual(contract["mode"], "TWO_PHASE_POST_UPLOAD_SELF_BINDING")
        self.assertTrue(contract["child_must_pair_payload_and_binding"])
        self.assertTrue(contract["same_run_id_required"])
        self.assertTrue(contract["same_commit_sha_required"])
        self.assertFalse(contract["payload_self_id_may_be_inferred"])
        self.assertEqual(binding["runtime_artifact_id"], "POST_UPLOAD_EXTERNAL_BINDING")
        self.assertEqual(binding["runtime_artifact_sha256"], "POST_UPLOAD_EXTERNAL_BINDING")
        self.assertTrue(binding["post_upload_binding_required"])
        self.assertEqual(data["handoff_gate"]["state"], "TEMPLATE")

    def test_runtime_workflow_publishes_payload_then_post_upload_binding(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        payload_upload = text.index("Upload QPS W08 KEB runtime return")
        binding_build = text.index("Build post-upload KEB binding")
        binding_upload = text.index("Upload post-upload KEB binding")
        self.assertLess(payload_upload, binding_build)
        self.assertLess(binding_build, binding_upload)
        self.assertIn("steps.upload_keb_payload.outputs.artifact-id", text)
        self.assertIn("steps.upload_keb_payload.outputs.artifact-digest", text)
        self.assertIn('"runtime_artifact_id": artifact_id', text)
        self.assertIn('"runtime_artifact_digest": artifact_digest', text)

    def test_semantic_request_preserves_historical_lineage_without_credit(self):
        request = load(REQUEST)
        self.assertEqual(
            request["source_abacus_latest_merged_repair_pr"], "GBOGEB/ABACUS#805"
        )
        self.assertEqual(
            request["source_abacus_latest_merged_repair_sha"],
            "1ce4815b82beacc6d63de4fae31ad79be3d8e724",
        )
