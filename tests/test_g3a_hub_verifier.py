"""Adversarial tests for scripts/g3a_hub_verifier.py (receipt judge, no network)."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "g3a_hub_verifier.py"
_spec = importlib.util.spec_from_file_location("g3a_hub_verifier", SCRIPT)
V = importlib.util.module_from_spec(_spec)
sys.modules["g3a_hub_verifier"] = V
_spec.loader.exec_module(V)

H1 = "a" * 40
H2 = "b" * 40


def receipt(head: str = H1) -> dict:
    run = lambda rid, name, concl="success", att=1, sha=head: {  # noqa: E731
        "run_id": rid, "job_id": rid + 1, "attempt": att, "name": name,
        "head_sha": sha, "status": "completed", "conclusion": concl}
    return {
        "schema": V.SCHEMA, "repository": "GBOGEB/pipeline-automation-hub",
        "mission_id": "G3A-TEST", "index_namespace": "hub-jade", "start_index": 0,
        "expected_head_sha": head,
        "pulls": [{"number": 1154, "head_sha": head, "unresolved_threads": 0, "independent_approvals": 1}],
        "runs": [run(10, "portfolio-qa"), run(20, "fpc")],
        "gates": [
            {"id": "A1", "checks": [{"kind": "threads_zero", "pr": 1154}]},
            {"id": "A2", "checks": [{"kind": "run_success", "pr": 1154, "name": "portfolio-qa"},
                                    {"kind": "approvals_min", "pr": 1154, "minimum": 1}]},
            {"id": "A3", "checks": [{"kind": "contexts_success", "pr": 1154, "names": ["portfolio-qa", "fpc"]}]},
        ],
    }


def verdicts(rec: dict) -> list[str]:
    return [g["verdict"] for g in V.judge(rec)["gates"]]


class HubVerifierTests(unittest.TestCase):
    def test_all_green_advances_three(self):
        out = V.judge(receipt())
        self.assertEqual(verdicts(receipt()), ["PASS"] * 3)
        self.assertEqual(out["accepted_checkpoints"], 3)
        self.assertEqual(out["actual_index"], 3)

    def test_known_red_run_fails_and_blocks_later_gates(self):
        r = receipt()
        r["runs"][0]["conclusion"] = "failure"
        out = V.judge(r)
        self.assertEqual([g["verdict"] for g in out["gates"]], ["PASS", "FAIL", "FAIL"])
        self.assertEqual(out["accepted_checkpoints"], 1)
        self.assertEqual([g["credited"] for g in out["gates"]], [True, False, False])

    def test_red_not_hidden_by_later_green_of_same_name(self):
        r = receipt()
        r["runs"].append({"run_id": 11, "job_id": 12, "attempt": 1, "name": "portfolio-qa",
                          "head_sha": H1, "status": "completed", "conclusion": "success"})
        r["runs"][0]["conclusion"] = "failure"
        self.assertEqual(verdicts(r)[1], "FAIL")

    def test_rerun_attempt_supersedes_same_run_id(self):
        r = receipt()
        r["runs"][0]["conclusion"] = "failure"
        r["runs"].append({"run_id": 10, "job_id": 11, "attempt": 2, "name": "portfolio-qa",
                          "head_sha": H1, "status": "completed", "conclusion": "success"})
        self.assertEqual(verdicts(r), ["PASS"] * 3)

    def test_green_on_other_sha_is_not_transferred(self):
        r = receipt()
        for run in r["runs"]:
            run["head_sha"] = H2
        self.assertEqual(verdicts(r)[1], "UNKNOWN")

    def test_pr_head_differs_from_expected_fails(self):
        r = receipt()
        r["pulls"][0]["head_sha"] = H2
        self.assertEqual(verdicts(r)[0], "FAIL")

    def test_truncated_sha_is_unknown_never_pass(self):
        r = receipt()
        r["pulls"][0]["head_sha"] = "859e5312"
        self.assertEqual(verdicts(r)[0], "UNKNOWN")

    def test_handover_prefix_replay_cannot_pass(self):
        # Real handover facts: only SHA prefixes and run ids are known; replay must not PASS.
        r = receipt()
        r["pulls"][0]["head_sha"] = "859e5312"
        r["runs"] = [{"run_id": 43809756062, "job_id": 133108535138, "attempt": 1,
                      "name": "portfolio-qa", "head_sha": "859e5312",
                      "status": "completed", "conclusion": "failure"}]
        self.assertNotIn("PASS", verdicts(r))

    def test_queued_or_skipped_is_not_success(self):
        r = receipt()
        r["runs"][0]["status"] = "queued"
        r["runs"][0]["conclusion"] = None
        self.assertEqual(verdicts(r)[1], "UNKNOWN")
        r = receipt()
        r["runs"][0]["conclusion"] = "skipped"
        self.assertEqual(verdicts(r)[1], "UNKNOWN")

    def test_null_counts_are_unknown(self):
        r = receipt()
        r["pulls"][0]["unresolved_threads"] = None
        self.assertEqual(verdicts(r)[0], "UNKNOWN")
        r = receipt()
        r["pulls"][0]["unresolved_threads"] = 5
        self.assertEqual(verdicts(r)[0], "FAIL")

    def test_insufficient_approvals_fails(self):
        r = receipt()
        r["pulls"][0]["independent_approvals"] = 0
        self.assertEqual(verdicts(r)[1], "FAIL")

    def test_empty_gate_and_empty_names_fail(self):
        r = receipt()
        r["gates"][0]["checks"] = []
        self.assertEqual(verdicts(r)[0], "FAIL")
        r = receipt()
        r["gates"][2]["checks"][0]["names"] = []
        self.assertEqual(verdicts(r)[2], "FAIL")

    def test_missing_run_is_unknown(self):
        r = receipt()
        r["runs"] = [x for x in r["runs"] if x["name"] != "fpc"]
        self.assertEqual(verdicts(r)[2], "UNKNOWN")

    def test_unapproved_check_kind_is_unknown(self):
        r = receipt()
        r["gates"][0]["checks"] = [{"kind": "shell", "cmd": "rm -rf /"}]
        self.assertEqual(verdicts(r)[0], "UNKNOWN")

    def test_ineligible_receipts_raise(self):
        base = receipt()
        for mutate in (
            lambda r: r.update(schema="other"),
            lambda r: r.update(repository="GBOGEB/ABACUS"),
            lambda r: r.update(expected_head_sha="abc"),
            lambda r: r.update(start_index=-1),
            lambda r: r.update(start_index=True),
            lambda r: r.update(index_namespace=""),
            lambda r: r["gates"].pop(),
            lambda r: r["gates"].reverse(),
            lambda r: r.update(runs={}),
        ):
            r = copy.deepcopy(base)
            mutate(r)
            with self.assertRaises(V.Ineligible):
                V.judge(r)

    def test_cli_exit_codes(self):
        def run(rec):
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "r.json"
                p.write_text(json.dumps(rec), encoding="utf-8")
                return subprocess.run([sys.executable, str(SCRIPT), str(p)],
                                      capture_output=True, text=True, check=False).returncode
        red = receipt()
        red["runs"][0]["conclusion"] = "failure"
        unk = receipt()
        unk["pulls"][0]["unresolved_threads"] = None
        self.assertEqual(run(receipt()), 0)
        self.assertEqual(run(red), 1)
        self.assertEqual(run(unk), 2)
        bad = receipt()
        bad["schema"] = "x"
        self.assertEqual(run(bad), 2)
        self.assertEqual(subprocess.run([sys.executable, str(SCRIPT), "/nonexistent.json"],
                                        capture_output=True, check=False).returncode, 3)


if __name__ == "__main__":
    unittest.main()
