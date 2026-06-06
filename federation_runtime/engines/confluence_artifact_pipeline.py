#!/usr/bin/env python3
"""Confluence target-page reader and GitHub artifact generator.

This module implements CD_Item1 for the Phase 0 federation bridge. It can read a
single Confluence page from the REST API when credentials are supplied, or from a
local storage-format HTML fixture for deterministic CI/smoke execution.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from confluence_client import ConfluenceClient
from html_to_markdown import storage_html_to_markdown

TARGET_PAGE_ID = "1023934467"
TARGET_SPACE = "ACR"
TARGET_TITLE = "DSBT Task 3 - Technical Support"


@dataclass
class PageArtifacts:
    page_id: str
    title: str
    space: str
    raw_storage_html: str
    source_status: str
    metadata: dict[str, Any]
    attachments: list[dict[str, Any]] = field(default_factory=list)


class ConfluenceStorageParser(HTMLParser):
    """Conservative Confluence storage-format parser using only stdlib HTMLParser."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[dict[str, Any]] = []
        self.links: list[dict[str, Any]] = []
        self.tables: list[dict[str, Any]] = []
        self.macros: list[dict[str, Any]] = []
        self.images: list[dict[str, Any]] = []
        self.expandable_sections: list[dict[str, Any]] = []
        self._tag_stack: list[str] = []
        self._current_heading: dict[str, Any] | None = None
        self._current_link: dict[str, Any] | None = None
        self._current_table: dict[str, Any] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None
        self._macro_stack: list[dict[str, Any]] = []
        self._text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        self._tag_stack.append(tag)
        if re.fullmatch(r"h[1-6]", tag):
            self._current_heading = {"level": int(tag[1]), "text": "", "anchor": attrs_dict.get("id")}
        elif tag == "a":
            self._current_link = {"href": attrs_dict.get("href", ""), "text": "", "type": "external"}
        elif tag == "table":
            self._current_table = {"rows": []}
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []
        elif tag in {"ac:structured-macro", "ri:attachment", "ri:url", "ri:page", "ac:image"}:
            self._handle_confluence_tag(tag, attrs_dict)
        elif tag == "img":
            self.images.append({"src": attrs_dict.get("src", ""), "alt": attrs_dict.get("alt", "")})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._current_heading and re.fullmatch(r"h[1-6]", tag):
            self._current_heading["text"] = self._current_heading["text"].strip()
            self.headings.append(self._current_heading)
            self._text_chunks.append("#" * self._current_heading["level"] + " " + self._current_heading["text"] + "\n")
            self._current_heading = None
        elif tag == "a" and self._current_link:
            self._current_link["text"] = self._current_link["text"].strip()
            if self._current_link["href"]:
                self.links.append(self._current_link)
            self._current_link = None
        elif tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append(" ".join(self._current_cell).strip())
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None and self._current_table is not None:
            if any(cell for cell in self._current_row):
                self._current_table["rows"].append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._current_table is not None:
            self.tables.append(self._current_table)
            self._text_chunks.append(self._table_to_markdown(self._current_table))
            self._current_table = None
        elif tag == "ac:structured-macro" and self._macro_stack:
            macro = self._macro_stack.pop()
            self.macros.append(macro)
            if macro.get("name") == "expand":
                self.expandable_sections.append(dict(macro))
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        text = unescape(data).strip()
        if not text:
            return
        if self._current_heading is not None:
            self._current_heading["text"] += text + " "
        if self._current_link is not None:
            self._current_link["text"] += text + " "
        if self._current_cell is not None:
            self._current_cell.append(text)
        elif not self._current_heading:
            self._text_chunks.append(text + "\n")

    def _handle_confluence_tag(self, tag: str, attrs: dict[str, str]) -> None:
        if tag == "ac:structured-macro":
            self._macro_stack.append({"name": attrs.get("ac:name", ""), "schema_version": attrs.get("ac:schema-version", "")})
        elif tag == "ri:attachment":
            filename = attrs.get("ri:filename", "")
            self.links.append({"href": filename, "text": filename, "type": "attachment"})
        elif tag == "ri:url":
            href = attrs.get("ri:value", "")
            self.links.append({"href": href, "text": href, "type": "external"})
        elif tag == "ri:page":
            title = attrs.get("ri:content-title", "")
            self.links.append({"href": title, "text": title, "type": "confluence_page"})
        elif tag == "ac:image":
            self.images.append({"src": "confluence-storage-image", "alt": attrs.get("ac:alt", "")})

    @staticmethod
    def _table_to_markdown(table: dict[str, Any]) -> str:
        rows = table.get("rows", [])
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        normalized = [row + [""] * (width - len(row)) for row in rows]
        header = normalized[0]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * width) + " |"]
        lines.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
        return "\n".join(lines) + "\n"

    def markdown(self, title: str) -> str:
        chunks = [f"# {title}\n", *self._text_chunks]
        return "\n".join(chunk.rstrip() for chunk in chunks if chunk.strip()) + "\n"


def fetch_confluence_page(page_id: str) -> PageArtifacts:
    client = ConfluenceClient.from_environment()
    page = client.get_page(page_id)
    attachments = [
        {
            "id": item.get("id"),
            "title": item.get("title"),
            "media_type": item.get("metadata", {}).get("mediaType"),
            "download_link": item.get("_links", {}).get("download"),
        }
        for item in client.get_attachments(page_id)
    ]
    return PageArtifacts(
        page_id=page_id,
        title=page.get("title", TARGET_TITLE),
        space=page.get("space", {}).get("key", TARGET_SPACE),
        raw_storage_html=page.get("body", {}).get("storage", {}).get("value", ""),
        source_status="live_confluence_read",
        attachments=attachments,
        metadata={
            "page_id": page_id,
            "title": page.get("title", TARGET_TITLE),
            "space": page.get("space", {}).get("key", TARGET_SPACE),
            "version": page.get("version", {}).get("number"),
            "ancestors": [{"id": item.get("id"), "title": item.get("title")} for item in page.get("ancestors", [])],
            "children": [{"id": item.get("id"), "title": item.get("title")} for item in page.get("children", {}).get("page", {}).get("results", [])],
            "source_url": f"{client.base_url}/wiki/spaces/{TARGET_SPACE}/pages/{page_id}",
        },
    )


def fixture_artifacts(page_id: str, fixture: Path | None = None) -> PageArtifacts:
    html = fixture.read_text(encoding="utf-8") if fixture else """
<h1>DSBT Task 3 - Technical Support</h1>
<p>Phase 0 deterministic fixture for federation bridge smoke execution.</p>
<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">Support scope</ac:parameter><ac:rich-text-body><p>Expandable technical-support notes.</p></ac:rich-text-body></ac:structured-macro>
<h2>Inputs</h2>
<table><tr><th>Source</th><th>Trace</th></tr><tr><td>Confluence ACR</td><td>1023934467</td></tr></table>
<p><a href="https://github.com/example/codex/issues/1">GitHub task seed</a></p>
<ri:attachment ri:filename="support-context.pdf" />
"""
    return PageArtifacts(
        page_id=page_id,
        title=TARGET_TITLE,
        space=TARGET_SPACE,
        raw_storage_html=html,
        source_status="offline_fixture",
        attachments=[{"id": "fixture-attachment-1", "title": "support-context.pdf", "media_type": "application/pdf", "download_link": None}],
        metadata={
            "page_id": page_id,
            "title": TARGET_TITLE,
            "space": TARGET_SPACE,
            "version": None,
            "ancestors": [],
            "children": [],
            "source_url": None,
        },
    )


def write_artifacts(page: PageArtifacts, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    parser = ConfluenceStorageParser()
    parser.feed(page.raw_storage_html)
    metadata = {
        **page.metadata,
        "source_status": page.source_status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parser_capabilities": ["headings", "expandable_sections", "tables", "links", "attachments", "images", "confluence_macros", "page_hierarchy"],
        "structure_counts": {
            "headings": len(parser.headings),
            "expandable_sections": len(parser.expandable_sections),
            "tables": len(parser.tables),
            "links": len(parser.links),
            "attachments": len(page.attachments),
            "images": len(parser.images),
            "macros": len(parser.macros),
            "ancestors": len(page.metadata.get("ancestors", [])),
            "children": len(page.metadata.get("children", [])),
        },
        "headings": parser.headings,
        "tables": parser.tables,
        "macros": parser.macros,
        "expandable_sections": parser.expandable_sections,
        "images": parser.images,
    }
    links = {"page_id": page.page_id, "links": parser.links}
    attachments = {"page_id": page.page_id, "attachments": page.attachments}
    hierarchy = {
        "page_id": page.page_id,
        "ancestors": page.metadata.get("ancestors", []),
        "children": page.metadata.get("children", []),
    }

    (output_dir / "raw_storage.html").write_text(page.raw_storage_html, encoding="utf-8")
    (output_dir / "content.md").write_text(storage_html_to_markdown(page.raw_storage_html) + "\n", encoding="utf-8")
    (output_dir / "metadata.yaml").write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
    (output_dir / "links.json").write_text(json.dumps(links, indent=2), encoding="utf-8")
    (output_dir / "attachments.json").write_text(json.dumps(attachments, indent=2), encoding="utf-8")
    (output_dir / "hierarchy.json").write_text(json.dumps(hierarchy, indent=2), encoding="utf-8")
    return metadata


def main(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser(description="Generate GitHub artifacts from a targeted Confluence page")
    argp.add_argument("--page-id", default=TARGET_PAGE_ID)
    argp.add_argument("--output-dir", type=Path, default=Path("outputs") / "confluence" / f"page_{TARGET_PAGE_ID}")
    argp.add_argument("--fixture", type=Path, help="Use a local Confluence storage-format HTML fixture")
    argp.add_argument("--live", action="store_true", help="Require a live Confluence REST API read")
    args = argp.parse_args(argv)

    try:
        page = fetch_confluence_page(args.page_id) if args.live else fixture_artifacts(args.page_id, args.fixture)
        metadata = write_artifacts(page, args.output_dir)
    except Exception as exc:
        print(f"confluence artifact generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"wrote Confluence artifacts for page {args.page_id} to {args.output_dir} ({metadata['source_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
