"""Focused negative/continuation tests for the CODE PURPLE mid-wave testflight."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from scripts import code_purple_midwave_testflight as midwave


class FakeClient:
    def __init__(self, data: dict):
        self.data = data
        self.posted = []
    def get(self, path):
        value = self.data.get(path)
        if isinstance(value, Exception):
            raise value
        if value is None:
            raise urllib.error.HTTPError(path, 404, "Not Found", {}, None)
        return value
    def post_issue_comment(self, repo, issue, body):
        self.posted.append((repo, issue, body))


def repo(name: str, fork: bool = False) -> dict:
    return {"name": name, "full_name": "GBOGEB/" + name, "default_branch": "main",
            "archived": False, "fork": fork, "owner": {"login": "GBOGEB"}}


class MidwaveTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self):
        self.assertEqual(midwave.stable_hash({"x": 1, "y": 2}),
                         midwave.stable_hash({"y": 2, "x": 1}))

    def test_comment_classifier_security_is_first(self):
        self.assertEqual(midwave.classify_comment("Security vulnerability in test"), "security")
        self.assertEqual(midwave.classify_comment("Missing branch coverage"), "coverage")
        self.assertEqual(midwave.classify_comment("Runtime bug in code"), "code")
        self.assertEqual(midwave.classify_comment("Looks good"), "review_other")

    def test_bot_recognition_not_human_or_prefix(self):
        for author in ("dependabot[bot]", "github-actions[bot]", "chatgpt-codex-connector", "github-advanced-security"):
            self.assertTrue(midwave.is_bot(author))
        self.assertFalse(midwave.is_bot("engineer"))
        self.assertFalse(midwave.is_bot("codex-connector-impostor"))

    def test_normalize_bot_and_non_authority(self):
        result = midwave.normalize_comment(
            {"id": 8, "user": {"login": "chatgpt-codex-connector"},
             "body": "P1: security regression", "html_url": "https://example.org",
             "updated_at": "2026-10-14T14:00:00Z"},
            "inline", "GBOGEB/CODEX", 1040, "a" * 40)
        self.assertEqual(result["kind"], "security")
        self.assertEqual(result["disposition"], "REVIEW_REQUIRED_NOT_APPROVAL")
        self.assertEqual(result["source_sha_at_census"], "a" * 40)

    def test_ignore_humans_blank_and_identityless(self):
        base = {"id": 1, "user": {"login": "a-human"}, "body": "bug"}
        self.assertIsNone(midwave.normalize_comment(base, "review", "a/b", 3, "f" * 40))
        base["user"]["login"] = "test[bot]"
        base["body"] = " "
        self.assertIsNone(midwave.normalize_comment(base, "review", "a/b", 3, "f" * 40))
        base["body"], base["id"] = "bug", None
        self.assertIsNone(midwave.normalize_comment(base, "review", "a/b", 3, "f" * 40))

    def test_resume_preserves_history_and_invalidates_current_credit(self):
        prior = {"source_sha": "a" * 40, "gates": {"focused_tests": True},
                 "comment_fingerprints": ["history:1"], "history": []}
        state = midwave.compact_prior([], prior, "b" * 40, "root-1")
        self.assertEqual(state["history"][0]["source_sha"], "a" * 40)
        self.assertEqual(state["history"][0]["bot_comment_count"], 1)
        self.assertNotIn("comment_fingerprints", state["history"][0])
        self.assertFalse(state["same_head"])
        self.assertFalse(state["authority_transfer"])
        self.assertEqual(state["new_bot_comments"], [])

    def test_same_head_deduplicates_existing_bot_comment(self):
        comment = {"id": "r:4", "fingerprint": "abc"}
        prior = {"source_sha": "a" * 40, "comment_fingerprints": ["abc"]}
        result = midwave.compact_prior([comment, comment], prior, "a" * 40, "r")
        self.assertTrue(result["same_head"])
        self.assertEqual(result["new_bot_comments"], [])
        self.assertEqual(result["comment_fingerprints"], ["abc"])

    def test_new_bot_comment_is_retained_once(self):
        comment = {"id": "r:4", "fingerprint": "abc"}
        result = midwave.compact_prior([comment, comment], {}, "a" * 40, "r")
        self.assertEqual(result["new_bot_comments"], [comment])

    def test_count_skipped_and_cancelled_not_green(self):
        checks = [{"head_sha": "a" * 40, "conclusion": s} for s in
                  ("success", "failure", "skipped", "cancelled", None)]
        checks.append({"head_sha": "b" * 40, "conclusion": "success"})
        got = midwave.gate_census(checks, "a" * 40)
        self.assertEqual(got["counts"], {"success": 1, "failure": 1, "skipped": 1,
                                         "cancelled": 1, "pending": 1})
        self.assertEqual(got["pass_fraction"], {"numerator": 1, "denominator": 2})
        self.assertIsNone(got["all_required_green"])

    def test_all_checkpoints_true_still_holds_merge(self):
        got = midwave.latest_checkpoint(dict.fromkeys(midwave.STAGES, True))
        self.assertEqual(got["numerator"], got["denominator"])
        self.assertEqual(got["next"], "admission_hold")
        self.assertEqual(got["admission"], "HOLD")

    def test_partial_checkpoint_resumes_at_first_missing(self):
        got = midwave.latest_checkpoint({"preflight": True, "focused_tests": True,
                                        "security": True})
        self.assertEqual(got["next"], "integrated_ci")
        self.assertEqual(got["numerator"], 3)

    def test_parse_checkpoint_marker_and_corruption(self):
        doc = {"schema": midwave.SCHEMA, "source_sha": "b" * 40}
        val = midwave.ISSUE_MARKER + json.dumps(doc) + " -->"
        self.assertEqual(midwave.parse_checkpoint_comment("header\n" + val), doc)
        self.assertIsNone(midwave.parse_checkpoint_comment("no marker"))
        self.assertIsNone(midwave.parse_checkpoint_comment(midwave.ISSUE_MARKER + "{}"))
        self.assertIsNone(midwave.parse_checkpoint_comment(midwave.ISSUE_MARKER + "{bad} -->"))
        self.assertIsNone(midwave.parse_checkpoint_comment(
            midwave.ISSUE_MARKER + '{"schema":"not-ours"} -->'))

    def test_probe_reads_exact_sha_and_config_only(self):
        name = "GBOGEB/ABACUS"
        sha = "c" * 40
        data = {
            f"/repos/{name}/branches/main": {"commit": {"sha": sha}, "protected": False},
            f"/repos/{name}/actions/runs?branch=main&per_page=30":
                {"workflow_runs": [{"conclusion": "success"}, {"conclusion": "cancelled"},
                                   {"status": "queued"}]},
            f"/repos/{name}/contents/.github/workflows?ref={sha}":
                [{"type": "file", "name": "bandit.yml"},
                 {"type": "file", "name": "mip-coverage-evidence.yml"},
                 {"type": "file", "name": "testpilot-preflight.yml"}],
            f"/repos/{name}/contents/.pre-commit-config.yaml?ref={sha}": {"sha": "blob"},
        }
        got = midwave.probe_repo(FakeClient(data), repo("ABACUS"))
        self.assertEqual(got["main_sha"], sha)
        self.assertFalse(got["protected"])
        self.assertEqual(got["recent_runs"]["outcomes"], {
            "success": 1, "cancelled": 1, "queued": 1})
        self.assertTrue(got["tool_config"]["bandit"])
        self.assertTrue(got["tool_config"]["pre_commit"])
        self.assertFalse(got["tool_config"]["lldb"])
        self.assertIn("UNKNOWN", got["debugger_session"])

    def test_probe_branch_missing_fails_closed(self):
        got = midwave.probe_repo(FakeClient({}), repo("ABACUS"))
        self.assertIsNone(got["main_sha"])
        self.assertEqual(got["ci"], "UNKNOWN")
        self.assertEqual(got["branch_error"], "HTTPError")

    def test_probe_optional_endpoints_unknown(self):
        name = "GBOGEB/CODEX"
        got = midwave.probe_repo(FakeClient({
            f"/repos/{name}/branches/main": {"commit": {"sha": "d" * 40}},
        }), repo("CODEX"))
        self.assertEqual(got["tool_config_status"], "UNKNOWN")
        self.assertFalse(got["tool_config"]["pre_commit"])
        self.assertIsNone(got["protected"])

    def test_bot_comment_sources_include_inline_review_discussion(self):
        name, sha = "GBOGEB/CODEX", "e" * 40
        data = {
            f"/repos/{name}/issues/1040/comments?per_page=100":
                [{"id": 1, "user": {"login": "github-actions[bot]"}, "body": "lint regression"}],
            f"/repos/{name}/pulls/1040/comments?per_page=100":
                [{"id": 2, "user": {"login": "chatgpt-codex-connector"}, "body": "security problem"}],
            f"/repos/{name}/pulls/1040/reviews?per_page=100":
                [{"id": 3, "user": {"login": "human"}, "body": "approved"}],
        }
        got = midwave.bot_comments_for_pr(
            FakeClient(data), name, {"number": 1040, "head": {"sha": sha}})
        self.assertEqual(len(got), 2)
        self.assertEqual({x["kind"] for x in got}, {"security", "code"})

    def test_no_token_cannot_post(self):
        with self.assertRaises(ValueError):
            midwave.GitHubRead("").post_issue_comment("GBOGEB/CODEX", 1037, "x")

    def test_main_requires_safe_limit(self):
        with patch.object(sys, "argv", ["testflight", "--limit", "50"]), \
                self.assertRaises(SystemExit):
            midwave.main()

    def test_main_offline_resumes_and_writes_receipt(self):
        codex = repo("CODEX")
        abacus = repo("ABACUS")
        data = {
            "/users/GBOGEB/repos?per_page=100&page=1&type=owner": [codex, abacus],
            "/repos/GBOGEB/CODEX/branches/main":
                {"commit": {"sha": "a" * 40}, "protected": False},
            "/repos/GBOGEB/ABACUS/branches/main":
                {"commit": {"sha": "b" * 40}, "protected": False},
            "/repos/GBOGEB/CODEX/pulls?state=open&per_page=10": [
                {"number": 1040, "head": {"sha": "c" * 40}}],
            "/repos/GBOGEB/ABACUS/pulls?state=open&per_page=10": [],
            "/repos/GBOGEB/CODEX/pulls/1040/comments?per_page=100": [
                {"id": 1, "user": {"login": "chatgpt-codex-connector"},
                 "body": "security finding", "html_url": "https://github.com/example"}],
            "/repos/GBOGEB/CODEX/issues/1037/comments?per_page=100&page=1": [],
        }
        fake = FakeClient(data)
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "receipt.json"
            with patch.object(midwave, "GitHubRead", return_value=fake), \
                    patch.object(sys, "argv", ["testflight", "--limit", "2",
                                              "--out", str(output),
                                              "--post-on-new-bot-findings"]), \
                    patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(midwave.main(), 0)
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt["repository_census"]["accessible_count"], 2)
            self.assertEqual(receipt["repository_census"]["deep_sample_count"], 2)
            self.assertEqual(receipt["bot_review_census"]["count"], 1)
            self.assertFalse(receipt["merge_allowed"])
            self.assertEqual(len(fake.posted), 1)
            self.assertIn(midwave.ISSUE_MARKER, fake.posted[0][2])
            self.assertIn("+1 new, -0 resolved | open now: 1", fake.posted[0][2])

            # Second run, same findings: the receipt is found and nothing is reposted.
            data["/repos/GBOGEB/CODEX/issues/1037/comments?per_page=100&page=1"] = [
                {"body": fake.posted[0][2], "created_at": "2026-11-15T06:00:00Z"}]
            with patch.object(midwave, "GitHubRead", return_value=fake), \
                    patch.object(sys, "argv", ["testflight", "--limit", "2",
                                              "--out", str(output),
                                              "--post-on-new-bot-findings"]), \
                    patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(midwave.main(), 0)
            self.assertEqual(len(fake.posted), 1)

    def test_latest_checkpoint_is_read_past_the_first_page(self):
        def receipt(sha):
            event = {"schema": midwave.SCHEMA, "source_sha": sha}
            return {"body": midwave.ISSUE_MARKER + json.dumps(event) + " -->",
                    "created_at": "t-" + sha}
        page1 = [receipt("old")] + [{"body": "human note"}] * 99
        page2 = [receipt("new"), {"body": "trailing"}]
        fake = FakeClient({
            "/repos/GBOGEB/CODEX/issues/1037/comments?per_page=100&page=1": page1,
            "/repos/GBOGEB/CODEX/issues/1037/comments?per_page=100&page=2": page2,
        })
        found = midwave.find_latest_checkpoint(fake, "GBOGEB/CODEX", 1037)
        self.assertEqual(found["source_sha"], "new")
        self.assertEqual(found["_observed_at"], "t-new")
        self.assertIsNone(midwave.find_latest_checkpoint(FakeClient({}), "GBOGEB/CODEX", 1037))

    def test_delta_reports_resolved_and_bounds_fingerprints(self):
        keep = {"id": "r:1", "fingerprint": "f1", "repo": "GBOGEB/CODEX", "pr": 1,
                "kind": "code", "comment_url": "u1"}
        prior = {"source_sha": "a" * 40, "comment_fingerprints": ["f1", "f2", "stale"],
                 "open_ids": ["r:1", "r:2"]}
        state = midwave.compact_prior([keep], prior, "a" * 40, "r")
        self.assertEqual(state["new_bot_comments"], [])
        self.assertEqual(state["resolved_ids"], ["r:2"])
        self.assertEqual(state["comment_fingerprints"], ["f1"])
        body = midwave.render_delta_comment(state, "2026-11-15T00:00:00Z")
        self.assertIn("+0 new, -1 resolved | open now: 1 (was 2)", body)
        self.assertIn("- r:2", body)

    def test_findings_on_unscanned_prs_stay_open(self):
        keep = {"id": "O/CODEX#1:code:a", "fingerprint": "f1", "repo": "O/CODEX", "pr": 1,
                "kind": "code", "comment_url": "u"}
        prior = {"source_sha": "a" * 40, "comment_fingerprints": ["f1"],
                 "open_ids": ["O/CODEX#1:code:a", "O/CODEX#1:code:b", "O/CODEX#9:code:c"]}
        state = midwave.compact_prior([keep], prior, "a" * 40, "r", scanned={"O/CODEX#1"})
        self.assertEqual(state["resolved_ids"], ["O/CODEX#1:code:b"])
        self.assertEqual(state["carried_unscanned_ids"], ["O/CODEX#9:code:c"])
        self.assertIn("O/CODEX#9:code:c", state["open_ids"])

    def test_legacy_receipt_without_open_ids_triggers_first_delta(self):
        keep = {"id": "O/CODEX#1:code:a", "fingerprint": "f1", "repo": "O/CODEX", "pr": 1,
                "kind": "code", "comment_url": "u"}
        state = midwave.compact_prior([keep], {"comment_fingerprints": ["f1"]}, "a" * 40, "r")
        self.assertEqual(state["new_bot_comments"], [])
        self.assertTrue(state["legacy_migration"])
        fresh = midwave.compact_prior([keep], {}, "a" * 40, "r")
        self.assertFalse(fresh["legacy_migration"])

    def test_delta_comment_truncates_long_lists(self):
        rows = [{"id": f"r:{i}", "fingerprint": f"f{i}", "repo": "GBOGEB/CODEX", "pr": i,
                 "kind": "code", "comment_url": None} for i in range(15)]
        state = midwave.compact_prior(rows, {"open_ids": [f"x:{i}" for i in range(14)]}, "a" * 40, "r")
        body = midwave.render_delta_comment(state, None)
        self.assertIn("+15 new, -14 resolved | open now: 15 (was 14)", body)
        self.assertIn("+3 more (see run artifact)", body)
        self.assertIn("+2 more", body)


if __name__ == "__main__":
    unittest.main()
