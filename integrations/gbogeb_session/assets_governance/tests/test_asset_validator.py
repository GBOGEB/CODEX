"""Tests for GBOGEB/CODEX asset_validator.py."""

import json
from pathlib import Path

import pytest

from src.asset_validator import (
    ALLOWED_EXTENSIONS,
    ValidationResult,
    create_mock_sidecar,
    extract_svg_metadata,
    get_mime_type,
    now_iso,
    sha256_hash,
    validate_asset,
    process_directory,
)


class TestSha256Hash:
    def test_deterministic(self, sample_svg):
        h1 = sha256_hash(sample_svg)
        h2 = sha256_hash(sample_svg)
        assert h1 == h2

    def test_correct_length(self, sample_svg):
        h = sha256_hash(sample_svg)
        assert len(h) == 64

    def test_hex_chars(self, sample_svg):
        h = sha256_hash(sample_svg)
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_files_different_hashes(self, sample_svg, sample_png):
        assert sha256_hash(sample_svg) != sha256_hash(sample_png)


class TestGetMimeType:
    def test_svg(self):
        assert get_mime_type("test.svg") == "image/svg+xml"

    def test_png(self):
        assert get_mime_type("test.png") == "image/png"

    def test_drawio(self):
        assert get_mime_type("test.drawio") == "application/xml"

    def test_unknown(self):
        mt = get_mime_type("test.xyz123")
        assert mt == "application/octet-stream"


class TestNowIso:
    def test_format(self):
        ts = now_iso()
        assert ts.endswith("Z")
        assert "T" in ts
        assert len(ts) == 20


class TestExtractSvgMetadata:
    def test_with_viewbox_and_title(self, sample_svg):
        # sample_svg has width/height but no explicit viewBox in the tag
        meta = extract_svg_metadata(sample_svg)
        assert meta["has_title"] is True
        assert isinstance(meta["id_count"], int)

    def test_no_title(self, sample_svg_no_title):
        meta = extract_svg_metadata(sample_svg_no_title)
        assert meta["has_title"] is False
        assert meta["has_viewbox"] is True


class TestValidateAsset:
    def test_valid_svg(self, sample_svg):
        result = validate_asset(sample_svg)
        assert result.passed
        assert len(result.sha256) == 64
        assert result.file_size > 0
        assert result.mime_type == "image/svg+xml"

    def test_valid_png(self, sample_png):
        result = validate_asset(sample_png)
        assert result.passed

    def test_nonexistent_file(self, tmp_dir):
        result = validate_asset(tmp_dir / "nope.svg")
        assert not result.passed
        assert any("not found" in e.lower() for e in result.errors)

    def test_unsupported_extension(self, tmp_dir):
        bad_file = tmp_dir / "test.xyz"
        bad_file.write_text("data")
        result = validate_asset(bad_file)
        assert any("unsupported" in e.lower() for e in result.errors)

    def test_svg_warnings(self, sample_svg_no_title):
        result = validate_asset(sample_svg_no_title)
        assert result.passed  # warnings don't fail
        assert any("title" in w.lower() for w in result.warnings)

    def test_to_dict(self, sample_svg):
        result = validate_asset(sample_svg)
        d = result.to_dict()
        assert "filepath" in d
        assert "passed" in d
        assert "sha256" in d


class TestCreateMockSidecar:
    def test_creates_mock_file(self, sample_svg, tmp_dir):
        mock_path = create_mock_sidecar(sample_svg, tmp_dir)
        assert mock_path.exists()
        assert mock_path.suffix == ".mock"

    def test_mock_content_valid_json(self, sample_svg, tmp_dir):
        mock_path = create_mock_sidecar(sample_svg, tmp_dir)
        data = json.loads(mock_path.read_text())
        assert "filename" in data
        assert "sha256" in data
        assert "processing_status" in data
        assert data["processing_status"] == "verified"

    def test_mock_contains_svg_metadata(self, sample_svg, tmp_dir):
        mock_path = create_mock_sidecar(sample_svg, tmp_dir)
        data = json.loads(mock_path.read_text())
        assert "svg_metadata" in data


class TestProcessDirectory:
    def test_process_svgs(self, tmp_dir):
        # Create test SVGs
        for i in range(3):
            svg = tmp_dir / f"test_{i}.svg"
            svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><title>Test {i}</title><rect width="100" height="100"/></svg>')
        results = process_directory(tmp_dir)
        assert len(results) == 3
        assert all(r.passed for r in results)

    def test_skips_non_assets(self, tmp_dir):
        (tmp_dir / "readme.md").write_text("# Test")
        (tmp_dir / "test.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>T</title></svg>')
        results = process_directory(tmp_dir)
        assert len(results) == 1

    def test_empty_directory(self, tmp_dir):
        empty = tmp_dir / "empty"
        empty.mkdir()
        results = process_directory(empty)
        assert len(results) == 0


class TestCanonicalAssets:
    """Test actual canonical assets in the repo."""

    def test_canonical_svgs_exist(self, canonical_svgs):
        assert len(canonical_svgs) >= 2

    def test_canonical_svgs_valid(self, canonical_svgs):
        for svg_path in canonical_svgs:
            result = validate_asset(svg_path)
            assert result.passed, f"Validation failed for {svg_path.name}: {result.errors}"
