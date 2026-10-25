"""Tests for GBOGEB/CODEX svg_cleaner.py."""

import re
from pathlib import Path

import pytest

from src.svg_cleaner import (
    clean_svg,
    clean_file,
    collapse_whitespace,
    ensure_title,
    inject_ids,
    normalize_viewbox,
    remove_editor_attributes,
    remove_editor_elements,
    remove_editor_namespaces,
    remove_xml_comments,
)


class TestRemoveXmlComments:
    def test_removes_comments(self):
        svg = '<svg><!-- comment --><rect/></svg>'
        result = remove_xml_comments(svg)
        assert "<!--" not in result
        assert "<rect/>" in result

    def test_removes_multiline_comments(self):
        svg = '<svg>\n<!-- multi\nline\ncomment -->\n<rect/></svg>'
        result = remove_xml_comments(svg)
        assert "<!--" not in result

    def test_preserves_content(self):
        svg = '<svg><rect fill="#f00"/></svg>'
        result = remove_xml_comments(svg)
        assert result == svg


class TestRemoveEditorNamespaces:
    def test_removes_inkscape_ns(self):
        svg = '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
        result = remove_editor_namespaces(svg)
        assert "inkscape" not in result

    def test_removes_sodipodi_ns(self):
        svg = '<svg xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd">'
        result = remove_editor_namespaces(svg)
        assert "sodipodi" not in result

    def test_preserves_svg_ns(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg">'
        result = remove_editor_namespaces(svg)
        assert 'xmlns="http://www.w3.org/2000/svg"' in result


class TestRemoveEditorAttributes:
    def test_removes_inkscape_attrs(self):
        svg = '<rect inkscape:label="test" width="100"/>'
        result = remove_editor_attributes(svg)
        assert "inkscape:" not in result
        assert 'width="100"' in result

    def test_removes_data_name(self):
        svg = '<rect data-name="test" width="100"/>'
        result = remove_editor_attributes(svg)
        assert "data-name" not in result


class TestRemoveEditorElements:
    def test_removes_sodipodi_element(self):
        svg = '<svg><sodipodi:namedview pagecolor="#fff"/><rect/></svg>'
        result = remove_editor_elements(svg)
        assert "sodipodi" not in result
        assert "<rect/>" in result

    def test_removes_metadata(self):
        svg = '<svg><metadata><rdf:RDF/></metadata><rect/></svg>'
        result = remove_editor_elements(svg)
        assert "<metadata" not in result
        assert "<rect/>" in result


class TestNormalizeViewbox:
    def test_adds_viewbox(self):
        svg = '<svg width="400" height="300">'
        result = normalize_viewbox(svg)
        assert 'viewBox="0 0 400 300"' in result

    def test_preserves_existing_viewbox(self):
        svg = '<svg viewBox="0 0 800 600" width="400" height="300">'
        result = normalize_viewbox(svg)
        assert 'viewBox="0 0 800 600"' in result

    def test_no_dimensions(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg">'
        result = normalize_viewbox(svg)
        assert result == svg  # unchanged


class TestEnsureTitle:
    def test_adds_title(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        result = ensure_title(svg, "My Title")
        assert "<title>My Title</title>" in result

    def test_preserves_existing_title(self):
        svg = '<svg><title>Existing</title><rect/></svg>'
        result = ensure_title(svg, "New Title")
        assert "<title>Existing</title>" in result
        assert "New Title" not in result


class TestInjectIds:
    def test_injects_rect_id(self):
        svg = '<rect width="100" height="50"/>'
        result = inject_ids(svg, prefix="gbc")
        assert 'id="gbc-rect-001"' in result

    def test_skips_existing_ids(self):
        svg = '<rect id="my-rect" width="100"/>'
        result = inject_ids(svg, prefix="gbc")
        assert 'id="my-rect"' in result
        assert 'id="gbc-' not in result

    def test_multiple_elements(self):
        svg = '<rect width="10"/><circle cx="5" cy="5" r="5"/><text>Hi</text>'
        result = inject_ids(svg, prefix="test")
        assert 'id="test-rect-001"' in result
        assert 'id="test-circle-002"' in result
        assert 'id="test-text-003"' in result


class TestCleanSvg:
    def test_full_pipeline(self, sample_svg):
        content = sample_svg.read_text()
        cleaned = clean_svg(content, do_inject_ids=True, id_prefix="gbc")
        assert "inkscape" not in cleaned.lower() or "inkscape" not in cleaned
        assert "sodipodi" not in cleaned
        assert "<!--" not in cleaned
        assert "<metadata" not in cleaned

    def test_preserves_visual_elements(self, sample_svg):
        content = sample_svg.read_text()
        cleaned = clean_svg(content)
        assert "<rect" in cleaned
        assert "<circle" in cleaned
        assert "<text" in cleaned


class TestCleanFile:
    def test_clean_to_output(self, sample_svg, tmp_dir):
        output = tmp_dir / "output" / "cleaned.svg"
        cleaned = clean_file(sample_svg, output)
        assert output.exists()
        assert "<rect" in cleaned

    def test_nonexistent_file(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            clean_file(tmp_dir / "nope.svg")

    def test_non_svg_file(self, sample_png):
        with pytest.raises(ValueError):
            clean_file(sample_png)


class TestCanonicalSvgCleaning:
    """Test cleaning actual canonical assets."""

    def test_canonical_svgs_cleanable(self, canonical_svgs, tmp_dir):
        for svg_path in canonical_svgs:
            output = tmp_dir / svg_path.name
            cleaned = clean_file(svg_path, output)
            assert len(cleaned) > 0
            assert "<svg" in cleaned
