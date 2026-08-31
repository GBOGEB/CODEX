import copy
import unittest

from scripts import validate_ssot_style_bridge as validator


class TestValidateSsotStyleBridge(unittest.TestCase):
    def setUp(self):
        self.manifest = validator.load_manifest(validator.DEFAULT_MANIFEST)

    def test_manifest_is_valid(self):
        self.assertEqual([], validator.validate_manifest(self.manifest))

    def test_pca_axes_must_stay_reversed_for_catchup(self):
        broken = copy.deepcopy(self.manifest)
        broken["pca_axes"] = list(reversed(broken["pca_axes"]))
        errors = validator.validate_manifest(broken)
        self.assertIn("pca_axes must be ordered P5 to P1", errors)

    def test_federation_consumers_bind_public_and_private_repos(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["controlled_adapter"] = "public-export"
        errors = validator.validate_manifest(broken)
        self.assertIn("controlled adapter must be GBOGEB/cryoplant-project", errors)

    def test_federation_consumers_require_method_order(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["method_order"] = ["BT_PRIORITY", "DMAIC"]
        errors = validator.validate_manifest(broken)
        self.assertIn("method_order must be DMAIC, PCA_REVERSED_P5_TO_P1, BT_PRIORITY", errors)

    def test_federation_consumers_require_wave_id(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["wave_id"] = "SSOT-STYLE-W03"
        errors = validator.validate_manifest(broken)
        self.assertIn("federation consumer wave_id must be SSOT-STYLE-W04", errors)

    def test_federation_consumers_require_public_consumer(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["public_consumer"] = "GBOGEB/CODEX"
        errors = validator.validate_manifest(broken)
        self.assertIn("public consumer must be GBOGEB/ABACUS", errors)

    def test_federation_consumers_require_all_shared_lanes(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["shared_lanes"] = [
            lane for lane in broken["federation_consumers"]["shared_lanes"] if lane != "keb"
        ]
        errors = validator.validate_manifest(broken)
        self.assertIn("missing federation shared lane(s): keb", errors)

    def test_federation_consumers_reject_non_list_contract_fields(self):
        broken = copy.deepcopy(self.manifest)
        broken["federation_consumers"]["shared_lanes"] = "html,pdf"
        broken["federation_consumers"]["method_order"] = "DMAIC"
        errors = validator.validate_manifest(broken)
        self.assertIn("federation_consumers.shared_lanes must be a list of strings", errors)
        self.assertIn("federation_consumers.method_order must be a list of strings", errors)

    def test_handoff_check_policy_requires_repair_pr_links(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"]["linked_repair_prs"]["GBOGEB/ABACUS"] = [730]
        errors = validator.validate_manifest(broken)
        self.assertIn("linked repair PR(s) missing for GBOGEB/ABACUS: 754, 756", errors)

    def test_handoff_check_policy_blocks_known_failure_states(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"]["blocking_conclusions"].remove("action_required")
        broken["handoff_check_policy"]["manual_review_conclusions"] = []
        broken["handoff_check_policy"]["pending_statuses"].remove("queued")
        errors = validator.validate_manifest(broken)
        self.assertIn("missing blocking conclusion(s): action_required", errors)
        self.assertIn("missing manual-review conclusion(s): cancelled", errors)
        self.assertIn("missing pending status(es): queued", errors)

    def test_handoff_check_policy_requires_bidirectional_feedback(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"]["repository_feedback"] = {
            "from_abacus": "",
            "to_abacus": "",
        }
        errors = validator.validate_manifest(broken)
        self.assertIn("repository_feedback.from_abacus must be a non-empty string", errors)
        self.assertIn("repository_feedback.to_abacus must be a non-empty string", errors)

    def test_awake_score_counts_existing_probe_paths(self):
        score = validator.score_awake_probes(self.manifest)
        self.assertGreaterEqual(score["score"], 90.0)
        self.assertIn("ci", score["by_kind"])

    def test_penetration_score_separates_depth_from_presence(self):
        report = validator.score_penetration(self.manifest)
        self.assertGreaterEqual(report["score"], 80.0)
        self.assertIn("keb", report["by_kind"])
        self.assertLessEqual(report["by_kind"]["keb"]["depth"], report["by_kind"]["keb"]["total"])

    def test_handoff_policy_blocks_startup_failure_and_stale(self):
        broken = copy.deepcopy(self.manifest)
        policy = broken["handoff_check_policy"]
        policy["blocking_conclusions"].remove("startup_failure")
        policy["blocking_conclusions"].remove("stale")
        errors = validator.validate_manifest(broken)
        self.assertIn("missing blocking conclusion(s): stale, startup_failure", errors)

    def test_handoff_policy_requires_structured_all_clear_controls(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"]["all_clear_requirements"].remove("downstream_return_receipt_accepted")
        errors = validator.validate_manifest(broken)
        self.assertIn("missing all-clear requirement(s): downstream_return_receipt_accepted", errors)

    def test_handoff_policy_reports_malformed_object(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"] = None
        errors = validator.validate_manifest(broken)
        self.assertIn("handoff_check_policy must be an object", errors)

    def test_handoff_policy_allows_additional_repair_links(self):
        broken = copy.deepcopy(self.manifest)
        broken["handoff_check_policy"]["linked_repair_prs"]["GBOGEB/CODEX"].append(999)
        self.assertEqual([], validator.validate_manifest(broken))


if __name__ == "__main__":
    unittest.main()
