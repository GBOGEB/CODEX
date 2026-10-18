"""W34 dependency-ready work-conserving stage-only selection negatives."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("w34",ROOT/"scripts/id_scheduler_dependency_gate.py")
assert SPEC and SPEC.loader
w=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)
CODEX="a"*40
ABACUS="b"*40
SRC="c"*64


def metric():
    tasks=[
        {"id":"ready-a","owner":"GBOGEB/CODEX","pool":"linux","state":"READY_PROPOSED"},
        {"id":"ready-b","owner":"GBOGEB/CODEX","pool":"linux","state":"READY_PROPOSED"},
        {"id":"ready-c","owner":"GBOGEB/CODEX","pool":"windows","state":"READY_PROPOSED"},
        {"id":"ready-d","owner":"GBOGEB/ABACUS","pool":"linux","state":"READY_PROPOSED"},
        {"id":"waiting","owner":"GBOGEB/CODEX","pool":"linux","state":"WAITING_UPSTREAM_DERIVED"},
        {"id":"held","owner":"GBOGEB/CODEX","pool":"linux","state":"OWNER_HOLD"},
        {"id":"unknown","owner":"GBOGEB/CODEX","pool":"unknown","state":"READY_PROPOSED"},
    ]
    return {
        "schema":w.W33,"source_digest":SRC,
        "sources":{"GBOGEB/CODEX":CODEX,"GBOGEB/ABACUS":ABACUS},
        "admission":"HOLD","dispatch_enabled":False,"formal_root_closures":None,
        "task_instances":tasks,
        "pools":[
            {"id":"linux","observed_slots":2,"running_observed":0,
             "capacity_state":"OBSERVED_BOUND","utilization_pct":0.0},
            {"id":"windows","observed_slots":1,"running_observed":0,
             "capacity_state":"OBSERVED_BOUND","utilization_pct":0.0},
            {"id":"unknown","observed_slots":None,"running_observed":0,
             "capacity_state":"UNKNOWN","utilization_pct":None},
        ],
    }


def request(ident,tid=None,repo="GBOGEB/CODEX",pool="linux",
            path=None,head=None,gain=2):
    return {
        "id":ident,"task_id":tid or "ready-a","repo":repo,"pool":pool,
        "head_sha":head or (ABACUS if repo=="GBOGEB/ABACUS" else CODEX),
        "action_class":"STAGE_ONLY","mutation_enabled":False,
        "changed_paths":[path or "scripts/"+ident+".py"],
        "age_s":10.0,"est_remaining_s":5.0,
        "convergence_gain":gain,"stability_gain":1.0,"unblock_gain":0.5,
    }


class W34StageOnlyTests(unittest.TestCase):
    def setUp(self):
        self.m=metric()

    def stage(self,rows,**opts):
        return w.stage(self.m,rows,**opts)

    def test_valid_two_disjoint_proposals_are_not_dispatches(self):
        x=self.stage([request("one"),request("two",tid="ready-b")])
        self.assertEqual(x["staged_proposals"],2)
        self.assertFalse(x["dispatch_enabled"])
        self.assertEqual(x["cross_repo_worker_launches"],0)
        self.assertEqual(x["merge_admission"],"HOLD")
        self.assertTrue(all(r["native_job_launch"] is None for r in x["decisions"]))

    def test_work_conserving_priority_uses_existing_value_density(self):
        x=self.stage([request("slow",gain=1),request("high",tid="ready-b",gain=90)],
                     max_proposals=1)
        self.assertEqual(x["staged_ids"],["high"])
        self.assertEqual(next(r["decision"] for r in x["decisions"]
                              if r["id"]=="slow"),"DEFER_PULSE_BUDGET")

    def test_measured_two_slot_pool_never_overcommitted(self):
        rows=[request("one"),request("two",tid="ready-b"),
              request("three",tid="ready-d",repo="GBOGEB/ABACUS")]
        x=self.stage(rows)
        self.assertEqual(x["staged_proposals"],2)
        self.assertEqual(x["pool_capacity_remaining_after_proposals"]["linux"],0)
        self.assertEqual(sum(r["decision"]=="DEFER_POOL_RESERVED_BY_OTHER_PROPOSAL"
                             for r in x["decisions"]),1)

    def test_unknown_pool_capacity_is_not_zero_and_cannot_be_staged(self):
        x=self.stage([request("probe",tid="unknown",pool="unknown")])
        self.assertEqual(x["staged_proposals"],0)
        self.assertEqual(x["decisions"][0]["decision"],"DEFER_POOL_CAPACITY_UNKNOWN")

    def test_real_full_pool_is_distinct_from_unknown_capacity(self):
        self.m["pools"][0]["running_observed"]=2
        x=self.stage([request("one")])
        self.assertEqual(x["decisions"][0]["decision"],"DEFER_POOL_FULL")

    def test_waiting_upstream_cannot_run_or_stage(self):
        x=self.stage([request("blocked",tid="waiting")])
        self.assertEqual(x["decisions"][0]["decision"],
                         "DEFER_DEPENDENCY_WAITING_UPSTREAM_DERIVED")

    def test_owner_hold_cannot_run_or_stage(self):
        x=self.stage([request("review",tid="held")])
        self.assertEqual(x["decisions"][0]["decision"],"DEFER_DEPENDENCY_OWNER_HOLD")

    def test_stale_head_deferred_without_making_a_job(self):
        x=self.stage([request("one",head="f"*40)])
        self.assertEqual(x["decisions"][0]["decision"],"DEFER_STALE_SOURCE_HEAD")
        self.assertIsNone(x["decisions"][0]["native_job_launch"])

    def test_duplicate_logical_task_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_LOGICAL_WORK"):
            self.stage([request("one"),request("two")])

    def test_duplicate_proposal_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PROPOSAL"):
            self.stage([request("same"),request("same",tid="ready-b")])

    def test_overlapping_paths_are_serial_not_parallel(self):
        a=request("one",path="mission_control/mycelium")
        b=request("two",tid="ready-b",path="mission_control/mycelium/control.yaml")
        x=self.stage([a,b])
        self.assertEqual(x["staged_proposals"],1)
        self.assertEqual(sum(r["decision"]=="DEFER_CHANGED_PATH_LOCK"
                             for r in x["decisions"]),1)

    def test_same_path_distinct_owner_is_not_a_collision(self):
        rows=[request("one",path="docs/SIPOC.md"),
              request("other",tid="ready-d",repo="GBOGEB/ABACUS",path="docs/SIPOC.md")]
        x=self.stage(rows)
        self.assertEqual(x["staged_proposals"],2)

    def test_traversal_path_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNSAFE_CHANGED_PATH"):
            self.stage([request("one",path="../secrets")])

    def test_remote_mutation_never_accepted(self):
        x=request("one")
        x["mutation_enabled"]=True
        with self.assertRaisesRegex(ValueError,"NON_STAGE_OR_REMOTE_MUTATION_REQUEST"):
            self.stage([x])

    def test_non_stage_action_never_accepted(self):
        x=request("one")
        x["action_class"]="APPLY_BOUNDED_CODEX"
        with self.assertRaisesRegex(ValueError,"NON_STAGE_OR_REMOTE_MUTATION_REQUEST"):
            self.stage([x])

    def test_forged_required_gate_rejected(self):
        self.m["admission"]="PASS"
        with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_UPSTREAM_PROMOTION"):
            self.stage([request("one")])

    def test_unknown_head_rejected(self):
        x=request("one")
        x["head_sha"]="main"
        with self.assertRaisesRegex(ValueError,"UNPINNED_PROPOSAL_HEAD"):
            self.stage([x])

    def test_unverified_pool_denominator_rejected(self):
        self.m["pools"][0]["observed_slots"]=2
        self.m["pools"][0]["capacity_state"]="UNKNOWN"
        with self.assertRaisesRegex(ValueError,"FABRICATED_CAPACITY_DENOMINATOR"):
            self.stage([request("one")])

    def test_pool_oversubscription_metrics_rejected(self):
        self.m["pools"][0]["running_observed"]=3
        with self.assertRaisesRegex(ValueError,"OVERCLAIMED_POOL_CAPACITY"):
            self.stage([request("one")])

    def test_pulse_budget_limited_to_four(self):
        with self.assertRaisesRegex(ValueError,"UNBOUNDED_PROPOSAL_SIZE"):
            self.stage([request("one")],max_proposals=100)

    def test_idempotent_completed_key_cannot_stage_again(self):
        x=self.stage([request("one")])
        key=x["decisions"][0]["idempotency_key"]
        y=self.stage([request("one")],completed_keys=[key])
        self.assertEqual(y["decisions"][0]["decision"],"DEFER_ALREADY_STAGED")
        self.assertEqual(y["staged_proposals"],0)

    def test_repeat_same_input_deterministic_without_dispatch(self):
        requests=[request("one"),request("two",tid="ready-b")]
        self.assertEqual(self.stage(requests),self.stage(requests))

    def test_source_bound_w33_receipt_success_and_hash_tamper(self):
        with tempfile.TemporaryDirectory() as dirname:
            p=Path(dirname)
            f=p/"W33_TASK_METRICS.json";f.write_bytes(w.canonical(self.m))
            rec={"schema":"missioncontrol.mycelium.operational_dag.receipt.v1",
                 "candidate_head":CODEX,"admission":"HOLD","dispatch_enabled":False,
                 "authority_transfer":False,"source_digest":SRC,
                 "files":{"W33_TASK_METRICS.json":w.digest(f.read_bytes())}}
            rf=p/"W33_SHA256.json";rf.write_bytes(w.canonical(rec))
            self.assertEqual(w.source_bound_metrics(f,rf,CODEX),self.m)
            f.write_text("{}")
            with self.assertRaisesRegex(ValueError,"UPSTREAM_BYTES_OR_SOURCE_MISMATCH"):
                w.source_bound_metrics(f,rf,CODEX)

    def test_fake_wrong_w33_source_head_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            p=Path(dirname);f=p/"W33_TASK_METRICS.json";f.write_bytes(w.canonical(self.m))
            rec={"schema":"missioncontrol.mycelium.operational_dag.receipt.v1",
                 "candidate_head":CODEX,"admission":"HOLD","dispatch_enabled":False,
                 "authority_transfer":False,"source_digest":SRC,
                 "files":{"W33_TASK_METRICS.json":w.digest(f.read_bytes())}}
            rf=p/"W33_SHA256.json";rf.write_bytes(w.canonical(rec))
            with self.assertRaisesRegex(ValueError,"FORGED_UPSTREAM_RECEIPT"):
                w.source_bound_metrics(f,rf,ABACUS)

    def test_w34_receipt_rebuild_tamper_and_foreign_head(self):
        with tempfile.TemporaryDirectory() as dirname:
            p=Path(dirname)
            report=self.stage([request("one")])
            rec=w.receipt(report,p,candidate_head=CODEX,run_id=42,attempt=1)
            self.assertEqual(rec,w.verify(p,CODEX))
            before={f.name:f.read_bytes() for f in p.iterdir()}
            w.receipt(report,p,candidate_head=CODEX,run_id=42,attempt=1)
            self.assertEqual(before,{f.name:f.read_bytes() for f in p.iterdir()})
            with self.assertRaisesRegex(ValueError,"RECEIPT_AUTHORITY"):
                w.verify(p,ABACUS)
            (p/"W34_READY_PLAN.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError,"RECEIPT_HASH_DRIFT"):
                w.verify(p,CODEX)

    def test_no_false_root_closure_or_governed_merge(self):
        x=self.stage([request("one")])
        self.assertIsNone(x["formal_root_closures"])
        self.assertIsNone(x["owner_acceptance"])
        self.assertFalse(x["authority_transfer"])
        self.assertTrue(x["selected_output_not_engineering_credit"])


if __name__=="__main__":
    unittest.main()
