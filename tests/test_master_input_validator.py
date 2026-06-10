from __future__ import annotations

from pathlib import Path

from tools.validators.master_input_validator import REQUIRED_FOLDERS, validate_master_input


def _create_required_folders(root: Path) -> None:
    for folder in REQUIRED_FOLDERS:
        (root / folder).mkdir(parents=True)


def test_validate_master_input_reports_missing_folders(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    root.mkdir()
    (root / "ITT").mkdir()

    result = validate_master_input(root)

    assert result["status"] == "fail"
    missing = [error for error in result["errors"] if error["code"] == "missing_required_folder"]
    assert len(missing) == len(REQUIRED_FOLDERS) - 1
    assert any("Applicant" in error["message"] for error in missing)


def test_validate_master_input_reports_duplicate_names(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_folders(root)
    (root / "ITT" / "requirement.yaml").write_text("id: one\n", encoding="utf-8")
    (root / "SoR" / "requirement.yaml").write_text("id: two\n", encoding="utf-8")

    result = validate_master_input(root)

    assert result["status"] == "fail"
    assert any(error["code"] == "duplicate_file_name" for error in result["errors"])


def test_validate_master_input_reports_invalid_names(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_folders(root)
    (root / "Contracts" / "bad name.yaml").write_text("id: bad\n", encoding="utf-8")

    result = validate_master_input(root)

    assert result["status"] == "fail"
    assert any(error["code"] == "invalid_file_name" for error in result["errors"])


def test_validate_master_input_passes_empty_required_tree(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_folders(root)

    result = validate_master_input(root)

    assert result["status"] == "pass"
    assert result["error_count"] == 0
