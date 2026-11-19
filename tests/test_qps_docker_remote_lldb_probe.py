"""Fail-closed tests for the real Docker/LLDB probe subprocess boundary."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/qps_docker_remote_lldb_probe.py"
SPEC = importlib.util.spec_from_file_location("qps_docker_remote_lldb_probe_under_test", SCRIPT)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class DockerTimeoutReceiptTests(unittest.TestCase):
    def test_timeout_returns_bounded_failed_result_even_for_binary_output(self):
        exc = subprocess.TimeoutExpired(
            cmd=["docker", "build"], timeout=300,
            output=b"progress" * 4000, stderr=b"\\xfferror" * 4000
        )
        with patch.object(probe.subprocess, "run", side_effect=exc):
            result = probe.run(["docker", "build"], timeout=300)
        self.assertEqual(result["returncode"], 124)
        self.assertIs(result["timed_out"], True)
        self.assertEqual(result["timeout_seconds"], 300)
        self.assertLessEqual(len(result["stdout"]), 16000)
        self.assertLessEqual(len(result["stderr"]), 16000)

    def test_build_timeout_writes_reject_receipt_and_returns_nonzero(self):
        exc = subprocess.TimeoutExpired(
            cmd=["docker", "build"], timeout=300, output=b"partial build", stderr=b"timed out"
        )
        with tempfile.TemporaryDirectory() as td, \
             patch.object(probe, "OUT", Path(td)), \
             patch.object(probe.shutil, "which", side_effect=lambda x: "/usr/bin/" + x), \
             patch.object(probe.subprocess, "run", side_effect=exc):
            code = probe.main()
            body = json.loads((Path(td) / "docker_remote_lldb.json").read_text())
        self.assertEqual(code, 2)
        self.assertEqual(body["status"], "REJECT")
        self.assertEqual(body["dov_status"], "WITHHELD")
        self.assertEqual(body["reason"], "docker_build_timeout")
        self.assertEqual(body["build"]["returncode"], 124)
        self.assertEqual(body["authority_guards"]["formal_engineering_credit_delta"], 0)

    def test_normal_nonzero_build_is_not_relabeled_timeout(self):
        result = subprocess.CompletedProcess(
            args=["docker", "build"], returncode=1, stdout="", stderr="build failed"
        )
        with tempfile.TemporaryDirectory() as td, \
             patch.object(probe, "OUT", Path(td)), \
             patch.object(probe.shutil, "which", side_effect=lambda x: "/usr/bin/" + x), \
             patch.object(probe.subprocess, "run", return_value=result):
            self.assertEqual(probe.main(), 2)
            body = json.loads((Path(td) / "docker_remote_lldb.json").read_text())
        self.assertEqual(body["reason"], "docker_build_failed")
        self.assertNotIn("timed_out", body["build"])


if __name__ == "__main__":
    unittest.main()
