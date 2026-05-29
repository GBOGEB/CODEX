"""YAML/CSS slide-deck orchestration blocks for CODEX ⇄ ABACUS decks.

The module keeps content, presentation, and generated artifacts separated:
YAML carries governed deck data, CSS carries visual tokens, and this
orchestrator emits reviewable HTML, Pandoc-ready Markdown, and a manifest that
ABACUS can score for maturity/lineage.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

DEFAULT_OUTPUT_FORMATS: Sequence[str] = ("html", "md")
SUPPORTED_OUTPUT_FORMATS = frozenset({"html", "md", "markdown"})
BLOCK_KEYS: Sequence[str] = (
    "body",
    "objectives",
    "governance",
    "rtm_map",
    "checklist",
    "changes",
    "artifacts",
    "notes",
)
HEADING_TOKEN_OVERRIDES = {"rtm": "RTM", "iso": "ISO", "css": "CSS"}


@dataclass(frozen=True)
class DeckArtifact:
    """Single artifact emitted by the orchestration pipeline."""

    kind: str
    path: Path
    sha256: str


@dataclass(frozen=True)
class DeckBuildResult:
    """Structured result for generated review artifacts and ABACUS manifest."""

    deck_id: str
    output_dir: Path
    artifacts: tuple[DeckArtifact, ...]
    manifest_path: Path


def _run_git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            text=True,
            cwd=Path(__file__).parent,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _parse_vcs_timestamp(vcs_time: str) -> str:
    """Normalise a VCS ISO-8601 commit timestamp to a UTC isoformat string."""
    return (
        datetime.fromisoformat(vcs_time.replace("Z", "+00:00"))
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "deck"


def _sha256_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_deck_content(path: Path) -> dict[str, Any]:
    """Load and minimally validate a governed deck YAML source."""

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError("Deck YAML must contain a mapping at the document root")
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("Deck YAML must include a metadata mapping")
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("Deck YAML must include at least one slide")
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            raise ValueError(f"Slide {index} must be a mapping")
        if not slide.get("title"):
            raise ValueError(f"Slide {index} must include a title")
    return data


def load_css(path: Path) -> str:
    """Read a CSS template used for the HTML rendering path."""

    return path.read_text(encoding="utf-8")


def normalize_deck(data: Mapping[str, Any], deck_id: str | None = None) -> dict[str, Any]:
    """Attach deterministic ids and pipeline metadata to loaded deck content."""

    metadata = dict(data.get("metadata", {}))
    title = str(metadata.get("project") or metadata.get("title") or "Slide Deck")
    resolved_deck_id = deck_id or str(metadata.get("deck_id") or _slugify(title))
    metadata["deck_id"] = resolved_deck_id

    normalized_slides: list[dict[str, Any]] = []
    for index, raw_slide in enumerate(data.get("slides", []), start=1):
        slide = dict(raw_slide)
        section = str(slide.get("section") or "MAIN")
        slide.setdefault("id", f"{resolved_deck_id.upper().replace('-', '_')}_{index:03d}")
        slide["number"] = index
        slide["section"] = section
        normalized_slides.append(slide)

    return {
        "deck_id": resolved_deck_id,
        "metadata": metadata,
        "slides": normalized_slides,
        "source_hash": _sha256_text(json.dumps(data, sort_keys=True, default=str)),
    }


def _mapping_label_and_detail(item: Mapping[str, Any]) -> tuple[str, str]:
    label_key = next((key for key in ("gate", "id", "task", "name") if item.get(key)), None)
    label = str(item.get(label_key) if label_key else "Item")
    detail_parts = []
    for key, value in item.items():
        if key == label_key:
            continue
        detail_parts.append(f"{key}: {value}")
    return label, "; ".join(detail_parts)


def _render_sequence(items: Iterable[Any]) -> str:
    rendered = []
    for item in items:
        if isinstance(item, Mapping):
            label, detail = _mapping_label_and_detail(item)
            rendered.append(
                f"<li><strong>{html.escape(label)}</strong>"
                f"<span>{html.escape(detail)}</span></li>"
            )
        else:
            rendered.append(f"<li>{html.escape(str(item))}</li>")
    return f"<ul>{''.join(rendered)}</ul>" if rendered else ""


def _render_mapping_table(mapping: Mapping[str, Any]) -> str:
    rows = []
    for key, value in mapping.items():
        rows.append(
            "<tr>"
            f"<th>{html.escape(str(key))}</th>"
            f"<td>{html.escape(str(value))}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>" if rows else ""


def _format_block_heading(key: str) -> str:
    return " ".join(HEADING_TOKEN_OVERRIDES.get(token, token.title()) for token in key.split("_"))


def _manifest_artifact_path(artifact_path: Path, output_dir: Path) -> str:
    try:
        return artifact_path.relative_to(output_dir).as_posix()
    except ValueError as exc:  # pragma: no cover - defensive invariant check
        raise ValueError(f"Artifact path must be within output_dir: {artifact_path}") from exc


def _render_slide_blocks(slide: Mapping[str, Any]) -> str:
    blocks = []
    for key in BLOCK_KEYS:
        value = slide.get(key)
        if value in (None, ""):
            continue
        heading = _format_block_heading(key)
        if key == "body" and isinstance(value, list):
            blocks.append(_render_sequence(value))
        elif isinstance(value, list):
            css_class = "callout" if key in {"governance", "changes"} else "block"
            blocks.append(f"<div class=\"{css_class}\"><h3>{heading}</h3>{_render_sequence(value)}</div>")
        elif isinstance(value, Mapping):
            blocks.append(f"<div class=\"block\"><h3>{heading}</h3>{_render_mapping_table(value)}</div>")
        else:
            blocks.append(f"<p>{html.escape(str(value))}</p>")
    return "\n".join(blocks)


def render_html_deck(deck: Mapping[str, Any], css: str) -> str:
    """Render normalized deck content to standalone HTML review slides."""

    metadata = deck["metadata"]
    title = str(metadata.get("project") or metadata.get("title") or deck["deck_id"])
    status = str(metadata.get("status") or "draft")
    version = str(metadata.get("version") or "0.0")
    slide_sections = []
    for slide in deck["slides"]:
        slide_sections.append(
            f"<section class=\"slide\" id=\"{html.escape(str(slide['id']))}\">"
            f"<div class=\"bar\"><span>{html.escape(str(slide['section']))}</span>"
            f"<span>Slide {slide['number']}</span></div>"
            f"<h1>{html.escape(str(slide['title']))}</h1>"
            f"{_render_slide_blocks(slide)}"
            "</section>"
        )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>{html.escape(title)} — Deck {html.escape(version)}</title>
<style>
{css}
</style>
</head>
<body>
<header class=\"deck-cover\">
<p class=\"eyebrow\">{html.escape(status)}</p>
<h1>{html.escape(title)}</h1>
<p>Version {html.escape(version)} · Deck ID {html.escape(str(deck['deck_id']))}</p>
</header>
{''.join(slide_sections)}
</body>
</html>
"""


def _markdown_for_value(key: str, value: Any) -> list[str]:
    lines: list[str] = []
    if value in (None, ""):
        return lines
    if key != "body":
        lines.extend([f"### {_format_block_heading(key)}", ""])
    if isinstance(value, Mapping):
        lines.extend(["| Item | Detail |", "|---|---|"])
        for item_key, item_value in value.items():
            lines.append(f"| {item_key} | {item_value} |")
        lines.append("")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, Mapping):
                label, detail = _mapping_label_and_detail(item)
                lines.append(f"- **{label}**: {detail}")
            else:
                lines.append(f"- {item}")
        lines.append("")
    else:
        lines.extend([str(value), ""])
    return lines


def render_markdown_deck(deck: Mapping[str, Any]) -> str:
    """Render normalized deck content to Pandoc-ready Markdown."""

    metadata = deck["metadata"]
    title = str(metadata.get("project") or metadata.get("title") or deck["deck_id"])
    lines = [f"% {title}", f"% Version {metadata.get('version', '0.0')}", ""]
    for slide in deck["slides"]:
        lines.extend(["---", "", f"# {slide['title']}", "", f"_{slide['section']} · Slide {slide['number']}_", ""])
        for key in BLOCK_KEYS:
            lines.extend(_markdown_for_value(key, slide.get(key)))
    return "\n".join(lines).rstrip() + "\n"


def build_deck_assets(
    content_path: Path,
    css_path: Path,
    output_dir: Path,
    deck_id: str | None = None,
    formats: Iterable[str] = DEFAULT_OUTPUT_FORMATS,
    generated_at: str | None = None,
) -> DeckBuildResult:
    """Run the content→presentation→artifact pipeline for one deck.

    Timestamp precedence for manifest reproducibility:
    explicit ``generated_at`` value, then ``SOURCE_DATE_EPOCH``, then VCS
    commit time (``git show -s --format=%cI HEAD``), then ``"unknown"``.
    """

    data = load_deck_content(content_path)
    css = load_css(css_path)
    deck = normalize_deck(data, deck_id=deck_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = deck["deck_id"]

    artifacts: list[DeckArtifact] = []
    requested_formats = {str(item).lower() for item in formats}
    unsupported = sorted(requested_formats - SUPPORTED_OUTPUT_FORMATS)
    if unsupported:
        joined = ", ".join(unsupported)
        supported = ", ".join(sorted(SUPPORTED_OUTPUT_FORMATS))
        raise ValueError(f"Unsupported format(s): {joined}. Supported formats: {supported}")
    if "html" in requested_formats:
        html_body = render_html_deck(deck, css)
        html_path = output_dir / f"{stem}.html"
        html_path.write_text(html_body, encoding="utf-8")
        artifacts.append(DeckArtifact("html", html_path, _sha256_file(html_path)))
    if "md" in requested_formats or "markdown" in requested_formats:
        markdown_body = render_markdown_deck(deck)
        markdown_path = output_dir / f"{stem}.md"
        markdown_path.write_text(markdown_body, encoding="utf-8")
        artifacts.append(DeckArtifact("markdown", markdown_path, _sha256_file(markdown_path)))

    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if generated_at:
        generated_at_value = generated_at
    elif source_date_epoch:
        try:
            generated_at_epoch = int(source_date_epoch)
        except ValueError as exc:
            raise ValueError("SOURCE_DATE_EPOCH must be an integer Unix timestamp") from exc
        generated_at_value = datetime.fromtimestamp(generated_at_epoch, timezone.utc).isoformat()
    elif vcs_time := _run_git("show", "-s", "--format=%cI", "HEAD"):
        generated_at_value = _parse_vcs_timestamp(vcs_time)
    else:
        generated_at_value = "unknown"

    manifest = {
        "deck_id": deck["deck_id"],
        "pipeline": "yaml_css_to_html_markdown_v1",
        "generated_at": generated_at_value,
        "source": str(content_path),
        "style": str(css_path),
        "source_hash": deck["source_hash"],
        "slide_count": len(deck["slides"]),
        "abacus_controls": {
            "lineage_manifest": True,
            "fixed_and_locked_status": deck["metadata"].get("status") == "Fixed and Locked",
            "rtm_appendix_present": any("rtm_map" in slide for slide in deck["slides"]),
        },
        "artifacts": [
            {
                "kind": artifact.kind,
                "path": _manifest_artifact_path(artifact.path, output_dir),
                "sha256": artifact.sha256,
            }
            for artifact in artifacts
        ],
    }
    manifest_path = output_dir / f"{stem}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return DeckBuildResult(
        deck_id=deck["deck_id"],
        output_dir=output_dir,
        artifacts=tuple(artifacts),
        manifest_path=manifest_path,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build HTML/Markdown deck assets from YAML + CSS")
    parser.add_argument("--content", type=Path, required=True, help="Deck content YAML")
    parser.add_argument("--style", type=Path, required=True, help="Deck CSS template")
    parser.add_argument("--output-dir", type=Path, required=True, help="Generated artifact directory")
    parser.add_argument("--deck-id", type=str, help="Override generated deck id")
    parser.add_argument("--generated-at", type=str, help="Override generated_at value in manifest")
    parser.add_argument(
        "--format",
        nargs="+",
        default=list(DEFAULT_OUTPUT_FORMATS),
        choices=sorted(SUPPORTED_OUTPUT_FORMATS),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_deck_assets(
        content_path=args.content,
        css_path=args.style,
        output_dir=args.output_dir,
        deck_id=args.deck_id,
        formats=args.format,
        generated_at=args.generated_at,
    )
    print(f"Generated {len(result.artifacts)} artifacts for {result.deck_id}")
    print(result.manifest_path)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI passthrough
    raise SystemExit(main())
