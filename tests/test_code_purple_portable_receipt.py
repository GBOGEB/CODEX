"""Fail-closed tests for byte-bound CODE PURPLE candidate portability."""
from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "scripts/code_purple_portable_receipt.py"
SPEC = importlib.util.spec_from_file_location("code_purple_portable_receipt", FILE)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
SOURCE = "a" * 40
TARGET = "b" * 40


def sample():
    source_payload = dict(source_sha=SOURCE, authority_transfer=False,
                          asset_type="preflight", data={"fixture": "safe"})
    source_receipt = hashlib.sha256(module.canonical_bytes(source_payload)).hexdigest()
    consumer_payload = dict(source_sha=TARGET, authority_transfer=False,
                            source_receipt_sha256=source_receipt)
    consumer_receipt = hashlib.sha256(module.canonical_bytes(consumer_payload)).hexdigest()
    record = dict(
        repo="GBOGEB/CODEX", observed_head_sha=SOURCE, current_head_sha=SOURCE,
        consumer_repo="GBOGEB/ABACUS", consumer_head_sha=TARGET,
        portable_asset_type="preflight", pay_it_forward_requested=True,
        source_receipt_sha256=source_receipt, consumer_receipt_sha256=consumer_receipt,
        native_source_readback=True, native_consumer_readback=True,
        local_dov_proven=True, generalisation_gap_observed=True,
        sanitized=True, consumer_independent_proof=True, consumer_accepted=True,
        checks=[dict(name="test", status="completed", conclusion="success")],
        required_checks=["test"], executed_steps=2, code_review_complete=True,
        security_review_complete=True, unresolved_threads=0,
    )
    return record, source_payload, consumer_payload


class PortableReceiptTests(unittest.TestCase):
    def test_byte_bound_candidate_is_not_native_approval(self):
        r, p, c = sample()
        output = module.verify(r, p, c)
        self.assertEqual(output["classification"], "CANDIDATE_FOR_INDEPENDENT_ADMISSION")
        self.assertTrue(output["byte_bound"])
        self.assertFalse(output["independent_native_verification_performed"])
        self.assertFalse(output["merge_authorized"])

    def test_tampered_source_and_consumer_bytes_hold(self):
        for which in ("source", "consumer"):
            r, p, c = sample()
            if which == "source":
                p["data"] = {"fixture": "mutated"}
            else:
                c["unreviewed"] = True
            with self.subTest(which=which):
                self.assertEqual(module.verify(r, p, c)["classification"], "HOLD")

    def test_stale_source_or_missing_native_readback(self):
        for name, value in (("current_head_sha", TARGET),
                            ("native_source_readback", False),
                            ("native_consumer_readback", False)):
            r, p, c = sample()
            r[name] = value
            with self.subTest(name=name):
                self.assertEqual(module.verify(r, p, c)["classification"], "HOLD")

    def test_consumer_must_bind_source_receipt(self):
        r, p, c = sample()
        c["source_receipt_sha256"] = "0" * 64
        self.assertIn("CONSUMER_NOT_BOUND_TO_SOURCE_RECEIPT",
                      module.verify(r, p, c)["reasons"])

    def test_restrict_portable_type_and_repositories(self):
        r, p, c = sample()
        r["portable_asset_type"] = "restricted_binary"
        self.assertIn("UNSUPPORTED_PORTABLE_ASSET", module.verify(r, p, c)["reasons"])
        r, p, c = sample()
        r["consumer_repo"] = r["repo"]
        self.assertIn("ADJACENT_REPOSITORY_REQUIRED", module.verify(r, p, c)["reasons"])

    def test_payload_cannot_transfer_authority(self):
        r, p, c = sample()
        p["authority_transfer"] = True
        self.assertIn("PAYLOAD_AUTHORITY_TRANSFER_FORBIDDEN",
                      module.verify(r, p, c)["reasons"])

    def test_projector_remains_canonical_forward_gate(self):
        r, p, c = sample()
        r["consumer_accepted"] = False
        self.assertIn("CODE_PURPLE_FORWARD_GATES_UNPROVEN",
                      module.verify(r, p, c)["reasons"])

    def test_unknown_check_or_invalid_source_head_rejected(self):
        r, p, c = sample()
        r["observed_head_sha"] = "main"
        with self.assertRaises(ValueError):
            module.verify(r, p, c)
        r, p, c = sample()
        r["checks"].append(dict(name="test", status="completed", conclusion="success"))
        with self.assertRaises(ValueError):
            module.verify(r, p, c)


if __name__ == "__main__":
    unittest.main()
