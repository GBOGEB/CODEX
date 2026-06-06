#!/usr/bin/env python3
"""QPLANT locked contractual baseline ingestion for Phase 0 CD_Item2."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SOURCES = [Path("Book_Master.md"), Path("VCR_Requirements.md"), Path("VCR_Summary.md")]
REQ_PATTERN = re.compile(r"^\s*(?P<number>\d{1,4})\.\s+(?P<text>.+)")
SHALL_PATTERN = re.compile(r"\b(shall|must|required|contractor shall|system shall)\b", re.IGNORECASE)


@dataclass
class SourceRecord:
    path: Path
    sha256: str
    size_bytes: int
    requirement_count: int


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_requirements(path: Path) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    if not path.exists():
        return requirements
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line_number, line in enumerate(lines, start=1):
        match = REQ_PATTERN.match(line)
        if not match or not SHALL_PATTERN.search(match.group("text")):
            continue
        req_id = f"QPLANT-{path.stem.upper()}-{match.group('number').zfill(4)}"
        requirements.append(
            {
                "id": req_id,
                "source_path": str(path),
                "source_line": line_number,
                "source_requirement_number": match.group("number"),
                "statement": match.group("text").strip(),
                "trace_marker": f"{path}:{line_number}",
                "baseline_lock": "locked_source_not_reinterpreted",
            }
        )
    return requirements


def render_rtm(requirements: list[dict[str, Any]]) -> str:
    lines = [
        "# QPLANT Contractual Baseline Requirements Traceability Matrix",
        "",
        "This RTM is generated from locked source material. Requirement text is traced to source lines and is not reinterpreted.",
        "",
        "| Requirement ID | Source | Line | Requirement Number | Trace Marker | Baseline State |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for req in requirements:
        lines.append(
            "| {id} | {source_path} | {source_line} | {source_requirement_number} | `{trace_marker}` | {baseline_lock} |".format(**req)
        )
    lines.append("")
    return "\n".join(lines)


def ingest(sources: list[Path], docs_baseline: Path, docs_rtm: Path, output_dir: Path) -> dict[str, Any]:
    docs_baseline.mkdir(parents=True, exist_ok=True)
    docs_rtm.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    source_records: list[SourceRecord] = []
    requirements: list[dict[str, Any]] = []
    missing_sources: list[str] = []

    for source in sources:
        if not source.exists():
            missing_sources.append(str(source))
            continue
        extracted = extract_requirements(source)
        requirements.extend(extracted)
        source_records.append(SourceRecord(source, sha256(source), source.stat().st_size, len(extracted)))

    manifest = {
        "phase": "Phase 0",
        "cd_item": "CD_Item2",
        "generated_at": generated_at,
        "principle": "Federation, not duplication",
        "constraints": [
            "Do not overwrite locked baseline requirements",
            "Do not reinterpret contractual obligations without trace markers",
            "Preserve source references",
            "Emit change deltas separately",
        ],
        "sources": [record.__dict__ | {"path": str(record.path)} for record in source_records],
        "missing_sources": missing_sources,
        "outputs": {
            "baseline_manifest": str(docs_baseline / "contractual_baseline_manifest.yaml"),
            "requirements_json": str(output_dir / "requirements.json"),
            "rtm_markdown": str(docs_rtm / "requirements_traceability_matrix.md"),
            "change_deltas": str(output_dir / "change_deltas.yaml"),
        },
        "requirement_count": len(requirements),
    }
    deltas = {
        "generated_at": generated_at,
        "delta_policy": "separate_emit_only_no_locked_source_overwrite",
        "deltas": [],
        "notes": ["Initial Phase 0 baseline capture; future contractual changes must be added here before derived RTM updates."],
    }

    (docs_baseline / "README.md").write_text(
        "# QPLANT Contractual Baseline\n\nGenerated manifests in this directory preserve locked-source traceability. Source requirements remain immutable; derived artifacts are controlled separately.\n",
        encoding="utf-8",
    )
    (docs_baseline / "contractual_baseline_manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (docs_rtm / "requirements_traceability_matrix.md").write_text(render_rtm(requirements), encoding="utf-8")
    (output_dir / "requirements.json").write_text(json.dumps({"generated_at": generated_at, "requirements": requirements}, indent=2), encoding="utf-8")
    (output_dir / "change_deltas.yaml").write_text(yaml.safe_dump(deltas, sort_keys=False), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest QPLANT locked contractual baseline into traceable GitHub artifacts")
    parser.add_argument("--source", action="append", type=Path, dest="sources", help="Baseline source file; may be supplied multiple times")
    parser.add_argument("--docs-baseline", type=Path, default=Path("docs/qplant/baseline"))
    parser.add_argument("--docs-rtm", type=Path, default=Path("docs/qplant/rtm"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/qplant/contractual_ingestion"))
    args = parser.parse_args(argv)
    manifest = ingest(args.sources or DEFAULT_SOURCES, args.docs_baseline, args.docs_rtm, args.output_dir)
    print(f"ingested {manifest['requirement_count']} QPLANT baseline requirements from {len(manifest['sources'])} source(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
