"""Negative/positive/reverse tests for read-only consumer contract."""
import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

CONSUMER_REPO = "GBOGEB/CODEX"
SCRIPT = "mission_control/mycelium/acceptance_debt_consumer.py"
SPEC = importlib.util.spec_from_file_location(
    "acceptance_debt_consumer",
    Path(__file__).resolve().parents[1] / SCRIPT,
)
consumer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(consumer)
HEAD_A = "a" * 40
HEAD_B = "b" * 40


def fixture():
    return {
        "schema": "codepurple.acceptance.projection.v1",
        "admission": "HOLD",
        "authority_transfer": False,
        "security_waiver": False,
        "source_contexts": {
            "GBOGEB/ABACUS": {"head_sha": HEAD_A, "epoch": 0},
            CONSUMER_REPO: {"head_sha": HEAD_B, "epoch": 0},
        },
        "obligations": [
            {"id": "CP-T001", "admission_checked": False, "human_review": None}
        ],
        "metrics": {
            "admitted": 0, "current_main_coverage": None,
            "current_diff_coverage": None,
        },
    }


def signed_locally(data):
    raw = json.dumps(data, sort_keys=True).encode("utf-8")
    return raw, hashlib.sha256(raw).hexdigest()


def observe(data, sha=None, prod=HEAD_A, local=HEAD_B):
    raw, digest = signed_locally(data)
    return consumer.consumer_receipt(
        raw, expected_sha256=sha or digest,
        expected_producer_head=prod, expected_consumer_head=local,
    )


class ReadonlyAcceptanceConsumerTests(unittest.TestCase):
    def test_observation_stays_nonadmitting(self):
        result = observe(fixture())
        self.assertEqual(CONSUMER_REPO, result["consumer_repository"])
        self.assertFalse(result["authenticated_origin_verified"])
        self.assertFalse(result["independent_review_verified"])
        self.assertFalse(result["engineering_acceptance_verified"])
        self.assertEqual("HOLD", result["merge_admission"])
        self.assertEqual(0, result["root_closure_credit"])

    def test_source_digest_tamper_rejected(self):
        with self.assertRaisesRegex(consumer.EvidenceWithheld, "digest"):
            observe(fixture(), sha="0" * 64)

    def test_stale_producer_and_consumer_heads_rejected(self):
        with self.assertRaisesRegex(consumer.EvidenceWithheld, "producer head"):
            observe(fixture(), prod="f" * 40)
        with self.assertRaisesRegex(consumer.EvidenceWithheld, "consumer context"):
            observe(fixture(), local="e" * 40)

    def test_reverse_authority_security_and_admission_rejected(self):
        for key, bad in (
            ("authority_transfer", True),
            ("security_waiver", True),
            ("admission", "PASS"),
        ):
            data = fixture()
            data[key] = bad
            with self.subTest(key=key):
                with self.assertRaises(consumer.EvidenceWithheld):
                    observe(data)

    def test_false_human_attestation_and_coverage_rejected(self):
        for mutation in (
            lambda d: d["obligations"][0].update(admission_checked=True),
            lambda d: d["obligations"][0].update(human_review="approved"),
            lambda d: d["metrics"].update(admitted=1),
            lambda d: d["metrics"].update(current_diff_coverage=1.0),
        ):
            data = fixture()
            mutation(data)
            with self.assertRaises(consumer.EvidenceWithheld):
                observe(data)

    def test_forged_missing_context_and_epoch_rejected(self):
        data = fixture()
        data["source_contexts"].pop(CONSUMER_REPO)
        with self.assertRaises(consumer.EvidenceWithheld):
            observe(data)
        data = fixture()
        data["source_contexts"][CONSUMER_REPO]["epoch"] = True
        with self.assertRaises(consumer.EvidenceWithheld):
            observe(data)

    def test_repeat_deterministic_and_no_mutation(self):
        data = fixture()
        frozen = copy.deepcopy(data)
        self.assertEqual(observe(data), observe(data))
        self.assertEqual(data, frozen)

    def test_invalid_raw_bytes_and_bad_digest_format(self):
        with self.assertRaises(consumer.EvidenceWithheld):
            consumer.consumer_receipt(
                "not bytes", expected_sha256="0" * 64,
                expected_producer_head=HEAD_A, expected_consumer_head=HEAD_B
            )
        with self.assertRaises(consumer.EvidenceWithheld):
            consumer.consumer_receipt(
                b"{}", expected_sha256="BAD",
                expected_producer_head=HEAD_A, expected_consumer_head=HEAD_B
            )


if __name__ == "__main__":
    unittest.main()
