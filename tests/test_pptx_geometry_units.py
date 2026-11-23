"""Unit calibration for the existing native PPTX geometry runtime."""

import builtins
import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Emu, Inches, Mm

PATH = (
    Path(__file__).resolve().parents[1]
    / "src/ingress/pptx_geometry_semantic_runtime_v1.py"
)
SPEC = importlib.util.spec_from_file_location("pptx_geometry_units_owner", PATH)
owner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = owner
SPEC.loader.exec_module(owner)


class GeometryUnitTests(unittest.TestCase):
    def test_direct_geometry_import_and_conversion_do_not_require_pandas(self):
        original_import = builtins.__import__

        def without_pandas(name, *args, **kwargs):
            if name == "pandas" or name.startswith("pandas."):
                raise ModuleNotFoundError("pandas intentionally unavailable")
            return original_import(name, *args, **kwargs)

        spec = importlib.util.spec_from_file_location("geometry_without_pandas", PATH)
        module = importlib.util.module_from_spec(spec)
        with (
            patch.dict(sys.modules, {spec.name: module}),
            patch("builtins.__import__", side_effect=without_pandas),
        ):
            spec.loader.exec_module(module)
            self.assertEqual(
                module.PPTXGeometrySemanticRuntime.emu_to_mm(Inches(1)), 25.4
            )

    def test_full_export_uses_declared_dependency_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "generic.pptx"
            deck = Presentation()
            slide = deck.slides.add_slide(deck.slide_layouts[6])
            shape = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(3), Inches(1))
            shape.text = "Flow connection"
            deck.save(source)
            original_digest = hashlib.sha256(source.read_bytes()).hexdigest()
            result = owner.PPTXGeometrySemanticRuntime(source, root / "out").execute()
            rows = json.loads(Path(result["json"]).read_text())
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["left_mm"], 25.4)
            self.assertEqual(rows[0]["top_mm"], 50.8)
            self.assertEqual(rows[0]["semantic_role"], "FLOW_OBJECT")
            with Path(result["csv"]).open(newline="") as stream:
                csv_rows = list(csv.DictReader(stream))
            self.assertEqual(csv_rows[0]["extracted_text"], "Flow connection")
            summary = json.loads(Path(result["summary"]).read_text())
            self.assertEqual(summary["slides"], 1)
            self.assertEqual(summary["shapes"], 1)
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).hexdigest(), original_digest
            )

    def test_placeholder_fallback_remains_available_with_diagnostic(self):
        class BrokenPlaceholder:
            is_placeholder = True
            shape_type = MSO_SHAPE_TYPE.AUTO_SHAPE

            @property
            def placeholder_format(self):
                raise RuntimeError("synthetic unavailable placeholder metadata")

        with self.assertLogs(owner.logger, level="DEBUG"):
            self.assertEqual(
                owner.PPTXGeometrySemanticRuntime.semantic_role(
                    BrokenPlaceholder(), ""
                ),
                "GENERAL",
            )

    def test_connector_fallback_remains_available_with_diagnostic(self):
        class BrokenConnector:
            @property
            def shape_type(self):
                raise RuntimeError("synthetic unavailable shape metadata")

        with self.assertLogs(owner.logger, level="DEBUG"):
            self.assertFalse(
                owner.PPTXGeometrySemanticRuntime.connector_like(BrokenConnector())
            )

    def test_known_physical_lengths(self):
        convert = owner.PPTXGeometrySemanticRuntime.emu_to_mm
        self.assertEqual(convert(Inches(1)), 25.4)
        self.assertEqual(convert(Mm(1)), 1.0)
        self.assertEqual(convert(Mm(210)), 210.0)
        self.assertEqual(convert(0), 0.0)

    def test_native_length_oracle_including_negative_coordinates(self):
        for value in (-914400, -1, 1, 36000, 914400, 12192000, 6858000):
            with self.subTest(value=value):
                self.assertEqual(
                    owner.PPTXGeometrySemanticRuntime.emu_to_mm(value),
                    round(Emu(value).mm, 3),
                )


if __name__ == "__main__":
    unittest.main()
