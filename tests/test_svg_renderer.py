"""Tests for renderers/svg_renderer.py (W003.2)."""
from __future__ import annotations

import pytest

from renderers.svg_renderer import SVGRenderer, LINEAGE


# ---------------------------------------------------------------------------
# SVG root validation
# ---------------------------------------------------------------------------

class TestSVGRoot:
    def test_svg_root_tag_present(self):
        output = SVGRenderer(200, 100).render()
        assert output.startswith("<svg")

    def test_svg_xmlns_attribute(self):
        output = SVGRenderer(200, 100).render()
        assert 'xmlns="http://www.w3.org/2000/svg"' in output

    def test_svg_width_height_in_output(self):
        output = SVGRenderer(300, 150).render()
        assert 'width="300"' in output
        assert 'height="150"' in output

    def test_viewbox_matches_dimensions(self):
        output = SVGRenderer(400, 200).render()
        assert 'viewBox="0 0 400 200"' in output

    def test_wave_lineage_attribute(self):
        output = SVGRenderer(100, 100).render()
        assert 'data-wave="W003"' in output

    def test_renderer_lineage_attribute(self):
        output = SVGRenderer(100, 100).render()
        assert 'data-renderer="svg"' in output


# ---------------------------------------------------------------------------
# SVG generation
# ---------------------------------------------------------------------------

class TestSVGGeneration:
    def test_render_returns_string(self):
        result = SVGRenderer(400, 300).render()
        assert isinstance(result, str)

    def test_render_contains_closing_tag(self):
        result = SVGRenderer(400, 300).render()
        assert "</svg>" in result

    def test_add_rect_produces_rect_element(self):
        svg = SVGRenderer(400, 300)
        svg.add_rect(10, 10, 100, 40)
        assert "<rect" in svg.render()

    def test_add_line_produces_line_element(self):
        svg = SVGRenderer(400, 300)
        svg.add_line(0, 0, 100, 100)
        assert "<line" in svg.render()

    def test_add_text_produces_text_element(self):
        svg = SVGRenderer(400, 300)
        svg.add_text(50, 50, "Hello")
        output = svg.render()
        assert "<text" in output
        assert "Hello" in output

    def test_chaining_returns_self(self):
        svg = SVGRenderer(400, 300)
        result = svg.add_rect(0, 0, 10, 10).add_line(0, 0, 5, 5).add_text(5, 5, "x")
        assert result is svg

    def test_style_hook_included_in_output(self):
        svg = SVGRenderer(100, 100, style_hook=".node { fill: red; }")
        output = svg.render()
        assert "<style>" in output
        assert ".node { fill: red; }" in output


# ---------------------------------------------------------------------------
# Invalid schema / input rejection
# ---------------------------------------------------------------------------

class TestInvalidInputRejection:
    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            SVGRenderer(0, 100)

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            SVGRenderer(100, 0)

    def test_negative_dimensions_raise(self):
        with pytest.raises(ValueError):
            SVGRenderer(-1, -1)


# ---------------------------------------------------------------------------
# Lineage metadata
# ---------------------------------------------------------------------------

class TestLineage:
    def test_lineage_wave(self):
        assert LINEAGE["wave"] == "W003"

    def test_lineage_runtime_evidence(self):
        assert LINEAGE["runtime_evidence"] is True

    def test_lineage_property_returns_copy(self):
        svg = SVGRenderer(100, 100)
        meta = svg.lineage
        meta["wave"] = "TAMPERED"
        assert svg.lineage["wave"] == "W003"
