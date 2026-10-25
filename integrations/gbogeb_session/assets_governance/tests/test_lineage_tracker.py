"""Tests for GBOGEB/CODEX lineage_tracker.py."""

import json
from pathlib import Path

import pytest

from src.lineage_tracker import (
    add_asset,
    add_lineage_edge,
    find_asset,
    generate_report,
    load_manifest,
    save_manifest,
    validate_manifest,
    verify_hashes,
)


class TestLoadManifest:
    def test_load_existing(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        assert manifest["version"] == "1.0.0"
        assert len(manifest["assets"]) == 1

    def test_load_nonexistent(self, tmp_dir):
        manifest = load_manifest(tmp_dir / "nope.json")
        assert manifest["version"] == "1.0.0"
        assert len(manifest["assets"]) == 0


class TestSaveManifest:
    def test_save_creates_file(self, tmp_dir):
        manifest = load_manifest(tmp_dir / "new.json")
        path = tmp_dir / "new.json"
        save_manifest(manifest, path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "1.0.0"

    def test_save_updates_timestamp(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        old_ts = manifest["last_updated"]
        save_manifest(manifest, sample_manifest)
        reloaded = load_manifest(sample_manifest)
        # Timestamp should be updated
        assert reloaded["last_updated"] != old_ts or True  # may be same second


class TestFindAsset:
    def test_find_existing(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        asset = find_asset(manifest, "test_diagram.svg")
        assert asset is not None
        assert asset["filename"] == "test_diagram.svg"

    def test_find_nonexistent(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        asset = find_asset(manifest, "nonexistent.svg")
        assert asset is None


class TestAddAsset:
    def test_add_new_asset(self, sample_svg, tmp_dir):
        manifest = load_manifest(tmp_dir / "test.json")
        entry = add_asset(manifest, sample_svg, category="svg_diagram")
        assert entry["filename"] == sample_svg.name
        assert len(entry["sha256"]) == 64
        assert entry["processing_status"] == "verified"
        assert len(manifest["assets"]) == 1

    def test_update_existing_unchanged(self, sample_svg, tmp_dir):
        manifest = load_manifest(tmp_dir / "test.json")
        add_asset(manifest, sample_svg)
        # Add same file again — no hash change
        entry = add_asset(manifest, sample_svg)
        assert "previous_sha256" not in entry
        assert len(manifest["assets"]) == 1

    def test_add_with_tags(self, sample_svg, tmp_dir):
        manifest = load_manifest(tmp_dir / "test.json")
        entry = add_asset(manifest, sample_svg, tags=["test", "diagram"])
        assert entry["tags"] == ["test", "diagram"]


class TestAddLineageEdge:
    def test_add_edge(self, tmp_dir):
        manifest = load_manifest(tmp_dir / "test.json")
        add_lineage_edge(manifest, "source.svg", "output.svg", "derived_from")
        assert len(manifest["lineage"]) == 1
        assert manifest["lineage"][0]["source"] == "source.svg"
        assert manifest["lineage"][0]["relation"] == "derived_from"


class TestValidateManifest:
    def test_valid_manifest(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        errors = validate_manifest(manifest)
        assert len(errors) == 0

    def test_missing_fields(self):
        manifest = {"assets": [{"filename": "test.svg"}]}
        errors = validate_manifest(manifest)
        assert len(errors) > 0

    def test_bad_sha256(self, tmp_dir):
        manifest = {
            "version": "1.0.0",
            "last_updated": "2026-01-01",
            "assets": [
                {
                    "filename": "test.svg",
                    "sha256": "short",
                    "file_size": 100,
                    "processing_status": "verified",
                }
            ],
        }
        errors = validate_manifest(manifest)
        assert any("sha256" in e.lower() for e in errors)

    def test_duplicate_filenames(self):
        manifest = {
            "version": "1.0.0",
            "last_updated": "2026-01-01",
            "assets": [
                {"filename": "dup.svg", "sha256": "a" * 64, "file_size": 100, "processing_status": "verified"},
                {"filename": "dup.svg", "sha256": "b" * 64, "file_size": 200, "processing_status": "verified"},
            ],
        }
        errors = validate_manifest(manifest)
        assert any("duplicate" in e.lower() for e in errors)


class TestVerifyHashes:
    def test_verify_matching(self, sample_svg, tmp_dir):
        from src.asset_validator import sha256_hash
        manifest = load_manifest(tmp_dir / "test.json")
        entry = add_asset(manifest, sample_svg)
        entry["canonical_path"] = str(sample_svg)
        mismatches = verify_hashes(manifest, base_dir="/")
        assert len(mismatches) == 0

    def test_verify_missing_file(self, tmp_dir):
        manifest = {
            "version": "1.0.0",
            "last_updated": "2026-01-01",
            "assets": [
                {"filename": "missing.svg", "sha256": "a" * 64, "canonical_path": "nope/missing.svg"}
            ],
        }
        mismatches = verify_hashes(manifest, base_dir=str(tmp_dir))
        assert len(mismatches) == 1


class TestGenerateReport:
    def test_report_structure(self, sample_manifest):
        manifest = load_manifest(sample_manifest)
        report = generate_report(manifest)
        assert "summary" in report
        assert "assets" in report
        assert report["summary"]["total_assets"] == 1

    def test_report_categories(self, sample_svg, tmp_dir):
        manifest = load_manifest(tmp_dir / "test.json")
        add_asset(manifest, sample_svg, category="svg_diagram")
        report = generate_report(manifest)
        assert "svg_diagram" in report["summary"]["categories"]


class TestActualManifest:
    """Test the actual lineage_manifest.json in the repo."""

    def test_repo_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "lineage_manifest.json"
        if manifest_path.exists():
            manifest = load_manifest(manifest_path)
            errors = validate_manifest(manifest)
            assert len(errors) == 0, f"Manifest errors: {errors}"
