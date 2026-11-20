"""Unit calibration for the existing native PPTX geometry runtime."""
import importlib.util
from pathlib import Path
import sys
import unittest

from pptx.util import Emu, Inches, Mm

PATH = Path(__file__).resolve().parents[1] / "src/ingress/pptx_geometry_semantic_runtime_v1.py"
SPEC = importlib.util.spec_from_file_location("pptx_geometry_units_owner", PATH)
owner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = owner
SPEC.loader.exec_module(owner)


class GeometryUnitTests(unittest.TestCase):
    def test_known_physical_lengths(self):
        convert = owner.PPTXGeometrySemanticRuntime.emu_to_mm
        self.assertEqual(convert(Inches(1)), 25.4)
        self.assertEqual(convert(Mm(1)), 1.0)
        self.assertEqual(convert(Mm(210)), 210.0)
        self.assertEqual(convert(0), 0.0)

    def test_native_length_oracle_including_negative_coordinates(self):
        for value in (-914400, -1, 1, 36000, 914400, 12192000, 6858000):
            with self.subTest(value=value):
                self.assertEqual(owner.PPTXGeometrySemanticRuntime.emu_to_mm(value), round(Emu(value).mm, 3))


if __name__ == "__main__":
    unittest.main()
