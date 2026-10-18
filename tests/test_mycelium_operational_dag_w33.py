"""W33 Mycelium operational DAG positive, reverse and fail-closed contracts."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"mission_control"/"mycelium"/"ops_dag"
SPEC=importlib.util.spec_from_file_location("ops_dag_w33",HOME/"ops_dag.py")
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
SHA="a"*40


class W33OperationalDagTests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads((HOME/"W33_SELECTED_OBSERVATIONS.json").read_text())

    def report(self, d=None):
        return m.project(self.d if d is None else d)[0]

    def mutate(self):
        return copy.deepcopy(self.d)

    def test_selected_cohort_denominators(self):
        self.assertEqual((len(self.d["tasks"]),len(self.d["edges"])),(20,17))
        self.assertEqual(sum(t["kind"]=="NATIVE" for t in self.d["tasks"]),13)
        self.assertGreater(len(m.validate(self.d)[0]),2)

    def test_own_failure_vs_upstream_block_is_not_double_counted(self):
        r=self.report()
        self.assertEqual(r["native_failed_instances"],5)
        self.assertEqual(r["downstream_unique_blocked"],4)
        self.assertEqual(r["primary_failure_fingerprint_candidates"],2)
        self.assertEqual(r["root_amplification_per_failed_instance"],0.8)
        self.assertEqual(len([x for x in r["task_instances"]
                              if x["state"]=="UPSTREAM_FAILED_DERIVED"]),4)

    def test_four_shared_first_red_manifestations_one_fingerprint(self):
        roots=self.report()["root_candidates"]
        w=next(x for x in roots if "W29_COMPARATOR_IMPORT" in x["fingerprint"])
        self.assertEqual(w["failure_manifestations"],4)
        self.assertEqual(w["unique_downstream_blocked"],3)
        self.assertIsNone(w["formal_causal_root_closed"])

    def test_independent_success_and_owner_hold_are_unchanged(self):
        r={x["id"]:x for x in self.report()["task_instances"]}
        self.assertEqual(r["codex.w30.ub310"]["state"],"SUCCESS_NATIVE")
        self.assertEqual(r["w29.new.win311"]["state"],"SUCCESS_NATIVE")
        self.assertEqual(r["codex.w30.receipt"]["state"],"READY_PROPOSED")
        self.assertEqual(r["qps.owner.decision"]["state"],"OWNER_HOLD")
        self.assertEqual(r["w29.new.matched"]["state"],"WAITING_UPSTREAM_DERIVED")
        self.assertEqual(r["w29.old.admission"]["state"],"UPSTREAM_FAILED_DERIVED")

    def test_old_results_not_misreported_current_main(self):
        r={x["id"]:x for x in self.report()["task_instances"]}
        self.assertIs(r["w29.new.win311"]["is_current_owner_head"],False)
        self.assertIsNone(r["qps.owner.decision"]["is_current_owner_head"])

    def test_capacity_stays_unknown_not_fabricated_zero(self):
        r=self.report()
        self.assertEqual(r["queue_sample_n"],0)
        self.assertIsNone(r["queue_p95_s"])
        self.assertIsNone(r["execution_p95_s"])
        self.assertEqual({p["capacity_state"] for p in r["pools"]},{"UNKNOWN"})
        self.assertTrue(all(p["utilization_pct"] is None for p in r["pools"]))

    def test_duplicate_task_id_rejected(self):
        d=self.mutate()
        d["tasks"].append(copy.deepcopy(d["tasks"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_TASK"):
            m.validate(d)

    def test_duplicate_native_identity_rejected(self):
        d=self.mutate()
        task=copy.deepcopy(d["tasks"][0]);task["id"]="new.unique.task"
        d["tasks"].append(task)
        with self.assertRaisesRegex(ValueError,"DUPLICATE_NATIVE_INSTANCE"):
            m.validate(d)

    def test_bad_or_foreign_sha_rejected(self):
        d=self.mutate()
        d["tasks"][0]["native"]["head_sha"]="main"
        with self.assertRaisesRegex(ValueError,"MISSING_NATIVE_IDENTITY"):
            m.validate(d)

    def test_queued_false_green_rejected(self):
        d=self.mutate()
        target=next(t for t in d["tasks"] if t["id"]=="w29.new.ub310")
        target["conclusion"]="success"
        with self.assertRaisesRegex(ValueError,"UNTRUSTWORTHY_OUTCOME"):
            m.validate(d)

    def test_fake_log_root_on_metadata_only_rejected(self):
        d=self.mutate()
        target=next(t for t in d["tasks"] if t["id"]=="b0.w32.canonical")
        target["first_red_signature"]="FAKE"
        with self.assertRaisesRegex(ValueError,"FAKE_ROOT_FINGERPRINT"):
            m.validate(d)

    def test_unmeasured_capacity_cannot_be_claimed(self):
        d=self.mutate()
        d["pools"][0]["observed_slots"]=8
        d["pools"][0]["capacity_evidence"]="NATIVE_JOB_METADATA"
        d["pools"][0]["source_ref"]="https://github.com/GBOGEB/CODEX/actions"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_CAPACITY"):
            m.validate(d)

    def test_pool_capacity_requires_native_receipt_sha(self):
        d=self.mutate()
        d["pools"][0].update({"observed_slots":4,"capacity_evidence":"NATIVE_POOL_INVENTORY_VERIFIED",
                              "source_ref":"https://github.com/GBOGEB/CODEX/actions"})
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_CAPACITY"):
            m.validate(d)
        d["pools"][0]["receipt_sha256"]="b"*64
        m.validate(d)
        self.assertEqual(self.report(d)["pools"][0]["utilization_pct"],0.0)

    def test_executable_cycle_rejected(self):
        d=self.mutate()
        d["edges"].append({"from":"w29.old.admission","to":"w29.old.ub310",
                          "kind":"REQUIRES_SUCCESS",
                          "source_ref":"https://github.com/GBOGEB/ABACUS/issues/1860"})
        with self.assertRaisesRegex(ValueError,"EXECUTABLE_DAG_CYCLE"):
            m.validate(d)

    def test_reference_cycle_allowed_without_scheduling(self):
        d=self.mutate()
        d["edges"].append({"from":"qps.owner.decision","to":"codex.w30.receipt",
                          "kind":"REFERENCES",
                          "source_ref":"https://github.com/GBOGEB/CODEX/issues/977"})
        m.validate(d)
        self.assertEqual(self.report(d)["counts"]["OWNER_HOLD"],1)

    def test_missing_edge_endpoint_rejected(self):
        d=self.mutate();d["edges"][0]["to"]="no-native-task"
        with self.assertRaisesRegex(ValueError,"DANGLING_OR_UNTYPED_EDGE"):
            m.validate(d)

    def test_failed_instance_does_not_poison_native_completed_success(self):
        d=self.mutate()
        d["edges"].append({"from":"w29.old.ub310","to":"codex.w30.ub310",
                          "kind":"REQUIRES_SUCCESS",
                          "source_ref":"https://github.com/GBOGEB/ABACUS/pull/2256"})
        r={x["id"]:x for x in self.report(d)["task_instances"]}
        self.assertEqual(r["codex.w30.ub310"]["state"],"SUCCESS_NATIVE")
        self.assertEqual(r["codex.w30.ub310"]["blocked_by"],[])

    def test_fake_authorized_dispatch_and_merge_both_rejected(self):
        d=self.mutate();d["governance"]["dispatch_enabled"]=True
        with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_PROMOTION"):m.validate(d)
        d=self.mutate();d["governance"]["merge_admission"]="PASS"
        with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_PROMOTION"):m.validate(d)

    def test_malformed_timestamps_rejected(self):
        d=self.mutate()
        d["tasks"][0]["started_at"]="2026-10-18T20:00:00Z"
        d["tasks"][0]["created_at"]="2026-10-18T20:01:00Z"
        with self.assertRaisesRegex(ValueError,"NEGATIVE_QUEUE_TIME"):
            m.validate(d)

    def test_actual_queue_and_runtime_percentiles_with_denominators(self):
        d=self.mutate()
        for i,task in enumerate(d["tasks"][:2]):
            task["created_at"]="2026-10-18T20:00:00Z"
            task["started_at"]="2026-10-18T20:00:0"+str(i+1)+"Z"
            task["completed_at"]="2026-10-18T20:00:1"+str(i+1)+"Z"
        r=self.report(d)
        self.assertEqual((r["queue_sample_n"],r["runtime_sample_n"]),(2,2))
        self.assertEqual(r["queue_p95_s"],2.0)
        self.assertEqual(r["execution_p95_s"],10.0)

    def test_sipoc_axes_independent(self):
        x=m.sipoc(self.d)
        self.assertEqual([r["axis"] for r in x["rows"]],list(m.AXES))
        self.assertEqual(x["admission"],"HOLD")

    def test_temporal_matched_status_not_coverage(self):
        d=self.mutate()
        t=next(x for x in d["tasks"] if x["id"]=="w29.new.ub310")
        t["status"]="completed";t["conclusion"]="success"
        delta=m.compare(self.d,d)
        self.assertTrue(delta["same_logical_population"])
        self.assertEqual(delta["native_failed_delta"],0)
        self.assertIsNone(delta["coverage_gain_eligible"])
        self.assertEqual(delta["owner_admission"],"HOLD")

    def test_temporal_incomparable_selection_null_delta(self):
        d=self.mutate()
        d["tasks"][0]["logical_key"]="renamed_population"
        delta=m.compare(self.d,d)
        self.assertFalse(delta["same_logical_population"])
        self.assertIsNone(delta["native_failed_delta"])

    def test_deterministic_bundle_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)
            receipt=m.build(self.d,out,SHA,run_id=123,attempt=1)
            self.assertEqual(receipt,m.verify(out,SHA))
            first={p.name:p.read_bytes() for p in out.iterdir()}
            m.build(self.d,out,SHA,run_id=123,attempt=1)
            self.assertEqual(first,{p.name:p.read_bytes() for p in out.iterdir()})
            (out/"W33_TASK_VIEWER.html").write_text("tampered")
            with self.assertRaisesRegex(ValueError,"RECEIPT_HASH_DRIFT"):
                m.verify(out,SHA)

    def test_wrong_head_or_partial_attempt_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)
            with self.assertRaisesRegex(ValueError,"PARTIAL_NATIVE_RUN_BINDING"):
                m.build(self.d,out,SHA,run_id=123)
            m.build(self.d,out,SHA)
            with self.assertRaisesRegex(ValueError,"FALSE_RECEIPT_AUTHORITY"):
                m.verify(out,"b"*40)

    def test_viewer_is_local_and_safe(self):
        r,layers=m.project(self.d)
        page=m.viewer(r,layers,self.d)
        for token in ("<title>CODE PURPLE", "id=\"graph\"",
                      "textContent", "UPSTREAM_FAILED_DERIVED", "NO DISPATCH"):
            self.assertIn(token,page)
        self.assertNotIn("https://cdn.",page)
        self.assertNotIn("fetch(",page)
        self.assertNotIn("innerHTML",page)

    def test_real_svg_edge_overlay_is_in_native_viewer(self):
        report,layers=m.project(self.d)
        page=m.viewer(report,layers,self.d)
        for token in ('id="edgePaths"', 'id="layerGrid"',
                      'createElementNS(ns,"path")', 'requestAnimationFrame(drawEdges)',
                      'REQUIRES_SUCCESS', 'aria-pressed'):
            self.assertIn(token,page)

    def test_connected_graph_preserves_17_edges_and_no_browser_dispatch(self):
        report,layers=m.project(self.d)
        page=m.viewer(report,layers,self.d)
        self.assertEqual(report["graph"]["edges"],17)
        self.assertIn('link.kind==="REFERENCES"',page)
        self.assertNotIn('workflow_dispatch',page)
        self.assertNotIn('GenUI.',page)

    def test_no_false_stability_or_six_sigma(self):
        report=self.report()
        self.assertFalse(report["stability"]["stable"])
        self.assertFalse(report["stability"]["six_sigma_qualified"])
        self.assertEqual(report["admission"],"HOLD")
        self.assertFalse(report["dispatch_enabled"])


if __name__ == "__main__":
    unittest.main()
