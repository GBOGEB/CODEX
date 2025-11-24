"""PPT engine helpers for CODEX slide production.

This module focuses on predictable, multi-format rendering of slide decks with
clear integration points for the DOW pipeline (orchestration), KEB conversion
helpers (Pandoc wrappers), and GBOGEB governance checks. It favors explicit
metadata propagation so that PPTX, HTML, and PDF outputs remain aligned and
traceable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence


DEFAULT_FORMATS: Sequence[str] = ("pptx", "pdf", "html")
LAYOUT_ALIASES: Mapping[str, str] = {
    "statement": "Statement",
    "appendix": "Appendix",
    "comparison": "ComparisonGrid",
}
THEME_COLORS: Mapping[str, str] = {
    "primary": "#003865",
    "accent": "#5CBFEB",
    "success": "#2D936C",
    "warning": "#FF8C42",
}


@dataclass
class TemplateSettings:
    """Declarative description of the template and governance requirements."""

    template_path: Path
    theme_colors: Mapping[str, str] = field(default_factory=lambda: THEME_COLORS)
    strict_links: bool = True
    partner_logo: Path | None = None
    base_url: str | None = None


@dataclass
class BuildResult:
    """Structured outcome from a build invocation."""

    source: Path
    output_dir: Path
    formats: List[str]
    metadata_path: Path


class PandocNotAvailable(RuntimeError):
    """Raised when Pandoc is required but cannot be located."""


def sha256_file(path: Path) -> str:
    """Return the SHA256 checksum for a file, streaming in chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_template_metadata(settings: TemplateSettings) -> MutableMapping[str, str]:
    """Return minimal metadata about the active template.

    The metadata is embedded into the deck to make it easy for GBOGEB to
    validate provenance and to help reviewers understand which version of the
    template produced an artefact.
    """

    metadata: MutableMapping[str, str] = {
        "template_path": str(settings.template_path),
        "strict_links": str(settings.strict_links),
        "theme_colors": json.dumps(dict(settings.theme_colors)),
    }

    if settings.template_path.exists():
        metadata["template_checksum"] = sha256_file(settings.template_path)
    if settings.partner_logo:
        metadata["partner_logo"] = str(settings.partner_logo)
    if settings.base_url:
        metadata["base_url"] = settings.base_url

    return metadata


def ensure_pandoc_available(pandoc_cmd: str) -> None:
    """Validate that Pandoc is on PATH unless conversions are stubbed."""

    try:
        subprocess.run([pandoc_cmd, "--version"], check=True, capture_output=True)
    except FileNotFoundError as exc:  # pragma: no cover - environment dependent
        raise PandocNotAvailable("Pandoc is required for PPT builds but is missing") from exc


def convert_markdown_bundle(
    source_path: Path,
    output_dir: Path,
    formats: Iterable[str] = DEFAULT_FORMATS,
    pandoc_cmd: str = "pandoc",
    dry_run: bool = False,
) -> List[Path]:
    """Convert a Markdown source into PPTX, PDF, and HTML using Pandoc/KEB.

    The function gracefully falls back to writing placeholder artefacts when the
    environment lacks Pandoc so that local development and CI dry runs remain
    deterministic.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    outputs: List[Path] = []
    resolved_formats = list(dict.fromkeys(formats))  # remove duplicates while preserving order

    if not dry_run:
        ensure_pandoc_available(pandoc_cmd)

    for fmt in resolved_formats:
        target = output_dir / f"{source_path.stem}.{fmt}"

        if dry_run:
            target.write_text(
                f"Placeholder {fmt.upper()} for {source_path.name} generated in dry-run mode.\n",
                encoding="utf-8",
            )
        else:
            args = [
                pandoc_cmd,
                str(source_path),
                "--from",
                "markdown",
                "--to",
                fmt,
                "--output",
                str(target),
            ]
            subprocess.run(args, check=True, capture_output=True)

        outputs.append(target)

    return outputs


def validate_deck_metadata(metadata: Mapping[str, str]) -> Dict[str, Dict[str, str]]:
    """Return a governance report expected by the GBOGEB checks.

    The function ensures required fields are present and marks any missing
    entries so pipeline consumers can fail fast with actionable messages.
    """

    required_fields = ("author", "revision", "sensitivity", "template_checksum")
    report: Dict[str, Dict[str, str]] = {"missing": {}, "present": {}}

    for key in required_fields:
        value = metadata.get(key)
        if value:
            report["present"][key] = str(value)
        else:
            report["missing"][key] = "required"

    return report


def build_deck(
    source: Path,
    output_dir: Path,
    settings: TemplateSettings,
    formats: Iterable[str] = DEFAULT_FORMATS,
    pandoc_cmd: str = "pandoc",
    dry_run: bool = False,
    metadata_overrides: Mapping[str, str] | None = None,
) -> BuildResult:
    """Render a deck from Markdown to multi-format outputs with governance metadata."""

    outputs = convert_markdown_bundle(
        source_path=source,
        output_dir=output_dir,
        formats=formats,
        pandoc_cmd=pandoc_cmd,
        dry_run=dry_run,
    )

    metadata: Dict[str, str] = {
        "author": os.getenv("DECK_AUTHOR", "unknown"),
        "revision": os.getenv("DECK_REVISION", "v0.0"),
        "sensitivity": os.getenv("DECK_SENSITIVITY", "internal"),
        "source": str(source),
        "outputs": json.dumps([str(path) for path in outputs]),
    }
    metadata.update(load_template_metadata(settings))
    if metadata_overrides:
        metadata.update(metadata_overrides)

    report = validate_deck_metadata(metadata)
    metadata["governance_report"] = json.dumps(report)

    metadata_path = output_dir / f"{source.stem}.metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return BuildResult(
        source=source,
        output_dir=output_dir,
        formats=list(formats),
        metadata_path=metadata_path,
    )


def batch_build(
    manifest_dir: Path,
    output_dir: Path,
    settings: TemplateSettings,
    formats: Iterable[str] = DEFAULT_FORMATS,
    pandoc_cmd: str = "pandoc",
    dry_run: bool = False,
) -> List[BuildResult]:
    """Process every Markdown source within a manifest directory."""

    results: List[BuildResult] = []
    for source in sorted(manifest_dir.glob("*.md")):
        results.append(
            build_deck(
                source=source,
                output_dir=output_dir,
                settings=settings,
                formats=formats,
                pandoc_cmd=pandoc_cmd,
                dry_run=dry_run,
            )
        )
    return results


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for building decks or running batches."""

    parser = argparse.ArgumentParser(description="Build PPTX/PDF/HTML decks from Markdown sources")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--template", type=Path, default=Path("slides/assets/base_template.pptx"))
        subparser.add_argument("--partner-logo", type=Path)
        subparser.add_argument("--base-url", type=str)
        subparser.add_argument("--format", nargs="+", default=list(DEFAULT_FORMATS))
        subparser.add_argument("--pandoc", default="pandoc")
        subparser.add_argument("--dry-run", action="store_true")
        subparser.add_argument("--strict-links", action="store_true", default=True)

    build_parser = subparsers.add_parser("build", help="Build a single deck")
    add_common_options(build_parser)
    build_parser.add_argument("--source", type=Path, required=True)
    build_parser.add_argument("--output-dir", type=Path, required=True)

    batch_parser = subparsers.add_parser("batch", help="Build all decks in a directory")
    add_common_options(batch_parser)
    batch_parser.add_argument("--manifest-dir", type=Path, required=True)
    batch_parser.add_argument("--output-dir", type=Path, required=True)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the PPT engine CLI."""

    args = parse_args(argv)
    settings = TemplateSettings(
        template_path=args.template,
        strict_links=args.strict_links,
        partner_logo=getattr(args, "partner_logo", None),
        base_url=getattr(args, "base_url", None),
    )

    if args.command == "build":
        build_deck(
            source=args.source,
            output_dir=args.output_dir,
            settings=settings,
            formats=args.format,
            pandoc_cmd=args.pandoc,
            dry_run=args.dry_run,
        )
    elif args.command == "batch":
        batch_build(
            manifest_dir=args.manifest_dir,
            output_dir=args.output_dir,
            settings=settings,
            formats=args.format,
            pandoc_cmd=args.pandoc,
            dry_run=args.dry_run,
        )

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI passthrough
    raise SystemExit(main())
