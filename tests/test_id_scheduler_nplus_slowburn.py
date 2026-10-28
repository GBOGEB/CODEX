"""N+6 source-pinned disjoint slow-burn: exact receipt and mutation negatives."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# pytest's root collection and unittest's '-s tests' mode use different import
# paths. Load the adjacent W34 fixture by its exact file path in both modes.
HELPERS_PATH = Path(__file__).resolve().with_name(
    "test_id_scheduler_dependency_gate_w34.py")
HELPERS_SPEC = importlib.util.spec_from_file_location(
    "_w34_slowburn_fixture", HELPERS_PATH)
assert HELPERS_SPEC and HELPERS_SPEC.loader
helpers = importlib.util.module_from_spec(HELPERS_SPEC)
HELPERS_SPEC.loader.exec_module(helpers)
metric, request = helpers.metric, helpers.request

SPEC = importlib.util.spec_from_file_location(
    "nplus", ROOT / "scripts/id_scheduler_nplus_slowburn.py")
assert SPEC and SPEC.loader
nplus = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nplus)


def epoch(seq, ids=("a",), *, digest=None):
    m = metric()
    m["capture_utc"] = (
        datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(days=seq)
    ).isoformat()
    m["source_digest"] = digest or hashlib.sha256(str(seq).encode()).hexdigest()
    task = {"a": "ready-a", "b": "ready-b", "c": "ready-c",
            "d": "ready-d", "unknown": "unknown"}
    requests = [
        request(name + str(seq), tid=task[name], pool="unknown" if name == "unknown"
                else "windows" if name == "c" else "linux",
                repo="GBOGEB/ABACUS" if name == "d" else "GBOGEB/CODEX")
        for name in ids
    ]
    return {"metrics": m, "requests": requests}


class SixWaveStopControl(unittest.TestCase):
    def test_w34_fixture_is_loaded_from_the_sibling_file(self):
        # Guard pytest root collection and scoped unittest discovery alike.
        self.assertEqual(Path(HELPERS_SPEC.origin).resolve(), HELPERS_PATH)
        self.assertEqual(request("fixture")["action_class"], "STAGE_ONLY")
        self.assertIn("GBOGEB/CODEX", metric()["sources"])

    def test_six_transitions_require_seven_genuine_inputs(self):
        result = nplus.plan([epoch(i) for i in range(6)])
        self.assertEqual(result["status"], "WITHHELD_INCOMPLETE_NPLUS_HISTORY")
        self.assertEqual(result["required_genuine_source_observations"], 7)
        self.assertEqual(result["native_worker_launches"], 0)
        self.assertIsNone(result["operational_coverage_improvement"])

    def test_distinct_seven_observations_are_stage_only_not_proof(self):
        result = nplus.plan([epoch(i) for i in range(7)])
        self.assertEqual(result["status"], "STAGE_ONLY_NPLUS_CANDIDATE")
        self.assertEqual(result["distinct_source_digests"], 7)
        self.assertEqual(result["stage_only_proposals"], 1)
        self.assertEqual(result["native_worker_launches"], 0)
        self.assertIsNone(result["semantic_root_closure"])
        self.assertEqual(result["formal_credit_delta"], 0)
        self.assertEqual(result["merge_admission"], "HOLD")

    def test_renamed_replay_cannot_restaged_same_logical_task(self):
        result = nplus.plan([epoch(0), epoch(1)])
        second = result["epochs"][1]["decisions"][0]
        self.assertEqual(second["decision"], "DEFER_ALREADY_STAGED_AWAIT_NATIVE_RETURN")
        self.assertEqual(second["wake"], "REQUIRE_DISTINCT_NATIVE_RETURN")
        self.assertEqual(result["stage_only_proposals"], 1)

    def test_same_source_digest_with_new_clock_is_not_progress(self):
        d = epoch(0)["metrics"]["source_digest"]
        result = nplus.plan([epoch(0), epoch(1, digest=d)])
        self.assertEqual(result["distinct_source_digests"], 1)
        self.assertEqual(result["epochs"][1]["status"], "WITHHELD_REUSED_SOURCE_DIGEST")
        self.assertEqual(result["epochs"][1]["proposals"], 0)

    def test_reversed_or_duplicate_clock_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "REPLAYED_OR_REVERSED"):
            nplus.plan([epoch(1), epoch(0)])
        with self.assertRaisesRegex(ValueError, "REPLAYED_OR_REVERSED"):
            nplus.plan([epoch(1), epoch(1)])

    def test_membership_drift_fails_closed(self):
        newer = epoch(1)
        newer["metrics"]["sources"]["GBOGEB/QPS"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_POPULATION_DRIFT"):
            nplus.plan([epoch(0), newer])

    def test_remote_mutation_and_unsafe_path_fail_closed(self):
        bad = epoch(0)
        bad["requests"][0]["mutation_enabled"] = True
        with self.assertRaisesRegex(ValueError, "NON_STAGE_OR_REMOTE_MUTATION"):
            nplus.plan([bad])
        bad = epoch(0)
        bad["requests"][0]["changed_paths"] = ["../private"]
        with self.assertRaisesRegex(ValueError, "UNSAFE_CHANGED_PATH"):
            nplus.plan([bad])

    def test_stale_exact_head_is_deferred_without_launch(self):
        bad = epoch(0)
        bad["requests"][0]["head_sha"] = "f" * 40
        result = nplus.plan([bad])
        self.assertEqual(result["stage_only_proposals"], 0)
        self.assertEqual(result["epochs"][0]["decisions"][0]["wake"],
                         "REFRESH_EXACT_OWNER_HEAD")

    def test_unknown_pool_is_never_assumed_to_have_capacity(self):
        result = nplus.plan([epoch(0, ("unknown",))])
        self.assertEqual(result["stage_only_proposals"], 0)
        self.assertEqual(result["epochs"][0]["decisions"][0]["wake"],
                         "REQUIRE_NATIVE_POOL_INVENTORY")

    def test_bounded_disjoint_multipronged_epoch(self):
        result = nplus.plan([epoch(0, ("a", "b", "c", "d"))])
        self.assertEqual(result["stage_only_proposals"], 3)
        self.assertEqual(result["native_worker_launches"], 0)
        self.assertFalse(result["authority_transfer"])

    def test_overlapping_changed_paths_are_serial(self):
        one = epoch(0, ("a", "b"))
        for r in one["requests"]:
            r["changed_paths"] = ["mission_control/mycelium/control.yaml"]
        result = nplus.plan([one])
        self.assertEqual(result["stage_only_proposals"], 1)
        self.assertIn("DEFER_CHANGED_PATH_LOCK",
                      [x["decision"] for x in result["epochs"][0]["decisions"]])

    def test_stop_rule_rejects_unsafe_horizon_and_population(self):
        with self.assertRaisesRegex(ValueError, "HORIZON_REQUIRES"):
            nplus.plan([epoch(0)], horizon=5)
        with self.assertRaisesRegex(ValueError, "INVALID_OBSERVATION_HISTORY"):
            nplus.plan([])
        with self.assertRaisesRegex(ValueError, "UNBOUNDED_STAGE"):
            nplus.plan([epoch(0)], max_proposals=5)

    def test_determinism_and_strict_pulse_digest(self):
        history = [epoch(i) for i in range(3)]
        a = nplus.plan(copy.deepcopy(history))
        b = nplus.plan(copy.deepcopy(history))
        self.assertEqual(a, b)
        self.assertEqual(len(a["plan_sha256"]), 64)
        self.assertNotIn("worker_id", str(a))

if __name__ == "__main__":
    unittest.main()
