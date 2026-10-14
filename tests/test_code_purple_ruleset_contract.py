"""Falsification of false protected/green ruleset claims."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import code_purple_ruleset_contract as m

HEAD = "a" * 40


def base(name="CODEX", protected=False, rulesets=None, branch="main"):
    return {
        "repo": "GBOGEB/" + name,
        "default_branch": branch,
        "head_sha": HEAD,
        "protected": protected,
        "rulesets": [] if rulesets is None else rulesets,
        "size": 42,
    }


def rule(kinds=None, *, active=True, branch="~DEFAULT_BRANCH", ident=1):
    p = m.proposed_ruleset()
    return {
        "id": ident, "target": "branch",
        "enforcement": "active" if active else "disabled",
        "conditions": {"ref_name": {"include": [branch], "exclude": []}},
        "rules": p["rules"] if kinds is None else [{"type": k} for k in kinds],
        "bypass_actors": [],
    }


def snapshot(*repos):
    return {
        "schema": m.SCHEMA,
        "scope": "SYNTHETIC_FOCUSED_REGRESSION",
        "observed_at": "2026-10-14T15:30:00Z",
        "repositories": list(repos),
    }


class BranchPolicyContract(unittest.TestCase):
    def test_policy_is_default_branch_no_bypass_no_unverified_ci(self):
        p = m.proposed_ruleset()
        self.assertEqual(p["conditions"]["ref_name"]["include"], ["~DEFAULT_BRANCH"])
        self.assertEqual(p["bypass_actors"], [])
        self.assertEqual({x["type"] for x in p["rules"]}, m.REQUIRED)
        self.assertTrue(all(x["type"] != "required_status_checks" for x in p["rules"]))

    def test_no_ruleset_is_create_and_hold(self):
        v = m.assess(base())
        self.assertEqual((v["status"], v["action"]), ("NO_RULESET", "CREATE_ONE"))
        self.assertEqual(v["merge_admission"], "HOLD")

    def test_active_empty_ruleset_is_update_not_duplicate(self):
        v = m.assess(base("ABACUS", rulesets=[rule([], ident=24494381)]))
        self.assertEqual(v["action"], "UPDATE_EXISTING_EMPTY")
        self.assertEqual(v["ruleset_id"], 24494381)

    def test_valid_rules_and_protected_is_config_only(self):
        v = m.assess(base(protected=True, rulesets=[rule()]))
        self.assertEqual(v["status"], "CONFIGURED_NOT_ADMITTED")
        self.assertEqual(v["merge_admission"], "HOLD")

    def test_main_literal_does_not_cover_master(self):
        v = m.assess(base("support", branch="master", rulesets=[rule(branch="main")]))
        self.assertEqual(v["status"], "PARTIAL_OR_CONFLICTING")

    def test_default_branch_matches_non_main(self):
        v = m.assess(base("support", protected=True, branch="trunk", rulesets=[rule()]))
        self.assertEqual(v["status"], "CONFIGURED_NOT_ADMITTED")

    def test_disabled_rules_do_not_count(self):
        v = m.assess(base(rulesets=[rule(active=False)]))
        self.assertEqual(v["status"], "PARTIAL_OR_CONFLICTING")

    def test_deleted_protection_not_counted_as_review(self):
        v = m.assess(base(protected=True, rulesets=[rule(["deletion", "non_fast_forward"])]))
        self.assertEqual(v["status"], "PARTIAL_OR_CONFLICTING")

    def test_zero_approval_is_not_reviewed(self):
        r = rule()
        r["rules"][2]["parameters"]["required_approving_review_count"] = 0
        self.assertNotIn("pull_request", m.checks(r))

    def test_invalid_approval_type_is_not_reviewed(self):
        r = rule()
        r["rules"][2]["parameters"]["required_approving_review_count"] = None
        self.assertNotIn("pull_request", m.checks(r))

    def test_last_push_stale_and_thread_mandatory(self):
        for field in ("require_last_push_approval", "dismiss_stale_reviews_on_push",
                      "required_review_thread_resolution"):
            r = rule()
            r["rules"][2]["parameters"][field] = False
            self.assertNotIn("pull_request", m.checks(r))

    def test_exclusions_override_inclusion(self):
        r = rule()
        r["conditions"]["ref_name"]["exclude"] = ["~DEFAULT_BRANCH"]
        self.assertFalse(m.targets_default(r, "main"))

    def test_unknown_ruleset_fails_closed(self):
        r = base()
        r["rulesets"] = None
        self.assertEqual(m.assess(r)["status"], "UNKNOWN")

    def test_unknown_head_fails_closed(self):
        r = base()
        r["head_sha"] = None
        self.assertEqual(m.assess(r)["status"], "UNKNOWN")

    def test_empty_repo_separate_exception(self):
        r = base()
        r["size"] = 0
        self.assertEqual(m.assess(r)["status"], "EXCEPTION_REVIEW")

    def test_classic_branch_protection_requires_inspection(self):
        self.assertEqual(m.assess(base(protected=True))["action"], "INSPECT_CLASSIC_PROTECTION")

    def test_nonempty_existing_rules_not_overwritten(self):
        self.assertEqual(m.assess(base(rulesets=[rule(["deletion"])]))["action"],
                         "REVIEW_WITHOUT_OVERWRITE")

    def test_invalid_repo_rejected(self):
        with self.assertRaises(ValueError):
            m.assess({"repo": "something-invalid"})

    def test_summary_denominators_and_no_admission(self):
        report = m.report(snapshot(base(), base("ABACUS", rulesets=[rule([], ident=11)])))
        self.assertEqual(report["metrics"]["protected_reported"], {
            "numerator": 0, "denominator": 2})
        self.assertEqual(report["metrics"]["baseline_configured"], {
            "numerator": 0, "denominator": 2})
        self.assertIsNone(report["metrics"]["admission_verified"])
        self.assertFalse(report["mutation"])

    def test_duplicate_or_wrong_schema_rejected(self):
        with self.assertRaises(ValueError):
            m.report(snapshot(base(), base()))
        with self.assertRaises(ValueError):
            m.report({"schema": "unknown", "repositories": [base()]})

    def test_repeat_receipt_identical(self):
        data = snapshot(base(), base("ABACUS", rulesets=[rule([])]))
        self.assertEqual(m.checksum(m.report(data)), m.checksum(m.report(data)))

    def test_cli_outputs_machine_readable_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            src, out = Path(td) / "snap.json", Path(td) / "receipt.json"
            src.write_text(json.dumps(snapshot(base())), encoding="utf-8")
            self.assertEqual(m.main(["--snapshot", str(src), "--out", str(out)]), 0)
            self.assertEqual(json.loads(out.read_text())["rows"][0]["action"], "CREATE_ONE")


if __name__ == "__main__":
    unittest.main()
