import argparse
import json
import os
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ABACUS = ROOT / 'abacus_runtime'
EXPORT = ROOT / 'outputs' / 'runtime_export'


def export_abacus_runtime(
    source_dir: Path | None = None,
    export_dir: Path | None = None,
    report_path: Path | None = None,
) -> dict:
    source_dir = source_dir or ABACUS
    export_dir = export_dir or EXPORT

    if not source_dir.is_dir():
        raise FileNotFoundError(f"ABACUS runtime source not found: {source_dir}")

    if export_dir.exists():
        shutil.rmtree(export_dir)

    export_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    copied_directory_count = 0

    for item in source_dir.iterdir():
        target = export_dir / item.name

        if item.is_file():
            shutil.copy2(item, target)
            copied_files.append(item.name)
        elif item.is_dir():
            shutil.copytree(item, target)
            copied_directory_count += 1
            for root, _, files in os.walk(item):
                root_path = Path(root)
                copied_files.extend(
                    str((root_path / file_name).relative_to(source_dir))
                    for file_name in files
                )

    manifest_path = source_dir / 'runtime_manifest.yaml'
    manifest = {}
    if manifest_path.exists():
        manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8')) or {}

    report = {
        "bridge": "CODEX_ABACUS_RUNTIME_EXPORT",
        "source_dir": str(source_dir),
        "export_dir": str(export_dir),
        "runtime_name": manifest.get("runtime", {}).get("name", source_dir.name),
        "runtime_version": manifest.get("runtime", {}).get("version"),
        "modules": manifest.get("modules", []),
        "deployment": manifest.get("deployment", {}),
        "copied_file_count": len(copied_files),
        "copied_directory_count": copied_directory_count,
        "copied_files": sorted(copied_files),
    }

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Export ABACUS runtime assets for CODEX bridge workflows.')
    parser.add_argument(
        '--report-json',
        type=Path,
        help='Optional path to write a machine-readable bridge export report.',
    )
    args = parser.parse_args(argv)

    report = export_abacus_runtime(report_path=args.report_json)
    print(
        json.dumps(
            {
                "status": "exported",
                "runtime_name": report["runtime_name"],
                "runtime_version": report["runtime_version"],
                "copied_file_count": report["copied_file_count"],
                "copied_directory_count": report["copied_directory_count"],
                "report_path": str(args.report_json) if args.report_json else None,
            }
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
