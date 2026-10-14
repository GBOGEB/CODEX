"""CODEX/KEB semantic and authority tests for gg_MATH P4 synthetic wormhole."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qps_math_wormhole_keb",
    ROOT / "scripts/qps_math_wormhole_keb.py")
assert spec and spec.loader
keb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(keb)

SHA = "a"*40
ARTIFACT = hashlib.sha256(b"public synthetic math method card\n").hexdigest()


def synthetic():
    body = {
        "schema": "gg-math-qps-wormhole/v1",
        "route_id": "QPS-MATH-P4-3P3-V1",
        "route": ["GBOGEB/gg_MATH", "GBOGEB/CODEX", "GBOGEB/ABACUS",
                  "GBOGEB/cryoplant-project"],
        "producer": {"repo": "GBOGEB/gg_MATH", "source_sha": SHA,
                     "artifact_path": "research/MATH_METHOD_DEPENDENCY_GRAPH_v1.yaml",
                     "artifact_sha256": ARTIFACT},
        "method": {"id": "M04_PCA", "population_id": "SYNTHETIC_REFERENCE",
                   "data_class": "SYNTHETIC_REFERENCE", "threshold_authority": "QPS_ONLY",
                   "observed_pairwise_fitted": False},
        "lineage": {"wave": "W259", "pulse": "P4", "qps_child_state": "UNKNOWN"},
        "execution": {"state": "PROPOSED_UNVERIFIED", "run_id": None,
                      "job_id": None, "positive_steps": None},
        "authority": {"authority_transfer": False, "formal_credit_delta": 0,
                      "engineering_acceptance": False, "hard_gate_compensation_allowed": False,
                      "release_credit": False},
        "completed_hops": [],
    }
    return {**body, "receipt_sha256": keb.digest(body)}


def reseal(record):
    record["receipt_sha256"] = keb.digest({
        name: value for name, value in record.items() if name != "receipt_sha256"
    })
    return record


class KEBQPSWormholeTests(TestCase):
    def test_valid_semantics_are_candidate_only(self):
        state = keb.challenge(synthetic(), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertEqual("SEMANTIC_CANDIDATE_ONLY", state["status"])
        self.assertFalse(state["eligible_for_dow_authenticated_replay"])
        self.assertFalse(state["keb_native_run_authenticated"])
        self.assertEqual("DEFER", state["qps_child_disposition"])

    def test_source_sha_changes_fail(self):
        state = keb.challenge(synthetic(), source_sha="b"*40, artifact_sha256=ARTIFACT)
        self.assertIn("EXACT_SOURCE_IDENTITY_MISMATCH", state["errors"])

    def test_artifact_digest_changes_fail(self):
        state = keb.challenge(synthetic(), source_sha=SHA, artifact_sha256="b"*64)
        self.assertIn("EXACT_ARTIFACT_IDENTITY_MISMATCH", state["errors"])

    def test_digest_tampering_detected(self):
        r = synthetic()
        r["method"]["id"] = "M08_BRADLEY_TERRY"
        state = keb.challenge(r, source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertIn("CANONICAL_DIGEST_MISMATCH", state["errors"])

    def test_pca_cannot_generate_observed_bt_or_modify_project_threshold(self):
        r = synthetic()
        r["method"]["threshold_authority"] = "gg_MATH"
        r["method"]["observed_pairwise_fitted"] = True
        state = keb.challenge(reseal(r), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertIn("QPS_THRESHOLD_OR_BT_AUTHORITY_INVERSION", state["errors"])

    def test_foreign_population_must_defer(self):
        r = synthetic()
        r["method"]["population_id"] = "QPS_PRIVATE"
        state = keb.challenge(reseal(r), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertIn("OBSERVED_DATA_CLAIM_NOT_SUPPORTED", state["errors"])

    def test_private_raw_data_key_is_blocked(self):
        r = synthetic()
        r["raw_qps"] = "private"
        state = keb.challenge(reseal(r), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertEqual(["ENVELOPE_SCHEMA_OR_PRIVATE_FIELDS"], state["errors"])

    def test_fake_keb_native_pass_cannot_be_imported(self):
        r = synthetic()
        r["execution"]["state"] = "PASS"
        state = keb.challenge(reseal(r), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertIn("FAKE_AUTHORITY_OR_EXECUTION", state["errors"])

    def test_qps_accept_field_fails_even_when_resealed(self):
        r = synthetic()
        r["lineage"]["qps_child_state"] = "ACCEPT"
        state = keb.challenge(reseal(r), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertIn("QPS_CHILD_DECISION_INJECTION", state["errors"])

    def test_result_is_deterministic_no_authority(self):
        one = keb.challenge(synthetic(), source_sha=SHA, artifact_sha256=ARTIFACT)
        two = keb.challenge(synthetic(), source_sha=SHA, artifact_sha256=ARTIFACT)
        self.assertEqual(one, two)
        self.assertFalse(one["authority_transfer"])
        self.assertEqual(0, one["formal_credit_delta"])
        self.assertFalse(one["engineering_acceptance"])
