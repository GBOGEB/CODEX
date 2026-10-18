import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
HOME=Path(__file__).resolve().parents[1]/"mission_control"/"mycelium"/"five_axis"
spec=importlib.util.spec_from_file_location("w31",HOME/"census_w31.py")
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def sample():
    return {"schema":w.SCHEMA,"governance":{"merge_admission":"HOLD","mutation_enabled":False,"authority_transfer":False,"formal_root_closures":None},"snapshots":[{"repo":"GBOGEB/CODEX","head_sha":"a"*40,"reported_total":2,"runs":[{"id":10,"attempt":1,"status":"queued","conclusion":None,"head_sha":"a"*40}]}],"axis_observations":{a:[] for a in w.AXES},"historical_job_manifestations":[]}
def series(seq):
    return [{"source_sha":"a"*40,"scope_sha256":"b"*64,"numerator":n,"denominator":10,"evidence":"TERMINAL_NATIVE_ACCEPTED"} for n in seq]
class W31(unittest.TestCase):
    def test_real_snapshot(self):
        d=json.loads((HOME/"W31_FRESH_READBACK.json").read_text())
        r=w.report(d);self.assertEqual(len(r["main_census"]),2)
        self.assertGreater(r["main_census"][1]["unknown_tail"],0)
        self.assertEqual(r["scheduler_proposal"]["max_new_parallel_source_lanes"],1)
        self.assertEqual(set(r["five_axes"]),set(w.AXES))
    def test_duplicate_attempt_idempotent(self):
        d=sample();d["snapshots"][0]["runs"].append(copy.deepcopy(d["snapshots"][0]["runs"][0]))
        self.assertEqual(w.report(d)["main_census"][0]["observed_distinct_runs"],1)
    def test_conflicting_replay(self):
        d=sample();r=copy.deepcopy(d["snapshots"][0]["runs"][0]);r["status"]="pending";d["snapshots"][0]["runs"].append(r)
        with self.assertRaisesRegex(ValueError,"CONFLICTING_REPLAY"):w.report(d)
    def test_retry_not_second_run(self):
        d=sample();r=copy.deepcopy(d["snapshots"][0]["runs"][0]);r.update(attempt=2,status="completed",conclusion="success");d["snapshots"][0]["runs"].append(r)
        self.assertEqual(w.report(d)["main_census"][0]["observed_attempt_instances"],2)
        self.assertEqual(w.report(d)["main_census"][0]["observed_distinct_runs"],1)
    def test_wrong_head(self):
        d=sample();d["snapshots"][0]["runs"][0]["head_sha"]="b"*40
        with self.assertRaisesRegex(ValueError,"STALE_OR_CROSS_HEAD_RUN"):w.report(d)
    def test_fake_green(self):
        d=sample();d["snapshots"][0]["runs"][0]["conclusion"]="success"
        with self.assertRaisesRegex(ValueError,"FAKE_NATIVE_TERMINAL"):w.report(d)
    def test_governance_held(self):
        d=sample();d["governance"]["merge_admission"]="PASS"
        with self.assertRaisesRegex(ValueError,"AUTHORITY_PROMOTION"):w.report(d)
    def test_fifth_axis_mandatory(self):
        d=sample();d["axis_observations"].pop("source_coverage")
        with self.assertRaisesRegex(ValueError,"FIVE_AXIS_OMISSION"):w.report(d)
    def test_convergence_requires_three_deltas(self):
        self.assertEqual(w.evaluate_axis(series([8,8]))["state"],"REPEAT_BOUNDED")
        self.assertEqual(w.evaluate_axis(series([8,8,8,8]))["state"],"REDIRECT_PLATEAU_BELOW_TARGET")
        self.assertEqual(w.evaluate_axis(series([10,10,10,10]))["state"],"STABLE_LOCAL_TARGET")
    def test_growth_and_regression(self):
        self.assertEqual(w.evaluate_axis(series([8,9]))["state"],"EXPAND_MEASURED")
        self.assertEqual(w.evaluate_axis(series([9,8]))["state"],"REGRESSION")
    def test_uncomparable_population(self):
        x=series([8,9]);x[1]["scope_sha256"]="c"*64
        self.assertEqual(w.evaluate_axis(x)["state"],"UNCOMPARABLE")
    def test_unaccepted_oracle(self):
        x=series([8]);x[0]["evidence"]="LOCAL_ONLY"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_AXIS_POINT"):w.evaluate_axis(x)
    def test_root_dedup_not_closure(self):
        d=sample();d["historical_job_manifestations"]=[{"repo":"GBOGEB/ABACUS","run_id":15,"attempt":1,"job_id":i,"root_signature":"same-root","cell":str(i)} for i in (51,52)]
        r=w.report(d)["shared_first_red"];self.assertEqual(r["distinct_first_red_signatures"],1)
        self.assertIsNone(r["roots"][0]["owner_accepted_closure"])
    def test_hash_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);w.write(sample(),p,head="c"*40,run_id=15,attempt=1)
            w.verify(p,head="c"*40)
            with self.assertRaisesRegex(ValueError,"RECEIPT_PROMOTION"):w.verify(p,head="d"*40)
            (p/"W31_CENSUS_REPORT.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"RECEIPT_DRIFT"):w.verify(p,head="c"*40)
if __name__=="__main__":unittest.main()
