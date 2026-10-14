"""Static acceptance controls for the read-only monochrome process reader.

These tests deliberately do not claim executed browser/runner/worker proof.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "federation" / "mesh"
HTML = ROOT / "CODE_PURPLE_EVERRED_MONOCHROME_READER_v0.2.html"
DAG = ROOT / "CODE_PURPLE_EVERRED_MONOCHROME_FLOW_v0.2.mmd"
CONTRACT = ROOT / "CODE_PURPLE_EVERRED_GRAPH_REVIEW_v0.2.md"


class MonochromeReaderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.diagram = DAG.read_text(encoding="utf-8")
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_eight_stages_present_in_html_and_mermaid(self):
        for n in range(1, 9):
            stage = f"S{n:02d}"
            with self.subTest(stage=stage):
                self.assertIn(stage, self.html)
                self.assertIn(stage, self.diagram)

    def test_no_semantic_colour_palette(self):
        # Only grayscale hex colours may be used in HTML.
        for hexval in re.findall(r"#[0-9a-fA-F]{3,8}\b", self.html):
            h = hexval[1:]
            if len(h) == 3:
                rgb = [int(d, 16) for d in h]
            elif len(h) in (6, 8):
                rgb = [int(h[i:i+2], 16) for i in (0, 2, 4)]
            else:
                continue
            self.assertEqual(len(set(rgb)), 1, hexval)

    def test_reading_legend_is_explicit(self):
        for label in (
            "Basic reading legend", "ordinary advancement",
            "first-red repair", ".self re-entry",
            "pay_it_forward proposal", "HOLD / watch",
            "Rectangle: stage", "Diamond: decision",
            "admission gate", "No observation",
        ):
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_disclosure_and_keyboard_friendly_contract(self):
        for marker in (
            'id="details"', "<summary>", "aria-pressed",
            "focus-visible", "id=\"expand\"", "id=\"collapse\"",
        ):
            self.assertIn(marker, self.html)

    def test_n_minus_ten_is_not_synthetic_green(self):
        for value in ("N−10", "N−9", "N−8", "N−7", "N−6",
                      "N−5", "N−4", "N−3", "N−2", "N−1"):
            self.assertIn(value, self.html)
        self.assertIn("NOT_TRIGGERED", self.html)
        self.assertIn("QUEUED AT SNAPSHOT", self.html)

    def test_recensus_needs_identity_and_rejects_conflict(self):
        for marker in (
            "code-purple.observation.v1", "run_attempt", "job_id",
            "source_sha", "observed_at", "Contradictory",
            "Number.isSafeInteger", "receipts", "UNVERIFIED",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("https://cdn.", self.html)

    def test_crews_are_roles_not_launch_claims(self):
        for role in ("Reader", "Deep Reader", "Scout", "Ambulance",
                     "Dispatcher", "Repair Worker", "Runtime/LDAB",
                     "Independent Reviewer", "REX Historian"):
            self.assertIn(role, self.html)
        self.assertIn("UNKNOWN", self.html)

    def test_canonical_methods_and_authority_retained(self):
        for method in ("CODE PURPLE", "EVERRED", "NEVERGREEN", "3PR",
                       "MIP", "3PC", "3P3", "DMAIC", "QPS"):
            self.assertIn(method, self.contract)
        self.assertIn("not an independent scheduler", self.contract.lower())
        self.assertIn("protected main", self.contract)


if __name__ == "__main__":
    unittest.main()
