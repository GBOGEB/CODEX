"""W30 Mycelium fan-in: native positive, negative, reverse and mutation guards."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT/"mission_control"/"mycelium"/"five_axis"
sp=importlib.util.spec_from_file_location("spine_w30",HOME/"spine_w30.py")
assert sp and sp.loader
w=importlib.util.module_from_spec(sp)
sp.loader.exec_module(w)

class ParallelSpineW30Tests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads((HOME/"W30_SELECTED_NATIVE.json").read_text(encoding="utf-8"))
    def test_source_selected_and_five_owner_lanes(self):
        self.assertTrue(w.validate(self.d))
        self.assertEqual(len(self.d["lanes"]),5)
        self.assertEqual(len(self.d["observed_jobs"]),14)
        self.assertEqual([x[0] for x in w.SIPOC],list(w.AXES))
    def test_graph_contains_directed_fanin_without_cycle(self):
        g=w.graph(self.d)
        self.assertEqual(len(g["nodes"]),48)
        self.assertEqual(len(g["edges"]),47)
        self.assertGreater(len(g["layers"]),4)
        self.assertEqual(g["owner_gate"],"HOLD")
    def test_cohort_distinction_retained(self):
        m=w.metrics(self.d,w.graph(self.d))
        by={c["cohort"]:c for c in m["independent_cohorts"]}
        self.assertEqual((by["CODEX_FIVE_AXIS_NATIVE"]["native_success"],by["CODEX_FIVE_AXIS_NATIVE"]["job_denominator"]),(4,4))
        self.assertEqual((by["AB_W29_N"]["native_failure"],by["AB_W29_N"]["job_denominator"]),(4,4))
        self.assertEqual((by["AB_W12_N_MINUS_1"]["native_failure"],by["AB_W12_N_MINUS_1"]["job_denominator"]),(1,1))
        self.assertIsNone(m["future"]["accepted_root_closures"])
    def test_first_red_displacement_not_root_closure(self):
        m=w.metrics(self.d,w.graph(self.d))
        self.assertEqual((m["temporal_w29"]["paired_matrix_cells"],m["temporal_w29"]["first_red_stage_advanced_cells"]),(4,4))
        self.assertIsNone(m["future"]["accepted_root_closures"])
    def test_governance_promotion_rejected(self):
        d=copy.deepcopy(self.d)
        d["governance"]["merge_admission"]="PASS"
        with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_PROMOTION"):w.validate(d)
    def test_false_crew_launch_rejected(self):
        d=copy.deepcopy(self.d)
        d["governance"]["authenticated_dispatch"]=True
        with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_PROMOTION"):w.validate(d)
    def test_fabricated_native_green_rejected(self):
        d=copy.deepcopy(self.d)
        d["observed_jobs"][0]["conclusion"]="success"
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_FIRST_RED"):w.validate(d)
    def test_stale_branch_name_not_exact_sha(self):
        d=copy.deepcopy(self.d)
        d["observed_jobs"][0]["sha"]="main"
        with self.assertRaisesRegex(ValueError,"UNPINNED_JOB_HEAD"):w.validate(d)
    def test_repeat_job_rejected(self):
        d=copy.deepcopy(self.d)
        d["observed_jobs"].append(copy.deepcopy(d["observed_jobs"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_NATIVE_JOB"):w.validate(d)
    def test_collision_in_parallel_writer_scope_rejected(self):
        d=copy.deepcopy(self.d)
        d["lanes"][1]["changed_paths"]=[d["lanes"][0]["changed_paths"][0]]
        with self.assertRaisesRegex(ValueError,"WRITER_SCOPE_COLLISION"):w.validate(d)
    def test_unsafe_path_rejected(self):
        d=copy.deepcopy(self.d)
        d["lanes"][0]["changed_paths"].append("../security_gate.yaml")
        with self.assertRaisesRegex(ValueError,"UNSAFE_PATH"):w.validate(d)
    def test_missing_causal_origin_rejected(self):
        d=copy.deepcopy(self.d)
        d["lanes"][0]["origin"]=""
        with self.assertRaisesRegex(ValueError,"MISSING_PROTO_ORIGIN"):w.validate(d)
    def test_cannot_mark_candidate_terminal_without_receipts(self):
        d=copy.deepcopy(self.d)
        d["lanes"][0]["native_complete"]=True
        with self.assertRaisesRegex(ValueError,"FAKE_COMPLETION"):w.validate(d)
    def test_bad_private_remote_proof_rejected(self):
        d=copy.deepcopy(self.d)
        d["observed_jobs"][0]["repo"]="GBOGEB/cryoplant-project"
        with self.assertRaisesRegex(ValueError,"NATIVE_PRIVATE_QPS_PROOF_FORBIDDEN"):w.validate(d)
    def test_execution_dag_cycle_rejected(self):
        g=w.graph(self.d)
        g["edges"].append({"from":"spine:codex","to":"spine:fanin","kind":"REQUIRES"})
        with self.assertRaisesRegex(ValueError,"SPINE_EXECUTABLE_CYCLE"):w.ordered_layers(g["nodes"],g["edges"])
    def test_sipoc_has_five_independent_rows(self):
        s=w.sipoc(self.d)
        self.assertEqual([x["axis"] for x in s["rows"]],list(w.AXES))
        self.assertTrue(s["independent_denominators"])
    def test_bundles_are_deterministic_and_tamper_evident(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            a=w.build(self.d,folder,head="c"*40,run_id=42,attempt=1)
            self.assertEqual(a,w.verify(folder,"c"*40))
            originals={p.name:p.read_bytes() for p in folder.iterdir()}
            w.build(self.d,folder,head="c"*40,run_id=42,attempt=1)
            self.assertEqual(originals,{p.name:p.read_bytes() for p in folder.iterdir()})
            (folder/"W30_VIEWER.html").write_text("<html/>",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"DIGEST_DRIFT"):w.verify(folder,"c"*40)
    def test_receipt_cannot_be_reused_on_different_head(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            w.build(self.d,folder,head="c"*40)
            with self.assertRaisesRegex(ValueError,"FALSE_RECEIPT_AUTHORITY"):w.verify(folder,"d"*40)
    def test_html_shows_hold_and_five_row_sipoc(self):
        m=w.metrics(self.d,w.graph(self.d))
        page=w.render(m,w.sipoc(self.d))
        self.assertIn("MERGE ADMISSION HOLD",page)
        self.assertIn("Parallel SPINE",page)
        self.assertIn("causal_defect_detection",page)
if __name__=="__main__":
    unittest.main()
