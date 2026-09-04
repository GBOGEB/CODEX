from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

MODULE_PATH = Path("tools/run_qps_w05_bidder_eval_keb_return.py")
SPEC = importlib.util.spec_from_file_location("qps_w05_keb_return", MODULE_PATH)
assert SPEC and SPEC.loader
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class TestW05KebReturn(unittest.TestCase):
    def setUp(self) -> None:
        self.request = runtime.load(runtime.REQUEST)
        self.snapshot = runtime.load(runtime.SNAPSHOT)
        self.glossary = runtime.load(runtime.GLOSSARY)

    def execute(
        self,
        request: dict | None = None,
        snapshot: dict | None = None,
        glossary: dict | None = None,
    ) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.yaml"
            snapshot_path = root / "snapshot.yaml"
            glossary_path = root / "glossary.yaml"
            output_path = root / "receipt.yaml"
            request_path.write_text(yaml.safe_dump(request or self.request), encoding="utf-8")
            snapshot_path.write_text(yaml.safe_dump(snapshot or self.snapshot), encoding="utf-8")
            glossary_path.write_text(yaml.safe_dump(glossary or self.glossary), encoding="utf-8")
            with (
                mock.patch.object(runtime, "REQUEST", request_path),
                mock.patch.object(runtime, "SNAPSHOT", snapshot_path),
                mock.patch.object(runtime, "GLOSSARY", glossary_path),
                mock.patch.object(runtime, "OUT", output_path),
                mock.patch.object(runtime, "git_sha", return_value="a" * 40),
            ):
                self.assertEqual(runtime.main(), 0)
            return yaml.safe_load(output_path.read_text(encoding="utf-8"))

    def test_all_operations_execute_and_bind_hashes(self) -> None:
        receipt = self.execute()
        self.assertEqual(receipt["requested_operations"], receipt["executed_operations"])
        self.assertEqual(receipt["receipt_contract_version"], "0.2.0")
        for status in receipt["operation_status"].values():
            self.assertEqual(status["status"], "PASS_EXECUTED_MECHANIC")
            self.assertTrue(status["result"])
        for finding in receipt["typed_semantic_findings"]:
            hashes = finding["input_glossary_output_hashes"]
            self.assertTrue(all(len(value) == 64 for value in hashes.values()))
            self.assertFalse(finding["qps_authority"])

    def test_unknown_operation_fails_closed(self) -> None:
        request = copy.deepcopy(self.request)
        request["requested_KEB_operations"].append("claim_unimplemented_semantic_scan")
        with self.assertRaisesRegex(SystemExit, "unimplemented KEB operations"):
            self.execute(request=request)

    def test_child_baseline_mismatch_fails_closed(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["source_identity"]["child_baseline_sha"] = "b" * 40
        with self.assertRaisesRegex(SystemExit, "child baseline mismatch"):
            self.execute(snapshot=snapshot)

    def test_repeated_execution_is_deterministic(self) -> None:
        self.assertEqual(self.execute(), self.execute())


if __name__ == "__main__":
    unittest.main()
