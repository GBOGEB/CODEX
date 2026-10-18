"""CBD W39 guard: locally measured production-source gain cannot become global credit."""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path

DOCS=Path(__file__).resolve().parents[1]/"docs"
LEDGER=DOCS/"data/code_purple_convergence_control_w32.json"
HTML=DOCS/"code_purple_convergence.html"


class NativeMatchedRollupW39(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(LEDGER.read_text())
        cls.w=cls.data["cbd_w38_native"]
        cls.html=HTML.read_text()

    def test_exact_native_identity(self):
        w=self.w
        self.assertEqual(w["terminal_run"],39171719898)
        self.assertEqual(w["terminal_job"],117805992686)
        self.assertEqual(w["run_attempt"],1)
        self.assertEqual(w["terminal_status"],"COMPLETED_SUCCESS")
        self.assertRegex(w["source_pr_head"],r"^[0-9a-f]{40}$")
        self.assertRegex(w["source_sha256"],r"^[0-9a-f]{64}$")

    def test_source_owner_and_scope_pinned(self):
        w=self.w
        self.assertEqual(w["source_owner"],"GBOGEB/ABACUS")
        self.assertEqual(w["scope"],"ci/governance/feedback_queue_pressure.py")
        self.assertTrue(w["source_unchanged"])
        self.assertEqual(w["matched_instrumenter"],"coverage.py==7.10.7")

    def test_matched_branch_population(self):
        b=self.w["source_branch"]
        self.assertEqual((b["baseline_covered"],b["expanded_covered"],b["eligible"]),(21,36,36))
        self.assertEqual(b["delta"],15)
        self.assertEqual(b["expanded_covered"]-b["baseline_covered"],15)

    def test_matched_statement_population(self):
        s=self.w["source_statements"]
        self.assertEqual((s["baseline_covered"],s["expanded_covered"],s["eligible"]),(63,97,97))
        self.assertEqual(s["delta"],34)
        self.assertEqual(s["expanded_covered"]-s["baseline_covered"],34)

    def test_local_full_is_not_global_full(self):
        self.assertIsNone(self.w["global_main_coverage_delta"])
        self.assertFalse(self.w["governed_admission"])
        self.assertIsNone(self.w["formal_root_closure"])
        self.assertIsNone(self.data["historical_coverage"]["current_main_same_head_coverage"])
        self.assertEqual(self.data["merge_admission"],"HOLD")

    def test_new_observer_independent_denominator(self):
        route=self.w["next_public_receipt"]
        self.assertEqual(route["pr"],2288)
        self.assertEqual(route["local_new_source_branches"],"6/6")
        self.assertEqual(route["native_tests_pass"],29)
        self.assertIsNone(route["real_event_to_route_yield"])

    def test_no_fake_reviewer_or_red_canary(self):
        guard=self.w["independent_governance"]
        self.assertIsNone(guard["CODEX_effective_branch_protection"])
        self.assertIsNone(guard["ABACUS_required_approvals"])
        self.assertFalse(guard["eligible_reviewer_accepted"])
        self.assertIsNone(guard["blocked_red_canary"])

    def test_five_unmodified_authority_axes(self):
        self.assertEqual({a["id"] for a in self.data["axes"]},
                         {"SOURCE","PENETRATION","FEDERATION","RUNNER","ROOT"})
        self.assertTrue(all(a["accepted_current"] is None for a in self.data["axes"]))

    def test_html_connected_to_source_data(self):
        for item in ('id="cbdW38Rollup"','id="w39Branch"','id="w39Statements"',
                     'id="w39Route"','id="w39Proof"','const w=d.cbd_w38_native'):
            self.assertIn(item,self.html)
        self.assertIn("br.baseline_covered+br.delta===br.expanded_covered",self.html)
        self.assertIn("st.baseline_covered+st.delta===st.expanded_covered",self.html)
        self.assertIn("main uplift UNKNOWN",self.html)

    def test_html_uses_inert_text_binding(self):
        self.assertIn('const set = (id, value)',self.html)
        self.assertIn(".textContent =",self.html)
        self.assertNotIn("w39Branch.innerHTML",self.html)
        self.assertNotIn("w39Statements.innerHTML",self.html)

    def test_no_qps_confidential_provenance_in_new_receipt(self):
        s=json.dumps(self.w,sort_keys=True)
        self.assertNotIn("cryoplant-project",s)
        self.assertNotIn("QPS_PRIVATE_SHA",s)
        self.assertFalse(self.w["governed_admission"])

    def test_source_digest_not_coverage_document_digest(self):
        sha=self.w["source_sha256"]
        self.assertNotEqual(sha,__import__("hashlib").sha256(HTML.read_bytes()).hexdigest())
        self.assertNotEqual(sha,__import__("hashlib").sha256(LEDGER.read_bytes()).hexdigest())

    def test_no_globally_promoted_event_metric(self):
        assert self.w["next_public_receipt"]["real_event_to_route_yield"] is None
        self.assertIsNone(self.w["global_main_coverage_delta"])

    def test_invariant_mutation_detection(self):
        shadow=copy.deepcopy(self.w)
        shadow["source_branch"]["delta"]=16
        b=shadow["source_branch"]
        self.assertNotEqual(b["baseline_covered"]+b["delta"],b["expanded_covered"])


if __name__=="__main__":
    unittest.main()
