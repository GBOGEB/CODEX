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


if __name__ == "__main__":
    unittest.main()
