from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import scripts.check_bridge_alignment as bridge


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class CheckBridgeAlignmentTests(unittest.TestCase):
    def _paths_for_root(self, root: Path) -> dict:
        return {
            "ROOT": root,
            "BRIDGE_MAP_PATH": root / "federation" / "orchestration" / "codex_abacus_bridge_map.yaml",
            "ABACUS_MANIFEST_PATH": root / "abacus_runtime" / "runtime_manifest.yaml",
            "FEDERATION_CONTRACT_PATH": root / "governance" / "contracts" / "delta-1-runtime-federation-contract.yaml",
            "SYNC_PATH": root / "governance" / "synchronization" / "abacus-codex-recursive-sync.yaml",
            "SEMANTIC_SCHEMA_PATH": root / "federation" / "semantic_index" / "schema.yaml",
        }

    def test_validate_fails_when_required_files_are_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=False)

            self.assertEqual(exit_code, 1)
            self.assertIn("required files missing", buffer.getvalue())

    def test_validate_fails_for_unknown_module_and_missing_codex_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            _write(
                paths["BRIDGE_MAP_PATH"],
                """
bridge:
  module_alignment:
    - abacus_module: unknown_module
      codex_path: missing/path
""".strip(),
            )
            _write(paths["ABACUS_MANIFEST_PATH"], "modules:\n  - renderer\n")
            _write(paths["FEDERATION_CONTRACT_PATH"], "delta_1_runtime_federation_contract: {}\n")
            _write(paths["SYNC_PATH"], "abacus_codex_recursive_sync: {}\n")
            _write(paths["SEMANTIC_SCHEMA_PATH"], "type: object\n")

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=False)

            self.assertEqual(exit_code, 1)
            self.assertIn("is not defined in abacus_runtime/runtime_manifest.yaml", buffer.getvalue())
            self.assertIn("codex_path 'missing/path' does not exist", buffer.getvalue())

    def test_validate_reports_dormant_paths_in_non_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            _write(
                paths["BRIDGE_MAP_PATH"],
                """
bridge:
  module_alignment:
    - abacus_module: renderer
      codex_path: telemetry
""".strip(),
            )
            _write(paths["ABACUS_MANIFEST_PATH"], "modules:\n  - renderer\n")
            _write(paths["FEDERATION_CONTRACT_PATH"], "delta_1_runtime_federation_contract: {}\n")
            _write(paths["SYNC_PATH"], "abacus_codex_recursive_sync: {}\n")
            _write(paths["SEMANTIC_SCHEMA_PATH"], "type: object\n")
            _write(root / "telemetry" / ".gitkeep", "\n")

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=False)

            self.assertEqual(exit_code, 0)
            self.assertIn("dormant codex paths detected", buffer.getvalue())

    def test_validate_fails_on_dormant_paths_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            _write(
                paths["BRIDGE_MAP_PATH"],
                """
bridge:
  module_alignment:
    - abacus_module: renderer
      codex_path: telemetry
""".strip(),
            )
            _write(paths["ABACUS_MANIFEST_PATH"], "modules:\n  - renderer\n")
            _write(paths["FEDERATION_CONTRACT_PATH"], "delta_1_runtime_federation_contract: {}\n")
            _write(paths["SYNC_PATH"], "abacus_codex_recursive_sync: {}\n")
            _write(paths["SEMANTIC_SCHEMA_PATH"], "type: object\n")
            _write(root / "telemetry" / ".gitkeep", "\n")

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=True)

            self.assertEqual(exit_code, 1)
            self.assertIn("strict dormant mode is enabled", buffer.getvalue())

    def test_validate_reports_unmapped_modules_in_non_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            _write(
                paths["BRIDGE_MAP_PATH"],
                """
bridge:
  module_alignment:
    - abacus_module: renderer
      codex_path: dashboards
""".strip(),
            )
            _write(paths["ABACUS_MANIFEST_PATH"], "modules:\n  - renderer\n  - telemetry\n")
            _write(paths["FEDERATION_CONTRACT_PATH"], "delta_1_runtime_federation_contract: {}\n")
            _write(paths["SYNC_PATH"], "abacus_codex_recursive_sync: {}\n")
            _write(
                paths["SEMANTIC_SCHEMA_PATH"],
                "properties:\n  human_render:\n    properties:\n      status:\n        enum: [ACTIVE]\n",
            )
            _write(root / "dashboards" / ".gitkeep", "\n")

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=False, strict_coverage=False)

            self.assertEqual(exit_code, 0)
            self.assertIn("unmapped abacus modules detected", buffer.getvalue())
            self.assertIn("telemetry", buffer.getvalue())

    def test_validate_fails_on_unmapped_modules_in_strict_coverage_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths_for_root(root)

            _write(
                paths["BRIDGE_MAP_PATH"],
                """
bridge:
  module_alignment:
    - abacus_module: renderer
      codex_path: dashboards
""".strip(),
            )
            _write(paths["ABACUS_MANIFEST_PATH"], "modules:\n  - renderer\n  - telemetry\n")
            _write(paths["FEDERATION_CONTRACT_PATH"], "delta_1_runtime_federation_contract: {}\n")
            _write(paths["SYNC_PATH"], "abacus_codex_recursive_sync: {}\n")
            _write(
                paths["SEMANTIC_SCHEMA_PATH"],
                "properties:\n  human_render:\n    properties:\n      status:\n        enum: [ACTIVE]\n",
            )
            _write(root / "dashboards" / ".gitkeep", "\n")

            with patch.multiple(bridge, **paths):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = bridge.validate(strict_dormant=False, strict_coverage=True)

            self.assertEqual(exit_code, 1)
            self.assertIn("strict coverage mode is enabled", buffer.getvalue())
