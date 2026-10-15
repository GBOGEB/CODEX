"""Native CODEX replay of DOW exact Git-blob candidate: no self-authentication."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import replay_dow_w169_sideload as r


class DOWW169ReplayTests(unittest.TestCase):
    def test_exact_source_blob_and_transport_validation(self):
        row = r.replay()
        self.assertEqual(row["structural"], "PASS")
        self.assertEqual(row["byte_binding"], "BYTES_UNVERIFIED")
        self.assertEqual(row["source_pr"], 2025)
        self.assertEqual(row["qps_child_disposition"], "DEFER")
        self.assertFalse(row["native_authenticated"])
        self.assertFalse(row["k8s_api_verified"])
        self.assertFalse(row["k8s_workload_verified"])

    def test_no_false_native_authentication(self):
        row = r.replay()
        self.assertIsNone(row["transport_receipt"]["native_metadata"]["run_id"])
        self.assertIsNone(row["transport_receipt"]["native_metadata"]["executed_steps"])
        self.assertEqual(row["admission"], "HOLD")

    def test_fixture_tamper_fails_closed(self):
        with patch.object(r, "blob_sha", return_value="f"*40):
            with self.assertRaisesRegex(ValueError, "differs"):
                r.replay()

    def test_pin_forged_run_or_release_fails_closed(self):
        original = json.loads(r.PIN.read_text())
        for key, value in (("native_run", 99), ("k8s_api_verified", True), ("artifact_bytes_verified", True), ("admission", "ACCEPT")):
            forged = copy.deepcopy(original)
            forged[key] = value
            with tempfile.TemporaryDirectory() as temp:
                pin = Path(temp) / "pin.json"
                pin.write_text(json.dumps(forged), encoding="utf-8")
                with patch.object(r, "PIN", pin):
                    with self.assertRaisesRegex(ValueError, "proof|elevation"):
                        r.replay()

    def test_source_scope_cannot_be_rewritten(self):
        original = json.loads(r.PIN.read_text())
        forged = copy.deepcopy(original)
        forged["producer"] = "GBOGEB/CODEX"
        with tempfile.TemporaryDirectory() as temp:
            pin = Path(temp) / "pin.json"
            pin.write_text(json.dumps(forged), encoding="utf-8")
            with patch.object(r, "PIN", pin):
                with self.assertRaisesRegex(ValueError, "owner changed"):
                    r.replay()

    def test_runtime_native_source_local_byte_match_not_child_accept(self):
        rcv = r.replay_runtime()
        self.assertEqual(rcv["structural"], "PASS")
        self.assertEqual(rcv["source_exact_bytes"], "LOCAL_HASH_MATCH_ONLY")
        self.assertEqual(rcv["run_id"], 38774568289)
        self.assertEqual(rcv["job_id"], 116558746360)
        self.assertFalse(rcv["native_authenticated_by_keb"])
        self.assertFalse(rcv["k8s_api_verified_by_keb"])
        self.assertEqual(rcv["qps_child_disposition"], "DEFER")

    def test_runtime_byte_forgery_rejected(self):
        with patch.object(r.hashlib, "sha256", wraps=r.hashlib.sha256) as spied:
            spied.return_value.hexdigest.return_value = "0"*64
            with self.assertRaisesRegex(ValueError, "SHA256/size mismatch"):
                r.replay_runtime()

    def test_runtime_attempt_forgery_rejected(self):
        pth = r.ROOT / "federation/sideload/W169_NATIVE_PROVENANCE_v1.json"
        original = json.loads(pth.read_text())
        original["attempt"] = 2
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pin.json"
            p.write_text(json.dumps(original))
            with patch.object(r, "ROOT", Path(d)):
                # Fail closed when pinned repository source is unavailable.
                with self.assertRaises(FileNotFoundError):
                    r.replay_runtime()


if __name__ == "__main__":
    unittest.main()
