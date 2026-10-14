"""Static accessibility checks for the CODE PURPLE convergence map."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "code_purple_convergence.html"
MERMAID = ROOT / "docs" / "diagrams" / "code_purple_convergence.mmd"
REX = ROOT / "docs" / "code_purple_rex_control.html"


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.labels = set()
        self.nav = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a":
            self.links.append(values.get("href"))
        if values.get("aria-label"):
            self.labels.add(values["aria-label"])
        if tag == "nav":
            self.nav.append(values)


def luminance(hex_color):
    channels = [int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055)/1.055)**2.4 for c in channels]
    return sum(a*b for a, b in zip((0.2126, 0.7152, 0.0722), linear))


def contrast(a, b):
    lum = sorted([luminance(a), luminance(b)])
    return (lum[1]+0.05)/(lum[0]+0.05)


class ConvergenceMapContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.mermaid = MERMAID.read_text(encoding="utf-8")
        cls.dom = Markup()
        cls.dom.feed(cls.html)

    def test_sticky_keyboard_navigator_and_legend(self):
        self.assertIn("Persistent convergence navigation", self.dom.labels)
        self.assertIn("Persistent color legend", self.dom.labels)
        self.assertIn("position:sticky", self.html)
        self.assertIn(".skip:focus", self.html)
        self.assertIn(":focus-visible", self.html)
        self.assertIn("prefers-reduced-motion", self.html)

    def test_six_navigation_targets_really_exist(self):
        for fragment in ("overview", "lanes", "verification", "top21", "boundaries", "sources"):
            with self.subTest(fragment=fragment):
                self.assertIn("#" + fragment, self.dom.links)
                self.assertIn(fragment, self.dom.ids)

    def test_narrow_viewport_fallback(self):
        self.assertIn("@media(max-width:700px)", self.html)
        self.assertIn("grid-template-columns:1fr", self.html)

    def test_existing_rex_control_links_to_page(self):
        self.assertIn(
            'href="code_purple_convergence.html"',
            REX.read_text(encoding="utf-8")
        )

    def test_mermaid_uses_distinct_class_fill_and_readable_text(self):
        classes = re.findall(
            r"classDef (\w+) fill:(#[0-9a-fA-F]{6}),stroke:(#[0-9a-fA-F]{6}),color:(#[0-9a-fA-F]{6})",
            self.mermaid,
        )
        self.assertEqual(5, len(classes))
        self.assertEqual(5, len({fill for _, fill, _, _ in classes}))
        for role, fill, stroke, ink in classes:
            with self.subTest(role=role):
                self.assertGreaterEqual(contrast(ink, fill), 4.5)
                self.assertGreaterEqual(contrast(stroke, fill), 3.0)

    def test_no_runtime_mutation_or_admission_claim(self):
        self.assertIn("No security waiver", self.html)
        self.assertIn("No authority transfer", self.html)
        self.assertIn("TOP21 is a ranking capacity", self.html)
        self.assertIn("Static architecture reference", self.html)
        self.assertNotIn("<script src=", self.html)


if __name__ == "__main__":
    unittest.main()
