import json
from pathlib import Path

import yaml

from scripts.export_abacus_runtime import export_abacus_runtime, main


def test_export_abacus_runtime_copies_files_and_reports_manifest(tmp_path: Path) -> None:
    source_dir = tmp_path / "abacus_runtime"
    export_dir = tmp_path / "runtime_export"
    report_path = tmp_path / "bridge_report.json"

    source_dir.mkdir()
    (source_dir / "README.md").write_text("# runtime\n", encoding="utf-8")
    (source_dir / "runtime_manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "runtime": {"name": "ABACUS_RUNTIME", "version": "0.1.0"},
                "modules": ["renderer", "telemetry"],
                "deployment": {"pages": {"enabled": True, "strategy": "github_actions"}},
            }
        ),
        encoding="utf-8",
    )
    nested = source_dir / "templates"
    nested.mkdir()
    (nested / "dashboard.html").write_text("<html></html>\n", encoding="utf-8")

    report = export_abacus_runtime(source_dir=source_dir, export_dir=export_dir, report_path=report_path)

    assert (export_dir / "README.md").read_text(encoding="utf-8") == "# runtime\n"
    assert (export_dir / "templates" / "dashboard.html").exists()
    assert report["runtime_name"] == "ABACUS_RUNTIME"
    assert report["runtime_version"] == "0.1.0"
    assert report["modules"] == ["renderer", "telemetry"]
    assert report["copied_file_count"] == 3
    assert sorted(report["copied_files"]) == ["README.md", "runtime_manifest.yaml", "templates/dashboard.html"]

    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert persisted_report == report


def test_main_writes_json_summary_and_report(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "repo"
    source_dir = root / "abacus_runtime"
    export_dir = root / "outputs" / "runtime_export"
    report_path = tmp_path / "bridge_report.json"

    source_dir.mkdir(parents=True)
    (source_dir / "runtime_manifest.yaml").write_text(
        yaml.safe_dump({"runtime": {"name": "ABACUS_RUNTIME", "version": "9.9.9"}}),
        encoding="utf-8",
    )
    (source_dir / "runtime_modules.md").write_text("modules\n", encoding="utf-8")

    monkeypatch.setattr("scripts.export_abacus_runtime.ABACUS", source_dir)
    monkeypatch.setattr("scripts.export_abacus_runtime.EXPORT", export_dir)

    assert main(["--report-json", str(report_path)]) == 0

    summary = json.loads(capsys.readouterr().out)
    assert summary["status"] == "exported"
    assert summary["runtime_name"] == "ABACUS_RUNTIME"
    assert summary["runtime_version"] == "9.9.9"
    assert summary["report_path"] == str(report_path)
