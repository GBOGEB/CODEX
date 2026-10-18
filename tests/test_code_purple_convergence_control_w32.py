"""Contract tests for the CODE PURPLE W32 DOV control-tower projection."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGER = DOCS / "data/code_purple_convergence_control_w32.json"
HTML = DOCS / "code_purple_convergence.html"


class ConvergenceControlContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")

    def test_owner_authority_never_promoted(self):
        self.assertEqual(self.ledger["merge_admission"], "HOLD")
        self.assertFalse(self.ledger["authority_transfer"])
        self.assertFalse(self.ledger["security_waiver"])
        self.assertFalse(self.ledger["mutation_enabled"])

    def test_no_unmeasured_zero_fill(self):
        h = self.ledger["historical_coverage"]
        for key in ("current_main_same_head_coverage", "current_pr_broad",
                    "current_pr_diff", "accepted_fixed_population_delta_pp"):
            self.assertIsNone(h[key], key)
        s = self.ledger["status_snapshots"]
        for key in ("authenticated_crew_launch_ids", "accepted_rex_receipts",
                    "root_open", "root_closed", "bd_open", "bd_closed",
                    "first_correctly_admitted_pr", "negative_red_canary_proven"):
            self.assertIsNone(s[key], key)

    def test_prior_verified_b0_is_not_current_main(self):
        c = self.ledger["historical_coverage"]["canonical_main_verified_previous"]
        self.assertEqual((c["covered"], c["eligible"]), (35571, 52497))
        self.assertEqual(c["run_id"], 39148074250)
        self.assertNotEqual(c["sha"], self.ledger["source_heads_observed"]["ABACUS"])
        self.assertRegex(c["sha"], r"^[0-9a-f]{40}$")

    def test_old_epoch_coverage_is_unmatched(self):
        h = self.ledger["historical_coverage"]
        self.assertEqual(h["historical_main_baseline_20261011"]["percent"], 36.85)
        self.assertEqual(h["historical_pr_broad_20261012"]["percent"], 36.92)
        self.assertEqual(h["historical_pr_diff_20261012"]["percent"], 51)
        for name in ("historical_main_baseline_20261011",
                     "historical_pr_broad_20261012", "historical_pr_diff_20261012"):
            self.assertEqual(h[name]["comparison"], "UNMATCHED")
            self.assertIsNone(h[name]["denominator"])

    def test_five_axes_have_independent_owners(self):
        axes = self.ledger["axes"]
        self.assertEqual({a["id"] for a in axes},
                         {"SOURCE", "PENETRATION", "FEDERATION", "RUNNER", "ROOT"})
        self.assertTrue(all(a["accepted_current"] is None for a in axes))
        self.assertTrue(all(a["denominator"] and a["owner"] for a in axes))

    def test_six_disjoint_lanes_and_15_unadmitted_cases(self):
        lanes = self.ledger["disjoint_lanes"]
        self.assertEqual(len(lanes), 6)
        self.assertEqual({a["pr"] for a in lanes}, {2263, 2264, 2265, 2266, 2267, 2274})
        self.assertEqual(self.ledger["candidate"]["designed_cases"], 15)
        self.assertIsNone(self.ledger["candidate"]["terminal_native_cases"])
        self.assertIsNone(self.ledger["candidate"]["measured_coverage_uplift"])

    def test_links_are_source_owned_and_safe(self):
        links = self.ledger["links"]
        self.assertGreaterEqual(len(links), 11)
        for row in links:
            url = row["href"]
            self.assertNotIn("..", url)
            parsed = urlparse(url)
            self.assertTrue((not parsed.scheme and not parsed.netloc) or
                            (parsed.scheme == "https" and parsed.netloc == "github.com"))
            self.assertIn(row["authority"], {"CODEX", "ABACUS", "QPS"})

    def test_refresh_is_read_only_and_shows_unknown(self):
        self.assertIn('id="control-tower"', self.html)
        self.assertIn('id="githubReload"', self.html)
        self.assertIn("Promise.allSettled", self.html)
        self.assertIn('cache:"no-store"', self.html)
        self.assertIn("run.head_sha===live.abacus.sha", self.html)
        self.assertIn('set("currentCoverage",UNKNOWN)', self.html)
        self.assertNotRegex(self.html, r"fetch\([^)]*method\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)")


    def test_native_selection_never_promotes_red_b0(self):
        receipt = self.ledger["candidate"]["native_selected_case_receipt"]
        self.assertEqual((receipt["designed_cases"], receipt["passed_cases"],
                          receipt["failed_cases"]), (15, 15, 0))
        self.assertEqual(receipt["full_canonical_B0"], "FAILURE")
        self.assertEqual(receipt["full_suite"], {"passed": 4796, "failed": 2, "skipped": 2})
        self.assertIsNone(receipt["coverage_delta"])
        self.assertRegex(receipt["source_head"], r"^[0-9a-f]{40}$")
        self.assertIsNone(self.ledger["candidate"]["ordinary_merge_observed"]["formal_admission"])

    def test_ordinary_issue_counts_never_substitute_bd_roots(self):
        s = self.ledger["status_snapshots"]
        issues = s["ordinary_issues_3repo_observed"]
        self.assertEqual((issues["open"], issues["closed"], issues["total"]), (106, 373, 479))
        self.assertFalse(issues["search_incomplete"])
        self.assertIn("NOT_CAUSAL_ROOTS", issues["kind"])
        self.assertIsNone(s["root_open"])
        self.assertIsNone(s["root_closed"])
        self.assertIsNone(s["bd_open"])
        self.assertIsNone(s["bd_closed"])

    def test_six_ordinary_merges_are_not_six_admissions(self):
        rows = self.ledger["disjoint_lanes"]
        summary = self.ledger["lane_rollup"]
        self.assertEqual((summary["observed_ordinary_merged"],
                          summary["selected_pr_population"]), (6, 6))
        self.assertIsNone(summary["governed_accepted"])
        self.assertIsNone(summary["formally_closed_causal_roots"])
        self.assertEqual(len({r["observed_merge_sha"] for r in rows}), 6)
        for row in rows:
            self.assertEqual(row["status"], "MERGED_ORDINARY_ADMISSION_UNVERIFIED")
            self.assertRegex(row["observed_pr_head"], r"^[0-9a-f]{40}$")
            self.assertRegex(row["observed_merge_sha"], r"^[0-9a-f]{40}$")
            self.assertIsNone(row["governed_admission"])
            self.assertIsNone(row["accepted_root_closure"])

    def test_live_metrics_are_fail_closed(self):
        self.assertIn('id="ordinaryIssues"', self.html)
        self.assertIn('id="w32NativeCases"', self.html)
        self.assertIn("incomplete_results===false", self.html)
        self.assertIn("Number.isSafeInteger", self.html)
        self.assertIn("Array.isArray(pulls)", self.html)
        self.assertIn("metadata sources loaded", self.html)

    def test_federated_portal_links_this_entry(self):
        self.assertIn("code_purple_convergence.html", (DOCS / "index.html").read_text())
        self.assertIn("code_purple_convergence.html",
                      (DOCS / "missioncontrol_federated_launchpad.html").read_text())


if __name__ == "__main__":
    unittest.main()
