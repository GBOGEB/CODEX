"""W2 event replay/freshness/retry adversarial qualification."""
import copy
import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"mission_control/mycelium/live_ops/event_reconcile.py"
sp=importlib.util.spec_from_file_location("events",P)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
B={"repo":"GBOGEB/CODEX","run_id":43,"attempt":1,"job_id":15,
   "head_sha":"a"*40,"status":"queued","conclusion":None,
   "observed_at":"2026-10-19T00:00:00Z"}
class EventTests(unittest.TestCase):
 def test_idempotent_replay(self):
  x=m.reconcile([B,copy.deepcopy(B)])
  self.assertEqual(x["task_instances"],1)
  self.assertEqual(x["unique_event_observations"],1)
 def test_advancing_execution(self):
  n=dict(B,status="in_progress",observed_at="2026-10-19T00:01:00Z")
  t=dict(n,status="completed",conclusion="failure",observed_at="2026-10-19T00:02:00Z")
  x=m.reconcile([B,n,t])
  self.assertEqual(x["terminal"],1)
  self.assertEqual(x["reconciled"][0]["conclusion"],"failure")
 def test_older_arrival_never_rolls_back(self):
  t=dict(B,status="completed",conclusion="success",observed_at="2026-10-19T00:02:00Z")
  x=m.reconcile([t,B])
  self.assertEqual(x["terminal"],1)
 def test_attempts_not_collapsed(self):
  n=dict(B,attempt=2)
  self.assertEqual(m.reconcile([B,n])["task_instances"],2)
 def test_completed_cannot_be_reset(self):
  a=dict(B,status="completed",conclusion="failure",observed_at="2026-10-19T00:01:00Z")
  n=dict(B,observed_at="2026-10-19T00:02:00Z")
  with self.assertRaisesRegex(ValueError,"STATE_REGRESSION"):m.reconcile([a,n])
 def test_completed_outcome_cannot_flip(self):
  a=dict(B,status="completed",conclusion="failure",observed_at="2026-10-19T00:01:00Z")
  n=dict(a,conclusion="success",observed_at="2026-10-19T00:02:00Z")
  with self.assertRaisesRegex(ValueError,"TERMINAL_REWRITTEN"):m.reconcile([a,n])
 def test_same_time_conflict_rejected(self):
  n=dict(B,status="in_progress")
  with self.assertRaisesRegex(ValueError,"SAME_TIME_CONFLICT"):m.reconcile([B,n])
 def test_identity_collision_rejected(self):
  n=dict(B,head_sha="b"*40,observed_at="2026-10-19T00:02:00Z")
  with self.assertRaisesRegex(ValueError,"RUN_IDENTITY_HEAD_DRIFT"):m.reconcile([B,n])
 def test_invalid_attempt_rejected(self):
  n=dict(B,attempt=0)
  with self.assertRaisesRegex(ValueError,"INVALID_NATIVE_IDENTITY"):m.reconcile([n])
 def test_unbound_datetime_rejected(self):
  n=dict(B,observed_at="2026-10-19T00:01:00")
  with self.assertRaisesRegex(ValueError,"UNBOUND_EVENT_TIME"):m.reconcile([n])
 def test_native_status_conflict_rejected(self):
  n=dict(B,conclusion="success")
  with self.assertRaisesRegex(ValueError,"INCONSISTENT_STATUS"):m.reconcile([n])
 def test_no_dispatch_credit(self):
  x=m.reconcile([B]);self.assertEqual(x["mutable_actions"],0)
if __name__=="__main__":unittest.main()
