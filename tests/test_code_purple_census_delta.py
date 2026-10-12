"""Read-only Code Purple delta census proof: sparse changes, lineage and replay."""
from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "code_purple_census_delta.py"
SPEC = importlib.util.spec_from_file_location("code_purple_census_delta", MODULE)
assert SPEC is not None and SPEC.loader is not None
delta = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delta)
HEAD = "a" * 40
NEXT = "b" * 40


def sample() -> dict:
    return {
        "schema": "code-purple.census.snapshot/1",
        "repo": "GBOGEB/CODEX",
        "scope": "PR-984:check-runs",
        "source_sha": HEAD,
        "observed_at": "2026-10-12T10:00:00Z",
        "mission": {"goal": "PROVE_CODE_PURPLE", "dov": "WITHHELD", "todo_open": 2},
        "records": [
            {"id": "check-run:100", "kind": "check_run", "name": "CI",
             "status": "in_progress", "run_id": 123, "run_attempt": 1},
            {"id": "check-run:101", "kind": "check_run", "name": "security",
             "status": "queued", "run_id": 124, "run_attempt": 1},
        ],
    }


class DeltaCensusTest(unittest.TestCase):
    def test_no_change_ignores_observed_timestamp(self):
        old = sample()
        new = deepcopy(old)
        new["observed_at"] = "2026-10-12T10:30:00Z"
        d = delta.make_delta(old, new)
        self.assertEqual(d["status"], "NO_CHANGE")
        self.assertEqual(d["counts"]["updated"], 0)
        self.assertEqual(delta.apply_delta(old, d), delta.validate(new))

    def test_sparse_status_update_not_whole_record(self):
        old = sample()
        new = deepcopy(old)
        new["records"][0]["status"] = "completed"
        new["records"][0]["conclusion"] = "success"
        d = delta.make_delta(old, new)
        self.assertEqual(d["counts"]["updated"], 1)
        self.assertEqual(
            d["records"]["updated"]["check-run:100"]["set"],
            {"conclusion": "success", "status": "completed"},
        )
        self.assertEqual(delta.apply_delta(old, d), delta.validate(new))

    def test_added_and_tombstoned_and_mission_delta(self):
        old = sample()
        new = deepcopy(old)
        new["records"].pop(0)
        new["records"].append({"id": "check-run:102", "kind": "check_run", "name": "Test",
                               "status": "completed", "conclusion": "success"})
        new["mission"]["todo_open"] = 1
        d = delta.make_delta(old, new)
        self.assertEqual(d["counts"]["added"], 1)
        self.assertEqual(d["counts"]["removed"], 1)
        self.assertEqual(d["mission"]["set"], {"todo_open": 1})
        self.assertEqual(delta.apply_delta(old, d), delta.validate(new))

    def test_new_head_is_not_quality_improvement(self):
        old = sample()
        new = deepcopy(old)
        new["source_sha"] = NEXT
        d = delta.make_delta(old, new)
        self.assertEqual(d["comparability"], "CROSS_HEAD_REBASELINE")
        self.assertEqual(d["analytics_credit"], "WITHHELD_NO_INDEPENDENT_ITERATION_DENOMINATOR")
        self.assertEqual(delta.apply_delta(old, d), delta.validate(new))

    def test_wrong_baseline_fails_replay(self):
        old = sample()
        new = deepcopy(old)
        new["records"][0]["status"] = "completed"
        d = delta.make_delta(old, new)
        other = deepcopy(old)
        other["source_sha"] = NEXT
        with self.assertRaises(ValueError):
            delta.apply_delta(other, d)

    def test_tampered_patch_fails(self):
        old = sample()
        new = deepcopy(old)
        new["records"][0]["status"] = "completed"
        d = delta.make_delta(old, new)
        d["records"]["updated"]["check-run:100"]["set"]["status"] = "success"
        with self.assertRaises(ValueError):
            delta.apply_delta(old, d)

    def test_no_raw_log_or_extra_fields(self):
        old = sample()
        old["records"][0]["stdout"] = "potentially secret log"
        with self.assertRaises(ValueError):
            delta.validate(old)

    def test_duplicate_record_key_refused(self):
        old = sample()
        old["records"].append(deepcopy(old["records"][0]))
        with self.assertRaises(ValueError):
            delta.validate(old)

    def test_wrong_scope_refused(self):
        old = sample()
        new = deepcopy(old)
        new["scope"] = "another-pr"
        with self.assertRaises(ValueError):
            delta.make_delta(old, new)

    def test_unbound_sha_refused(self):
        old = sample()
        old["source_sha"] = "main"
        with self.assertRaises(ValueError):
            delta.validate(old)

    def test_attempt_must_be_nonzero_integer(self):
        old = sample()
        old["records"][0]["run_attempt"] = 0
        with self.assertRaises(ValueError):
            delta.validate(old)


if __name__ == "__main__":
    unittest.main()
