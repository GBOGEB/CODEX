"""MIP adversarial DAG operational semantics; never mock a green release."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/"mission_control/mycelium/live_ops"
spec=importlib.util.spec_from_file_location("live_ops",BASE/"dag_observer.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class OperationalDAGTests(unittest.TestCase):
 def setUp(self):self.d=json.loads((BASE/"W1_FIXTURE.json").read_text())
 def test_origin_and_downstream(self):
  x=m.measure(self.d)
  self.assertEqual(x["tasks"],7)
  self.assertEqual(x["root_pressure"]["linux-first-red"]["blocked_descendants"],2)
  self.assertEqual(x["distinct_primary_failure_instances"],1)
  self.assertEqual(x["union_blocked_instances"],2)
  self.assertEqual(x["dispatches"],0)
 def test_unrelated_branch_stays_running(self):
  x=m.measure(self.d);self.assertFalse(x["task_states"]["independent"]["derived_upstream_failed"])
 def test_deferred_does_not_occupy_owner_pool(self):
  x=m.measure(self.d);self.assertEqual(x["pool"]["owner"]["running"],0)
 def test_unknown_queue_is_not_zero(self):
  x=m.measure(self.d);self.assertEqual(x["queue_sample_n"],1)
 def test_no_false_evidence(self):
  x=m.measure(self.d);self.assertEqual(x["verified_native_proofs"],0)
 def test_cycle_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][0]["depends_on"]=["downstream-2"]
  with self.assertRaisesRegex(ValueError,"EXECUTABLE_CYCLE"):m.measure(d)
 def test_missing_dependency_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][0]["depends_on"]=["unknown"]
  with self.assertRaisesRegex(ValueError,"DANGLING_DEPENDENCY"):m.measure(d)
 def test_false_success_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][3]["conclusion"]="success"
  with self.assertRaisesRegex(ValueError,"PREMATURE_OUTCOME"):m.measure(d)
 def test_fake_verified_green_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][3]["evidence_verified"]=True
  with self.assertRaisesRegex(ValueError,"FORGED_PROOF"):m.measure(d)
 def test_duplicate_ids_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"].append(copy.deepcopy(d["tasks"][0]))
  with self.assertRaisesRegex(ValueError,"DUPLICATE_ID"):m.measure(d)
 def test_pool_capacity_rejected(self):
  d=copy.deepcopy(self.d);d["pools"][1]["slots"]=0
  with self.assertRaisesRegex(ValueError,"OBSERVED_POOL_OVERSUBSCRIPTION"):m.measure(d)
 def test_false_dispatch_rejected(self):
  d=copy.deepcopy(self.d);d["dispatch_authorized"]=True
  with self.assertRaisesRegex(ValueError,"AUTHORITY_PROMOTION"):m.measure(d)
 def test_stale_head_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][0]["head_sha"]="main"
  with self.assertRaisesRegex(ValueError,"UNPINNED_HEAD"):m.measure(d)
 def test_duplicate_native_job_rejected(self):
  d=copy.deepcopy(self.d)
  for x in d["tasks"][:2]:x.update(run_id=3,job_id=4,attempt=1)
  with self.assertRaisesRegex(ValueError,"NATIVE_ID_REPLAY"):m.measure(d)
 def test_queue_timestamp_negative_rejected(self):
  d=copy.deepcopy(self.d);d["tasks"][5]["started_at"]="2026-10-18T19:19:00Z"
  with self.assertRaisesRegex(ValueError,"NEGATIVE_QUEUE"):m.measure(d)
if __name__=="__main__":unittest.main()
