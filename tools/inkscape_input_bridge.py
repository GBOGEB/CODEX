"""Bridge Inkscape-authored input bundles into the ABACUS P&ID parser.

This module does not vendor or switch to the Inkscape repository. It records the
upstream/fork reference, inventories any local Inkscape source tree or source
zip supplied by the operator, and safely extracts only the expected P&ID SVG/PPT
inputs from an operator-provided zip into the repository ``data/`` folders.

The bridge keeps the nuance in the drawing XML: Inkscape layers, labels, ids,
styles, markers, and paths remain the source consumed by ``pid_semantic_parser``.
"""

from __future__ import annotations

import argparse
import json
import os
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable

DEFAULT_UPSTREAM_REPO_URL = "https://gitlab.com/inkscape/inkscape/-/tree/master"
DEFAULT_FORK_REPO_URL = os.environ.get(
    "GBOGEB_INKSCAPE_REPO_URL", DEFAULT_UPSTREAM_REPO_URL
)
DEFAULT_BRIDGE_MANIFEST = Path("data/model/inkscape_bridge_manifest.json")

EXPECTED_INPUTS = {
    "PFD-PID MINERVA QCELL-LB.svg": Path("data/svg/PFD-PID MINERVA QCELL-LB.svg"),
    "PFD-PID MINERVA RFCELL seen by ACR.svg": Path(
        "data/svg/PFD-PID MINERVA RFCELL seen by ACR.svg"
    ),
    "PFD-PID of RFCELL - MASTER.pptx": Path("data/ppt/PFD-PID of RFCELL - MASTER.pptx"),
    "PID MINERVA CryoCell (QCELL-LB).pptx": Path(
        "data/ppt/PID MINERVA CryoCell (QCELL-LB).pptx"
    ),
    "QSYS (and RFCELL) instrumentation location for LB and LBI.pptx": Path(
        "data/ppt/QSYS (and RFCELL) instrumentation location for LB and LBI.pptx"
    ),
}

INKSCAPE_STANDARD_PATHS = {
    "extensions": Path("share/extensions"),
    "palettes": Path("share/palettes"),
    "symbols": Path("share/symbols"),
    "templates": Path("share/templates"),
    "markers": Path("share/markers"),
    "paint_servers": Path("share/paint"),
    "ui": Path("share/ui"),
}

SVG_SOURCE_POLICY = {
    "primary_source": "svg_xml_from_inkscape_bundle",
    "ocr": False,
    "rasterize": False,
    "pdf_first": False,
    "preserve_inkscape_layers": True,
    "preserve_labels": True,
    "preserve_object_ids": True,
    "preserve_markers": True,
    "preserve_colours": True,
    "preserve_group_hierarchy": True,
}


@dataclass(frozen=True)
class ExtractedInput:
    """A safely extracted expected P&ID input file."""

    archive_member: str
    output_path: str
    size_bytes: int


@dataclass(frozen=True)
class MissingInput:
    """An expected P&ID input file that was not present in the bundle."""

    expected_name: str
    output_path: str


def _safe_member_name(member_name: str) -> PurePosixPath:
    path = PurePosixPath(member_name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe zip member path rejected: {member_name}")
    return path


def _iter_zip_names(zip_path: Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as archive:
        return [name for name in archive.namelist() if not name.endswith("/")]


def extract_expected_inputs_from_zip(
    zip_path: str | Path,
    destination_root: str | Path = Path("."),
) -> dict[str, list[dict[str, object]]]:
    """Extract only expected SVG/PPT files from a source zip into ``data/``.

    Matching is by exact basename so the operator can provide a zip with nested
    folders while keeping extraction constrained to the known P&ID source names.
    """

    source_zip = Path(zip_path)
    root = Path(destination_root)
    if not source_zip.is_file():
        raise FileNotFoundError(f"Input zip not found: {source_zip}")

    extracted: list[ExtractedInput] = []
    seen: set[str] = set()
    with zipfile.ZipFile(source_zip) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            safe_name = _safe_member_name(member.filename)
            basename = safe_name.name
            output = EXPECTED_INPUTS.get(basename)
            if output is None:
                continue
            target = root / output
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as sink:
                sink.write(source.read())
            extracted.append(
                ExtractedInput(
                    archive_member=member.filename,
                    output_path=str(output),
                    size_bytes=target.stat().st_size,
                )
            )
            seen.add(basename)

    missing = [
        MissingInput(expected_name=name, output_path=str(path))
        for name, path in EXPECTED_INPUTS.items()
        if name not in seen
    ]
    return {
        "extracted": [asdict(item) for item in extracted],
        "missing": [asdict(item) for item in missing],
    }


def _inventory_directory(source_dir: Path, relative_path: Path) -> dict[str, object]:
    path = source_dir / relative_path
    if not path.exists():
        return {
            "path": str(relative_path),
            "found": False,
            "file_count": 0,
            "sample_files": [],
        }
    files = sorted(item for item in path.rglob("*") if item.is_file())
    return {
        "path": str(relative_path),
        "found": True,
        "file_count": len(files),
        "sample_files": [str(item.relative_to(source_dir)) for item in files[:20]],
    }


def _inventory_zip(
    zip_path: Path, relative_path: Path, names: Iterable[str]
) -> dict[str, object]:
    prefix = relative_path.as_posix().rstrip("/") + "/"
    matches = sorted(
        name for name in names if prefix in name and not name.endswith("/")
    )
    return {
        "path": str(relative_path),
        "found": bool(matches),
        "file_count": len(matches),
        "sample_files": matches[:20],
    }


def inventory_inkscape_source(source: str | Path | None) -> dict[str, object]:
    """Inventory Inkscape defaults/fabric from a local source tree or zip."""

    if source is None:
        return {
            "source_type": "not_provided",
            "source_path": None,
            "standard_paths": {
                key: {
                    "path": str(path),
                    "found": False,
                    "file_count": 0,
                    "sample_files": [],
                }
                for key, path in INKSCAPE_STANDARD_PATHS.items()
            },
        }

    path = Path(source)
    if path.is_dir():
        return {
            "source_type": "directory",
            "source_path": str(path),
            "standard_paths": {
                key: _inventory_directory(path, rel_path)
                for key, rel_path in INKSCAPE_STANDARD_PATHS.items()
            },
        }
    if path.is_file() and zipfile.is_zipfile(path):
        names = _iter_zip_names(path)
        return {
            "source_type": "zip",
            "source_path": str(path),
            "standard_paths": {
                key: _inventory_zip(path, rel_path, names)
                for key, rel_path in INKSCAPE_STANDARD_PATHS.items()
            },
        }
    return {
        "source_type": "unavailable",
        "source_path": str(path),
        "standard_paths": {
            key: {
                "path": str(rel_path),
                "found": False,
                "file_count": 0,
                "sample_files": [],
            }
            for key, rel_path in INKSCAPE_STANDARD_PATHS.items()
        },
    }


def build_bridge_manifest(
    *,
    input_zip: str | Path | None = None,
    inkscape_source: str | Path | None = None,
    repo_url: str = DEFAULT_FORK_REPO_URL,
    destination_root: str | Path = Path("."),
) -> dict[str, object]:
    """Build a manifest linking Inkscape defaults and drawing inputs."""

    extraction = {
        "extracted": [],
        "missing": [
            asdict(MissingInput(name, str(path)))
            for name, path in EXPECTED_INPUTS.items()
        ],
    }
    if input_zip is not None:
        extraction = extract_expected_inputs_from_zip(input_zip, destination_root)

    root = Path(destination_root)
    expected_status = []
    for name, path in EXPECTED_INPUTS.items():
        target = root / path
        expected_status.append(
            {
                "name": name,
                "path": str(path),
                "found": target.exists(),
                "size_bytes": target.stat().st_size if target.exists() else None,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo_url": repo_url,
        "upstream_reference": DEFAULT_UPSTREAM_REPO_URL,
        "policy": SVG_SOURCE_POLICY,
        "input_zip": str(input_zip) if input_zip is not None else None,
        "input_extraction": extraction,
        "expected_inputs": expected_status,
        "inkscape_source_inventory": inventory_inkscape_source(inkscape_source),
        "notes": [
            "Do not vendor or switch into the Inkscape repository during parser execution.",
            "Use Inkscape defaults/fabric as an external reference while preserving project-specific drawing layers and analysis metadata.",
            "Parser execution consumes extracted SVG XML directly; PPTX files are inventoried but not parsed in this bridge step.",
        ],
    }


def write_bridge_manifest(
    manifest: dict[str, object],
    output_path: str | Path = DEFAULT_BRIDGE_MANIFEST,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bridge Inkscape zip/tree inputs into ABACUS P&ID parser inputs"
    )
    parser.add_argument(
        "--input-zip", type=Path, help="Zip containing the expected P&ID SVG/PPT inputs"
    )
    parser.add_argument(
        "--inkscape-source",
        type=Path,
        help="Local Inkscape source tree or source zip for defaults/fabric inventory",
    )
    parser.add_argument(
        "--repo-url",
        default=DEFAULT_FORK_REPO_URL,
        help="GBOGEB fork or upstream Inkscape repository URL reference",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_BRIDGE_MANIFEST)
    args = parser.parse_args(argv)

    manifest = build_bridge_manifest(
        input_zip=args.input_zip,
        inkscape_source=args.inkscape_source,
        repo_url=args.repo_url,
    )
    output = write_bridge_manifest(manifest, args.output)
    print(f"Wrote Inkscape bridge manifest: {output}")
    extracted = manifest["input_extraction"]["extracted"]  # type: ignore[index]
    if extracted:
        print("Extracted expected inputs:")
        for item in extracted:  # type: ignore[union-attr]
            print(f"- {item['output_path']} ({item['size_bytes']} bytes)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
