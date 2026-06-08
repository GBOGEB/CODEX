from pathlib import Path

from tools.validators.master_input_validator import (
    REQUIRED_FOLDERS,
    generate_report,
    validate_master_input,
)


def _create_required_tree(root: Path) -> None:
    for folder in REQUIRED_FOLDERS:
        (root / folder).mkdir(parents=True)


def test_validate_master_input_passes_required_tree(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_tree(root)
    (root / "ITT" / "ITT Baseline.pdf").write_text("demo", encoding="utf-8")

    report = validate_master_input(root)

    assert report["valid"] is True
    assert report["findings"] == []


def test_validate_master_input_reports_missing_folders(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    root.mkdir()
    (root / "ITT").mkdir()

    report = validate_master_input(root)

    assert report["valid"] is False
    missing_codes = [finding["code"] for finding in report["findings"]]
    assert missing_codes.count("missing_folder") == len(REQUIRED_FOLDERS) - 1


def test_validate_master_input_reports_duplicates_and_bad_names(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_tree(root)
    (root / "ITT" / "Offer.pdf").write_text("one", encoding="utf-8")
    (root / "Applicant" / "offer.PDF").write_text("two", encoding="utf-8")
    (root / "SoR" / "bad@name.txt").write_text("bad", encoding="utf-8")

    report = validate_master_input(root)

    assert report["valid"] is False
    codes = {finding["code"] for finding in report["findings"]}
    assert {"duplicate_file", "naming_convention"} <= codes


def test_generate_report_writes_master_input_outputs(tmp_path: Path) -> None:
    root = tmp_path / "MASTER_input"
    _create_required_tree(root)
    report = validate_master_input(root)

    outputs = generate_report(
        report,
        json_path=tmp_path / "master_input_validation.json",
        markdown_path=tmp_path / "master_input_validation.md",
    )

    assert outputs["json"].exists()
    assert outputs["markdown"].exists()
    assert "MASTER_input Validation Report" in outputs["markdown"].read_text(
        encoding="utf-8"
    )
