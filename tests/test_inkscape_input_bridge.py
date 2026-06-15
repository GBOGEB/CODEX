from pathlib import Path
from zipfile import ZipFile

from tools.inkscape_input_bridge import (
    build_bridge_manifest,
    extract_expected_inputs_from_zip,
    inventory_inkscape_source,
)


def test_extract_expected_inputs_from_nested_zip(tmp_path: Path) -> None:
    source_zip = tmp_path / "inkscape-inputs.zip"
    with ZipFile(source_zip, "w") as archive:
        archive.writestr("nested/PFD-PID MINERVA QCELL-LB.svg", "<svg />")
        archive.writestr("nested/PID MINERVA CryoCell (QCELL-LB).pptx", b"ppt")
        archive.writestr("nested/ignored.txt", "ignore")

    result = extract_expected_inputs_from_zip(source_zip, tmp_path)

    extracted_paths = {item["output_path"] for item in result["extracted"]}
    assert "data/svg/PFD-PID MINERVA QCELL-LB.svg" in extracted_paths
    assert "data/ppt/PID MINERVA CryoCell (QCELL-LB).pptx" in extracted_paths
    assert (tmp_path / "data/svg/PFD-PID MINERVA QCELL-LB.svg").exists()
    assert len(result["missing"]) == 3


def test_inventory_inkscape_source_records_standard_dirs(tmp_path: Path) -> None:
    (tmp_path / "share/extensions").mkdir(parents=True)
    (tmp_path / "share/extensions/example.inx").write_text(
        "<inkscape-extension />", encoding="utf-8"
    )
    (tmp_path / "share/palettes").mkdir(parents=True)
    (tmp_path / "share/palettes/default.gpl").write_text(
        "GIMP Palette", encoding="utf-8"
    )

    inventory = inventory_inkscape_source(tmp_path)

    assert inventory["source_type"] == "directory"
    assert inventory["standard_paths"]["extensions"]["found"] is True
    assert inventory["standard_paths"]["palettes"]["file_count"] == 1


def test_bridge_manifest_preserves_policy_and_repo_reference(tmp_path: Path) -> None:
    source_zip = tmp_path / "inputs.zip"
    with ZipFile(source_zip, "w") as archive:
        archive.writestr("PFD-PID MINERVA RFCELL seen by ACR.svg", "<svg />")

    manifest = build_bridge_manifest(
        input_zip=source_zip,
        inkscape_source=None,
        repo_url="https://gitlab.com/GBOGEB/inkscape/-/tree/master",
        destination_root=tmp_path,
    )

    assert manifest["repo_url"] == "https://gitlab.com/GBOGEB/inkscape/-/tree/master"
    assert manifest["policy"]["primary_source"] == "svg_xml_from_inkscape_bundle"
    assert manifest["policy"]["rasterize"] is False
    assert any(item["found"] for item in manifest["expected_inputs"])
