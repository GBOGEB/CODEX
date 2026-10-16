"""Adversarial contract tests for CODE PURPLE required-check admission."""
from __future__ import annotations
import copy
import unittest
from scripts import code_purple_ruleset_evidence_v2 as m

SHA = "a"*40

def snapshot():
    return {
        "schema": m.SCHEMA, "repository": "GBOGEB/CODEX",
        "default_branch": "main", "branch_protected": True, "pr_head_sha": SHA,
        "rulesets": [{
            "enforcement": "active", "target": "branch",
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"]}},
            "rules": [{"type": "required_status_checks", "parameters": {
                "required_status_checks": [{"context": "governance-gate", "integration_id": 15368}]}}],
        }],
        "check_runs": [{"name": "governance-gate", "head_sha": SHA, "status": "completed",
                         "conclusion": "success", "app": {"id": 15368}}],
        "workflows": [{"name": "Governance", "job_contexts": ["governance-gate"],
                       "events": ["pull_request"], "pr_target_branches": ["main"],
                       "path_filters": False, "job_conditional": False}],
        "pr": {"draft": False, "head_sha": SHA, "mergeable": True,
               "mergeable_state": "clean"}
    }

class EvidenceV2(unittest.TestCase):
    def test_valid_context_producer_is_proven_not_admitted(self):
        x=m.assess(snapshot())
        self.assertTrue(x["mandatory_checks_proven"])
        self.assertEqual(x["required_contexts"][0]["state"], "PASS")
        self.assertEqual(x["merge_admission"], "HOLD")
        self.assertFalse(x["mutation"])

    def test_missing_required_check_fails_closed(self):
        s=snapshot()
        s["check_runs"]=[]
        x=m.assess(s)
        self.assertEqual(x["required_contexts"][0]["state"],"MISSING_OR_PENDING")
        self.assertFalse(x["mandatory_checks_proven"])

    def test_wrong_expected_app_rejected(self):
        s=snapshot()
        s["check_runs"][0]["app"]["id"]=7
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"MISSING_OR_PENDING")

    def test_wrong_sha_rejected(self):
        s=snapshot()
        s["check_runs"][0]["head_sha"]="b"*40
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"MISSING_OR_PENDING")

    def test_failed_check_not_allowed(self):
        s=snapshot()
        s["check_runs"][0]["conclusion"]="failure"
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"FAILED_CHECK")

    def test_skipped_check_not_called_success(self):
        s=snapshot()
        s["check_runs"][0]["conclusion"]="skipped"
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"SKIPPED_NOT_PROVEN")

    def test_conditional_job_detected(self):
        s=snapshot()
        s["workflows"][0]["job_conditional"]=True
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"CONDITIONAL_OR_NONUNIVERSAL_PRODUCER")

    def test_path_filter_detected(self):
        s=snapshot()
        s["workflows"][0]["path_filters"]=True
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"CONDITIONAL_OR_NONUNIVERSAL_PRODUCER")

    def test_non_pr_workflow_not_universal(self):
        s=snapshot()
        s["workflows"][0]["events"]=["workflow_dispatch"]
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"CONDITIONAL_OR_NONUNIVERSAL_PRODUCER")

    def test_wrong_base_branch_not_universal(self):
        s=snapshot()
        s["workflows"][0]["pr_target_branches"]=["develop"]
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"CONDITIONAL_OR_NONUNIVERSAL_PRODUCER")

    def test_unknown_producer_is_not_green(self):
        s=snapshot()
        s["workflows"]=[]
        self.assertEqual(m.assess(s)["required_contexts"][0]["state"],"UNKNOWN_PRODUCER")

    def test_no_effective_rules_is_not_enforcement(self):
        s=snapshot()
        s["rulesets"]=[]
        x=m.assess(s)
        self.assertFalse(x["effective_required_rule"])
        self.assertFalse(x["mandatory_checks_proven"])

    def test_draft_is_never_negative_probe_proof(self):
        s=snapshot()
        s["pr"].update(draft=True,mergeable=False,mergeable_state="blocked")
        s["check_runs"]=[]
        s["pr"]["blocking_reason"]="required_status_checks"
        s["pr"]["blocking_reason_source"]="LIVE_GITHUB_READBACK"
        self.assertFalse(m.assess(s)["negative_probe"]["blocked_by_check_proven"])

    def test_blocked_non_draft_without_specific_proof_is_unknown(self):
        s=snapshot()
        s["check_runs"]=[]
        s["pr"].update(mergeable=False, mergeable_state="blocked")
        self.assertFalse(m.assess(s)["negative_probe"]["blocked_by_check_proven"])

    def test_specifically_proven_status_gate_negative_probe(self):
        s=snapshot()
        s["check_runs"]=[]
        s["pr"].update(mergeable=False,mergeable_state="blocked",
                       blocking_reason="required_status_checks",
                       blocking_reason_source="LIVE_GITHUB_READBACK")
        self.assertTrue(m.assess(s)["negative_probe"]["blocked_by_check_proven"])
        self.assertEqual(m.assess(s)["merge_admission"],"HOLD")

    def test_mismatched_pr_head_invalidates_probe(self):
        s=snapshot()
        s["check_runs"]=[]
        s["pr"].update(head_sha="b"*40, mergeable=False, mergeable_state="blocked",
                       blocking_reason="required_status_checks",
                       blocking_reason_source="LIVE_GITHUB_READBACK")
        self.assertFalse(m.assess(s)["negative_probe"]["blocked_by_check_proven"])

    def test_unverified_protection_invalidates_probe(self):
        s=snapshot()
        s["check_runs"]=[]
        s["branch_protected"]=False
        s["pr"].update(mergeable=False,mergeable_state="blocked",
                       blocking_reason="required_status_checks",
                       blocking_reason_source="LIVE_GITHUB_READBACK")
        self.assertFalse(m.assess(s)["negative_probe"]["blocked_by_check_proven"])

    def test_conflicting_required_app_identity_rejected(self):
        s=snapshot()
        s["rulesets"][0]["rules"][0]["parameters"]["required_status_checks"].append(
            {"context":"governance-gate","integration_id":99})
        with self.assertRaisesRegex(ValueError,"conflicting"):
            m.assess(s)

    def test_bad_snapshot_rejected(self):
        s=snapshot()
        s["pr_head_sha"]="not-an-exact-sha"
        with self.assertRaisesRegex(ValueError,"exact PR head"):
            m.assess(s)

    def test_receipts_stable(self):
        self.assertEqual(m.digest(m.assess(snapshot())),m.digest(m.assess(copy.deepcopy(snapshot()))))

if __name__ == "__main__":
    unittest.main()
