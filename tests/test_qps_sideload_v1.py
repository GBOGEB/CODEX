"""Native positive/adversarial checks for governed KEB side-load v1."""
import copy
import hashlib
import importlib.util
import tempfile
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sideload", ROOT / "scripts/qps_sideload_v1.py")
assert spec and spec.loader
sl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl)


def sample():
    return {
        "schema": "qps.federation.sideload.envelope.v1", "id": "QPS-SL-W169-001",
        "producer": {"repo": "GBOGEB/ABACUS", "sha": "a" * 40},
        "consumer": "GBOGEB/cryoplant-project", "kind": "K8S_STATIC",
        "scope": {"surface": "qplant/deployment/k8s", "namespace": "qplant-production"},
        "source": {"path": "w169/receipt.json", "sha256": None, "size_bytes": None},
        "native": {"run_id": None, "job_id": None, "attempt": None, "executed_steps": None},
        "claims": {"authority_transfer": False, "engineering_credit_delta": 0,
                   "release_admitted": False}, "observed_at_utc": None,
    }


class SideLoadTests(TestCase):
    def test_candidate_never_earns_runtime(self):
        r = sl.inspect(sample())
        self.assertEqual(r["byte_binding"], "BYTES_UNVERIFIED")
        self.assertFalse(r["k8s_api_verified"])
        self.assertEqual(r["qps_child_disposition"], "DEFER")

    def test_bytes_are_verified_locally_not_remotely(self):
        rec = sample()
        content = b"sanitized evidence\n"
        rec["source"]["sha256"] = hashlib.sha256(content).hexdigest()
        rec["source"]["size_bytes"] = len(content)
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "w169/receipt.json"
            p.parent.mkdir()
            p.write_bytes(content)
            r = sl.inspect(rec, Path(root))
            self.assertEqual(r["byte_binding"], "LOCAL_HASH_MATCH_ONLY")
            self.assertFalse(r["native_authenticated"])

    def test_spoofed_artifact_fails(self):
        rec = sample()
        rec["source"] = {"path": "test.json", "sha256": "b"*64, "size_bytes": 4}
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "test.json").write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError, "hash/size mismatch"):
                sl.inspect(rec, Path(root))

    def test_escape_and_short_sha_fail(self):
        for field, value in (("path", "../private/secrets"),):
            rec = sample()
            rec["source"][field] = value
            with self.assertRaisesRegex(ValueError, "unsafe relative"):
                sl.inspect(rec)
        rec = sample()
        rec["producer"]["sha"] = "1234"
        with self.assertRaisesRegex(ValueError, "exact producer"):
            sl.inspect(rec)

    def test_promotions_and_raw_secrets_fail(self):
        rec = sample()
        rec["claims"]["release_admitted"] = True
        with self.assertRaisesRegex(ValueError, "forgery"):
            sl.inspect(rec)
        for key in ("raw_payload", "token", "secret"):
            rec = sample()
            rec[key] = "sensitive"
            with self.assertRaises(ValueError):
                sl.inspect(rec)

    def test_native_run_ids_are_not_self_authentication(self):
        rec = sample()
        rec["native"] = {"run_id": 1, "job_id": 2, "attempt": 1,
                         "executed_steps": 27}
        r = sl.inspect(rec)
        self.assertFalse(r["native_authenticated"])
        self.assertFalse(r["k8s_workload_verified"])

    def test_zero_step_is_not_application_execution(self):
        rec = sample()
        rec["native"]["executed_steps"] = 0
        r = sl.inspect(rec)
        self.assertTrue(r["zero_step"])
        self.assertFalse(r["native_authenticated"])

    def test_unknown_kind_and_extra_field_rejected(self):
        rec = sample()
        rec["kind"] = "K8S_ACCEPT"
        with self.assertRaises(ValueError):
            sl.inspect(rec)
        rec = sample()
        rec["unknown"] = "value"
        with self.assertRaises(ValueError):
            sl.inspect(rec)

    def test_input_not_mutated(self):
        rec = sample()
        copy_before = copy.deepcopy(rec)
        sl.inspect(rec)
        self.assertEqual(rec, copy_before)
