"""Synthetic regression tests for the CODEX Drive bridge method binding.

No Drive API, Gemini API, production source or credential is needed.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "googledrive" / "scripts" / "drive_sync_agent.py"
spec = importlib.util.spec_from_file_location("drive_sync_agent_guard_test", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DriveSyncMethodBindingTests(unittest.TestCase):
    def test_routing_and_guard_are_bound_to_agent(self):
        self.assertTrue(callable(getattr(module.DriveSyncAgent, "target_is_unsafe", None)))
        self.assertTrue(callable(getattr(module.DriveSyncAgent, "process_and_route", None)))

    def test_safe_relative_target(self):
        with tempfile.TemporaryDirectory() as d:
            agent = module.DriveSyncAgent(Path(d))
            for path in (
                "googledrive/parallel_refs/example.ipynb",
                "src/agents/codex/experimental/flow_calc.py",
            ):
                with self.subTest(path=path):
                    self.assertFalse(agent.target_is_unsafe(Path(path)))

    def test_traversal_and_absolute_targets_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            agent = module.DriveSyncAgent(Path(d))
            for path in (
                "../secret.txt", "subdir/../../secret.txt", "/tmp/secret.txt",
                "C:\\secret.txt", "C:\\Users\\User\\secret.txt",
                "..\\secret.txt", "C:secret.txt", "\\secret.txt",
            ):
                with self.subTest(path=path):
                    self.assertTrue(agent.target_is_unsafe(Path(path)))

    def test_absent_staging_does_not_route(self):
        with tempfile.TemporaryDirectory() as d:
            agent = module.DriveSyncAgent(Path(d))
            self.assertFalse(agent.process_and_route())
            self.assertFalse((Path(d) / "googledrive" / "decision_log.jsonl").exists())

    def test_empty_staging_does_not_append_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            stage = Path(d) / "googledrive" / "inbound_staging"
            stage.mkdir(parents=True)
            (stage / ".gitkeep").write_text("", encoding="utf-8")
            agent = module.DriveSyncAgent(Path(d))
            self.assertFalse(agent.process_and_route())
            self.assertFalse((Path(d) / "googledrive" / "decision_log.jsonl").exists())

    def test_notebook_fallback_remains_review_only(self):
        with tempfile.TemporaryDirectory() as d:
            agent = module.DriveSyncAgent(Path(d))
            decision = agent.evaluate_artifact_locally("sample.ipynb", '{"cells":[]}')
            self.assertEqual(decision["strategy"], "PARALLEL")
            self.assertEqual(
                decision["target_path"], "googledrive/parallel_refs/sample.ipynb"
            )
            self.assertEqual(
                agent.evaluate_artifact_locally("API_Key.ipynb", "{}")["strategy"],
                "DISCARD",
            )


if __name__ == "__main__":
    unittest.main()
