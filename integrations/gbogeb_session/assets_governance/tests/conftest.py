"""Shared fixtures for GBOGEB/CODEX tests."""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory."""
    return tmp_path


@pytest.fixture
def sample_svg(tmp_dir):
    """Create a sample SVG file for testing."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Created with Inkscape -->
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd"
     width="400" height="300"
     inkscape:version="1.2">
  <title>Test Diagram</title>
  <sodipodi:namedview pagecolor="#ffffff"/>
  <metadata>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <cc:Work xmlns:cc="http://creativecommons.org/ns#"/>
    </rdf:RDF>
  </metadata>
  <rect x="10" y="10" width="100" height="50" fill="#1a73e8" data-name="test"/>
  <circle cx="200" cy="150" r="40" fill="#34a853"/>
  <text x="100" y="200" font-size="14">Test Label</text>
</svg>'''
    svg_path = tmp_dir / "test_diagram.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    return svg_path


@pytest.fixture
def sample_svg_no_viewbox(tmp_dir):
    """SVG without viewBox attribute."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
  <rect x="0" y="0" width="200" height="100" fill="#ccc"/>
</svg>'''
    svg_path = tmp_dir / "no_viewbox.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    return svg_path


@pytest.fixture
def sample_svg_no_title(tmp_dir):
    """SVG without title element."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100" width="200" height="100">
  <rect x="0" y="0" width="200" height="100" fill="#ccc"/>
</svg>'''
    svg_path = tmp_dir / "no_title.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    return svg_path


@pytest.fixture
def sample_png(tmp_dir):
    """Create a minimal PNG file for testing."""
    # 1x1 white pixel PNG
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
        0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82,
    ])
    png_path = tmp_dir / "test_image.png"
    png_path.write_bytes(png_data)
    return png_path


@pytest.fixture
def sample_manifest(tmp_dir):
    """Create a sample lineage manifest."""
    manifest = {
        "version": "1.0.0",
        "last_updated": "2026-05-20T10:00:00Z",
        "repository": "GBOGEB/CODEX",
        "assets": [
            {
                "filename": "test_diagram.svg",
                "sha256": "a" * 64,
                "file_size": 1024,
                "mime_type": "image/svg+xml",
                "category": "svg_diagram",
                "tags": ["test"],
                "ingested_at": "2026-05-20T10:00:00Z",
                "git_commit": "abc1234",
                "processing_status": "verified",
                "canonical_path": "assets/canonical/test_diagram.svg",
                "mock_file": "test_diagram.svg.mock",
            }
        ],
        "lineage": [],
    }
    manifest_path = tmp_dir / "lineage_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


@pytest.fixture
def canonical_svgs():
    """Return paths to actual canonical SVG assets."""
    base = Path(__file__).parent.parent / "assets" / "canonical"
    return list(base.glob("*.svg"))
