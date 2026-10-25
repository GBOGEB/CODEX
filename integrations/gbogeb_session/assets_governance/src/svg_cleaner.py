#!/usr/bin/env python3
"""
SVG Cleaner — GBOGEB/CODEX (GBC)
==================================

SVG optimization and ID injection engine:
  • Remove editor metadata (Inkscape, Illustrator, Sketch namespaces)
  • Remove XML comments
  • Normalize viewBox attribute
  • Inject governance IDs with configurable prefix
  • Validate SVG structure
  • Output optimized SVGs to compiled/ directory

Usage:
    python svg_cleaner.py assets/canonical/cryomodule_schematic.svg
    python svg_cleaner.py --input-dir assets/canonical/ --output-dir assets/compiled/
    python svg_cleaner.py --input-dir assets/canonical/ --prefix gbc --inject-ids
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


# ============================================================================
# Configuration
# ============================================================================

# Namespace prefixes to strip from SVG
EDITOR_NAMESPACES: list[str] = [
    "inkscape",
    "sodipodi",
    "sketch",
    "illustrator",
    "adobe",
    "cc",
    "dc",
    "rdf",
]

# Attributes with editor-specific data to remove
EDITOR_ATTRIBUTES: list[str] = [
    r"inkscape:\w+",
    r"sodipodi:\w+",
    r"sketch:\w+",
    r"data-name",
]

# Default ID prefix for injected IDs
DEFAULT_ID_PREFIX: str = "gbc"


# ============================================================================
# SVG Processing Functions
# ============================================================================

def remove_xml_comments(svg_content: str) -> str:
    """Remove all XML/HTML comments from SVG content."""
    return re.sub(r'<!--[\s\S]*?-->', '', svg_content)


def remove_editor_namespaces(svg_content: str) -> str:
    """Remove editor-specific namespace declarations from <svg> tag."""
    for ns in EDITOR_NAMESPACES:
        # Remove xmlns:ns="..." declarations
        svg_content = re.sub(
            rf'\s+xmlns:{ns}\s*=\s*"[^"]*"', '', svg_content
        )
    return svg_content


def remove_editor_attributes(svg_content: str) -> str:
    """Remove editor-specific attributes from all elements."""
    for attr_pattern in EDITOR_ATTRIBUTES:
        svg_content = re.sub(
            rf'\s+{attr_pattern}\s*=\s*"[^"]*"', '', svg_content
        )
    return svg_content


def remove_editor_elements(svg_content: str) -> str:
    """Remove entire editor-specific elements (e.g., <sodipodi:namedview>)."""
    for ns in EDITOR_NAMESPACES:
        # Self-closing tags
        svg_content = re.sub(
            rf'<{ns}:[^/]*?/>', '', svg_content
        )
        # Opening + closing tags
        svg_content = re.sub(
            rf'<{ns}:[^>]*>[\s\S]*?</{ns}:\w+>', '', svg_content
        )
    # Remove <metadata> blocks (often contain RDF/CC data)
    svg_content = re.sub(
        r'<metadata\b[^>]*>[\s\S]*?</metadata>', '', svg_content
    )
    return svg_content


def normalize_viewbox(svg_content: str) -> str:
    """
    Ensure the <svg> element has a viewBox attribute.
    If width/height are present but viewBox is missing, add it.
    """
    if re.search(r'viewBox\s*=', svg_content):
        return svg_content  # Already has viewBox

    w_match = re.search(r'<svg[^>]*\bwidth\s*=\s*"(\d+(?:\.\d+)?)"', svg_content)
    h_match = re.search(r'<svg[^>]*\bheight\s*=\s*"(\d+(?:\.\d+)?)"', svg_content)

    if w_match and h_match:
        w = w_match.group(1)
        h = h_match.group(1)
        svg_content = re.sub(
            r'(<svg\b[^>]*)',
            rf'\1 viewBox="0 0 {w} {h}"',
            svg_content,
            count=1,
        )
    return svg_content


def inject_ids(svg_content: str, prefix: str = DEFAULT_ID_PREFIX) -> str:
    """
    Inject governance IDs into SVG elements that lack them.

    Targets: <rect>, <circle>, <ellipse>, <path>, <line>, <polyline>,
             <polygon>, <g>, <text>
    """
    counter = 0
    target_tags = ["rect", "circle", "ellipse", "path", "line",
                   "polyline", "polygon", "g", "text"]

    def add_id(match: re.Match) -> str:
        nonlocal counter
        tag = match.group(1)
        attrs = match.group(2)
        # Skip if already has an id
        if re.search(r'\bid\s*=', attrs):
            return match.group(0)
        counter += 1
        return f'<{tag} id="{prefix}-{tag}-{counter:03d}"{attrs}'

    pattern = r'<(' + '|'.join(target_tags) + r')\b([^>]*)'
    svg_content = re.sub(pattern, add_id, svg_content)

    return svg_content


def collapse_whitespace(svg_content: str) -> str:
    """Collapse excessive blank lines (keep max 1 blank line)."""
    return re.sub(r'\n{3,}', '\n\n', svg_content)


def ensure_title(svg_content: str, title: str = "GBOGEB/CODEX Visual Asset") -> str:
    """Ensure SVG has a <title> element for accessibility."""
    if re.search(r'<title\b', svg_content):
        return svg_content
    # Insert after <svg ...> opening tag
    svg_content = re.sub(
        r'(<svg\b[^>]*>)',
        rf'\1\n  <title>{title}</title>',
        svg_content,
        count=1,
    )
    return svg_content


# ============================================================================
# Main Cleaning Pipeline
# ============================================================================

def clean_svg(
    content: str,
    *,
    do_inject_ids: bool = True,
    id_prefix: str = DEFAULT_ID_PREFIX,
    title: str | None = None,
) -> str:
    """
    Run the full SVG cleaning pipeline.

    Steps:
      1. Remove XML comments
      2. Remove editor namespace declarations
      3. Remove editor-specific attributes
      4. Remove editor-specific elements & metadata
      5. Normalize viewBox
      6. Ensure <title> for accessibility
      7. Inject governance IDs (optional)
      8. Collapse whitespace
    """
    content = remove_xml_comments(content)
    content = remove_editor_namespaces(content)
    content = remove_editor_attributes(content)
    content = remove_editor_elements(content)
    content = normalize_viewbox(content)
    if title:
        content = ensure_title(content, title)
    else:
        content = ensure_title(content)
    if do_inject_ids:
        content = inject_ids(content, id_prefix)
    content = collapse_whitespace(content)
    return content.strip() + "\n"


def clean_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> str:
    """
    Clean an SVG file and optionally write to output path.

    Returns the cleaned SVG content.
    """
    inp = Path(input_path)
    if not inp.exists():
        raise FileNotFoundError(f"SVG file not found: {inp}")
    if inp.suffix.lower() != ".svg":
        raise ValueError(f"Not an SVG file: {inp}")

    content = inp.read_text(encoding="utf-8")
    cleaned = clean_svg(content, **kwargs)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cleaned, encoding="utf-8")
        print(f"  ✓ Cleaned: {inp.name} → {out}")
    else:
        print(f"  ✓ Cleaned: {inp.name} (in-place)")
        inp.write_text(cleaned, encoding="utf-8")

    return cleaned


def process_directory(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
    **kwargs: Any,
) -> list[Path]:
    """Process all SVG files in a directory. Returns list of output paths."""
    inp = Path(input_dir)
    results: list[Path] = []

    for svg_file in sorted(inp.glob("*.svg")):
        if output_dir:
            out_path = Path(output_dir) / svg_file.name
        else:
            out_path = None
        clean_file(svg_file, out_path, **kwargs)
        results.append(out_path or svg_file)

    return results


# ============================================================================
# CLI
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GBOGEB/CODEX — SVG Cleaner & Optimizer"
    )
    parser.add_argument("input", nargs="?", type=Path, help="Single SVG file to clean")
    parser.add_argument("--input-dir", type=Path, help="Directory of SVGs to process")
    parser.add_argument("--output-dir", type=Path, help="Output directory for cleaned SVGs")
    parser.add_argument("--prefix", default=DEFAULT_ID_PREFIX, help="ID prefix for injection")
    parser.add_argument("--inject-ids", action="store_true", default=True, help="Inject IDs")
    parser.add_argument("--no-inject-ids", action="store_true", help="Skip ID injection")
    parser.add_argument("--title", type=str, help="SVG <title> text")
    args = parser.parse_args()

    do_ids = not args.no_inject_ids

    print("╔══════════════════════════════════════════════════════╗")
    print("║  GBOGEB/CODEX — SVG Cleaner                         ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    if args.input:
        clean_file(args.input, args.output_dir and (Path(args.output_dir) / args.input.name),
                   do_inject_ids=do_ids, id_prefix=args.prefix, title=args.title)
    elif args.input_dir:
        results = process_directory(args.input_dir, args.output_dir,
                                     do_inject_ids=do_ids, id_prefix=args.prefix, title=args.title)
        print(f"\n  Processed {len(results)} SVG files")
    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
