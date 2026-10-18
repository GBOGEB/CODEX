"""W36 global observatory: native fail-closed census, lineage and HTML tests."""
from __future__ import annotations
import copy
import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"code_purple_dov_census_w36.py"
DOCS=ROOT/"docs"
spec=importlib.util.spec_from_file_location("w36", SCRIPT)
assert spec and spec.loader
w=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def original():
    return json.loads((DOCS/"data"/"code-purple-dov-w36.json").read_text(encoding="utf-8"))


def row(i=1, status="completed", conclusion="success", sha="a"*40,
        attempt=1, name="CI"):
    return {"id":i,"status":status,"conclusion":conclusion,"head_sha":sha,
            "run_attempt":attempt,"name":name}


def fake_api(returns=None, sha="a"*40, total=1):
    rows = [row()] if returns is None else returns
    def fetch(url):
        if url.endswith("/branches/main"):
            return {"commit":{"sha":sha}}
        if "/actions/runs?" in url:
            return {"total_count":total, "workflow_runs":copy.deepcopy(rows)}
        raise AssertionError("Unexpected URL: "+url)
    return fetch


class PortalParser(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.scripts=[];self.resources=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag in ("script","iframe","img") and "src" in a:self.resources.append(a["src"])
        if tag=="script":self.scripts.append(a.get("src"))


class FederatedDovW36(unittest.TestCase):
    def setUp(self):
        self.seed=original()
    def test_source_snapshot_keeps_five_noncompensating_axes(self):
        self.assertTrue(w.validate_source(self.seed))
        self.assertEqual(len(self.seed["axes"]),5)
        self.assertTrue(all(x["id"] for x in self.seed["axes"]))
    def test_no_promotion(self):
        d=copy.deepcopy(self.seed);d["governance"]["merge_admission"]="PASS"
        with self.assertRaisesRegex(ValueError,"AUTHORITY_PROMOTION"):w.validate_source(d)
    def test_private_boundary(self):
        d=copy.deepcopy(self.seed)
        next(x for x in d["repos"] if x["visibility"]=="private")["visibility"]="public"
        with self.assertRaisesRegex(ValueError,"PRIVATE_QPS_BOUNDARY"):w.validate_source(d)
    def test_public_snapshot_rejects_private_owner_metadata(self):
        d=copy.deepcopy(self.seed)
        private=next(x for x in d["repos"] if x["visibility"]=="private")
        private["sha"]="f"*40
        with self.assertRaisesRegex(ValueError,"PRIVATE_QPS_METADATA_FORBIDDEN"):
            w.validate_source(d)
        private["sha"]=None
        private["open_issue_and_pr_count"]=42
        with self.assertRaisesRegex(ValueError,"PRIVATE_QPS_METADATA_FORBIDDEN"):
            w.validate_source(d)
    def test_cannot_drop_axis(self):
        d=copy.deepcopy(self.seed);d["axes"].pop()
        with self.assertRaisesRegex(ValueError,"NONCOMPENSATING_FIVE_AXES"):w.validate_source(d)
    def test_native_synthetic_terminal(self):
        out=w.read_public("GBOGEB/ABACUS",fake_api())
        self.assertEqual((out["reported_total"],out["returned_distinct_runs"]),(1,1))
        self.assertEqual((out["nonterminal_observed"],out["unknown_tail"]),(0,0))
    def test_native_queue_not_pass(self):
        out=w.read_public("GBOGEB/CODEX",
                          fake_api([row(status="queued",conclusion=None)],total=4))
        self.assertEqual((out["queued_observed"],out["unknown_tail"]),(1,3))
        self.assertFalse(out["complete"])
    def test_inconsistent_finished_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_TERMINAL_CREDIT"):
            w.read_public("GBOGEB/CODEX",fake_api([row(status="queued",conclusion="success")]))
    def test_wrong_head_rejected(self):
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_HEAD"):
            w.read_public("GBOGEB/CODEX",fake_api([row(sha="b"*40)]))
    def test_invalid_run_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_RUN_ID"):
            w.read_public("GBOGEB/CODEX",fake_api([row(i=0)]))
    def test_run_retry_unique_denominator(self):
        def fetch(url):
            if url.endswith("/branches/main"):
                return {"commit":{"sha":"a"*40}}
            if url.endswith("&page=1"):
                return {"total_count":101,"workflow_runs":[row(i=i) for i in range(1,101)]}
            if url.endswith("&page=2"):
                return {"total_count":101,"workflow_runs":[row(i=1,attempt=2)]}
            raise AssertionError(url)
        x=w.read_public("GBOGEB/ABACUS",fetch)
        self.assertEqual((x["returned_distinct_runs"],x["unknown_tail"]),(100,1))
        self.assertEqual(x["runs"][-1]["attempt"],2)
    def test_concurrent_run_inflow_retains_bounded_evidence(self):
        def fetch(url):
            if url.endswith("/branches/main"):
                return {"commit":{"sha":"a"*40}}
            if url.endswith("&page=1"):
                return {"total_count":101, "workflow_runs":[row(i=i) for i in range(1,101)]}
            if url.endswith("&page=2"):
                return {"total_count":102, "workflow_runs":[row(i=101)]}
            raise AssertionError(url)
        out=w.read_public("GBOGEB/ABACUS",fetch)
        self.assertEqual((out["reported_total"],out["returned_distinct_runs"],out["unknown_tail"]),(101,100,1))
        self.assertTrue(out["pagination_population_changed"])
        self.assertFalse(out["complete"])
    def test_false_duplicate_replay_rejected(self):
        rows=[row(i=1),row(i=1,conclusion="failure")]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ID_CONFLICT"):
            w.read_public("GBOGEB/CODEX",fake_api(rows,total=2))
    def test_owner_limit(self):
        with self.assertRaisesRegex(ValueError,"OWNER_OR_PAGE_BOUNDARY"):
            w.read_public("GBOGEB/cryoplant-project",fake_api())
        with self.assertRaisesRegex(ValueError,"OWNER_OR_PAGE_BOUNDARY"):
            w.read_public("GBOGEB/CODEX",fake_api(),pages=10)
    def test_no_private_qps_get_request(self):
        calls=[]
        def fake(url):
            calls.append(url)
            return fake_api()(url)
        report=w.build(self.seed,fetch=fake)
        self.assertEqual(report["repositories"][-1]["evidence_class"],"PRIVATE_OWNER_DEFER")
        self.assertFalse(any("cryoplant" in x for x in calls))
        self.assertEqual(len(calls),4)
    def test_failed_api_is_unknown_not_zero(self):
        def fail(_url):
            raise OSError("offline")
        report=w.build(self.seed,fetch=fail)
        self.assertIsNone(report["repositories"][0]["reported_total"])
        self.assertEqual(report["repositories"][0]["evidence_class"],"UNAVAILABLE_NOT_ZERO")
    def test_receipt_tamper_and_head(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            w.emit(self.seed,p,head="a"*40,run_id=12,attempt=1,fetch=fake_api())
            self.assertEqual(w.verify(p,"a"*40)["admission"],"HOLD")
            with self.assertRaisesRegex(ValueError,"RECEIPT_AUTHORITY"):w.verify(p,"b"*40)
            (p/"W36_LIVE_READBACK.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"RECEIPT_HASH_DRIFT"):w.verify(p,"a"*40)
    def test_html_semantic_entry_and_safety(self):
        raw=(DOCS/"code-purple-dov.html").read_text(encoding="utf-8")
        parser=PortalParser();parser.feed(raw)
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertTrue({"refresh","native","axes","repos","links","frontiers","status"}.issubset(parser.ids))
        self.assertIn('aria-live="polite"',raw)
        self.assertIn("MERGE ADMISSION: HOLD",raw)
        self.assertIn('data/code-purple-dov-w36.json',raw)
        self.assertIn("async function refresh()",raw)
        self.assertIn("Private QPS",raw)
        self.assertFalse(parser.resources)
        self.assertNotIn("Authorization:",raw)
        self.assertNotIn("fetch(",raw.split("async function refresh()")[0].split("<script>")[0])
    def test_html_responsive_and_view_security(self):
        raw=(DOCS/"code-purple-dov.html").read_text(encoding="utf-8")
        self.assertIn("@media(max-width:580px)",raw)
        self.assertIn("textContent",raw)
        self.assertIn('u.hostname!=="github.com"',raw)
        self.assertIn("rel=",raw)
    def test_portal_discovery_single_entry(self):
        raw=(DOCS/"index.html").read_text(encoding="utf-8")
        self.assertEqual(raw.count('href="code-purple-dov.html"'),1)
    def test_historical_not_current(self):
        hist=self.seed["historical"]
        self.assertEqual(hist["abacus_same_head_run_records"][-1],612)
        self.assertNotEqual(hist["abacus_b0_source_sha"],
                            next(x["sha"] for x in self.seed["repos"] if x["repo"]=="GBOGEB/ABACUS"))
        self.assertTrue(all(x["coverage_current"] is None for x in self.seed["repos"]))
    def test_scope_graphs_not_additive(self):
        self.assertEqual([x["nodes"] for x in self.seed["historical"]["graph_scopes"]],[37,48,20])
    def test_owned_overlap_is_declared(self):
        urls={x["url"] for x in self.seed["links"]}
        self.assertIn("https://github.com/GBOGEB/ABACUS/pull/2276",urls)
        self.assertIn("https://github.com/GBOGEB/ABACUS/pull/2277",urls)
        self.assertIn("https://github.com/GBOGEB/CODEX/pull/1108",urls)


if __name__=="__main__":
    unittest.main()
