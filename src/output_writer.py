"""
output_writer.py
────────────────
Write extracted Confluence page data to structured local files.

Output layout per page:
    outputs/confluence/page_{id}/
        raw_storage.html     — verbatim Confluence storage HTML
        content.md           — converted Markdown
        metadata.yaml        — page metadata
        links.json           — internal + external links
        attachments.json     — attachment index
        hierarchy.json       — ancestors + children tree
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import yaml

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from html_to_markdown import storage_html_to_markdown

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Writer
# ──────────────────────────────────────────────────────────────────────

class OutputWriter:
    """
    Write all extracted page artefacts to disk.

    Parameters
    ──────────
    output_root : str | Path
        Root output directory.  Default: outputs/confluence
    base_url : str
        Confluence site root — used for link resolution.
    """

    def __init__(
        self,
        output_root: str | Path = "outputs/confluence",
        base_url: str = "",
    ) -> None:
        self.output_root = Path(output_root)
        self.base_url = base_url.rstrip("/")

    # ── Main entry point ───────────────────────────────────────────────

    def write_page(
        self,
        page_data: Dict[str, Any],
        attachments: Optional[List[Dict[str, Any]]] = None,
        children: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        """
        Write all artefacts for one Confluence page.

        Parameters
        ──────────
        page_data   : raw page dict from ConfluenceClient.get_page()
        attachments : list from ConfluenceClient.get_attachments()
        children    : list from ConfluenceClient.get_children()

        Returns
        ───────
        dict mapping artefact name → absolute file path
        """
        page_id = str(page_data["id"])
        page_dir = self.output_root / f"page_{page_id}"
        page_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Writing artefacts to %s", page_dir)

        written: Dict[str, str] = {}

        written["raw_storage_html"] = self._write_raw_html(page_data, page_dir)
        written["content_md"] = self._write_markdown(page_data, page_dir)
        written["metadata_yaml"] = self._write_metadata(page_data, page_dir)
        written["links_json"] = self._write_links(page_data, page_dir)
        written["attachments_json"] = self._write_attachments(
            page_id, attachments or [], page_dir
        )
        written["hierarchy_json"] = self._write_hierarchy(
            page_data, children or [], page_dir
        )

        logger.info(
            "Page %s — %d artefacts written to %s",
            page_id, len(written), page_dir,
        )
        return written

    # ── Individual writers ────────────────────────────────────────────

    def _write_raw_html(
        self,
        page_data: Dict[str, Any],
        page_dir: Path,
    ) -> str:
        html = self._storage_html(page_data)
        path = page_dir / "raw_storage.html"
        path.write_text(html, encoding="utf-8")
        logger.debug("raw_storage.html written (%d bytes)", len(html))
        return str(path.resolve())

    def _write_markdown(
        self,
        page_data: Dict[str, Any],
        page_dir: Path,
    ) -> str:
        html = self._storage_html(page_data)
        markdown = storage_html_to_markdown(html, base_url=self.base_url)
        if page_data.get("title") and not markdown.startswith("#"):
            markdown = f"# {page_data['title']}\n\n{markdown}".strip()
        path = page_dir / "content.md"
        path.write_text(markdown + "\n", encoding="utf-8")
        logger.debug("content.md written (%d chars)", len(markdown))
        return str(path.resolve())

    def _write_metadata(
        self,
        page_data: Dict[str, Any],
        page_dir: Path,
    ) -> str:
        html = self._storage_html(page_data)
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "confluence_read_only",
            "id": str(page_data.get("id", "")),
            "type": page_data.get("type"),
            "title": page_data.get("title"),
            "space": page_data.get("space", {}).get("key"),
            "version": page_data.get("version", {}).get("number"),
            "status": page_data.get("status"),
            "webui": page_data.get("_links", {}).get("webui"),
            "counts": {
                "headings": len(re.findall(r"<h[1-6]\b", html, flags=re.I)),
                "tables": len(re.findall(r"<table\b", html, flags=re.I)),
                "links": len(self._extract_links(page_data)),
                "attachments": len(re.findall(r"<ri:attachment\b", html, flags=re.I)),
                "images": len(re.findall(r"<(?:img|ac:image)\b", html, flags=re.I)),
                "macros": len(re.findall(r"<ac:structured-macro\b", html, flags=re.I)),
                "ancestors": len(page_data.get("ancestors", [])),
            },
            "labels": self._labels_from_page(page_data),
        }
        path = page_dir / "metadata.yaml"
        path.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
        return str(path.resolve())

    def _write_links(
        self,
        page_data: Dict[str, Any],
        page_dir: Path,
    ) -> str:
        payload = {
            "page_id": str(page_data.get("id", "")),
            "links": self._extract_links(page_data),
        }
        path = page_dir / "links.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path.resolve())

    def _write_attachments(
        self,
        page_id: str,
        attachments: List[Dict[str, Any]],
        page_dir: Path,
    ) -> str:
        normalized = []
        for attachment in attachments:
            links = attachment.get("_links", {})
            download = links.get("download")
            normalized.append(
                {
                    "id": attachment.get("id"),
                    "title": attachment.get("title"),
                    "media_type": attachment.get("metadata", {}).get("mediaType"),
                    "file_size": attachment.get("extensions", {}).get("fileSize"),
                    "download_link": download,
                    "absolute_download_url": f"{self.base_url}{download}" if self.base_url and download else download,
                }
            )
        payload = {"page_id": page_id, "attachments": normalized}
        path = page_dir / "attachments.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path.resolve())

    def _write_hierarchy(
        self,
        page_data: Dict[str, Any],
        children: List[Dict[str, Any]],
        page_dir: Path,
    ) -> str:
        payload = {
            "page_id": str(page_data.get("id", "")),
            "ancestors": [self._page_ref(item) for item in page_data.get("ancestors", [])],
            "children": [self._page_ref(item) for item in children],
        }
        path = page_dir / "hierarchy.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path.resolve())

    # ── Extractors ────────────────────────────────────────────────────

    def _extract_links(self, page_data: Dict[str, Any]) -> List[Dict[str, str]]:
        html = self._storage_html(page_data)
        links: List[Dict[str, str]] = []

        for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, flags=re.I | re.S):
            attrs = self._attrs(match.group(1))
            href = attrs.get("href", "")
            if not href:
                continue
            text = self._strip_tags(match.group(2)).strip() or href
            links.append({"type": self._link_type(href), "text": text, "href": href})

        for match in re.finditer(r"<ac:link\b[^>]*>(.*?)</ac:link>", html, flags=re.I | re.S):
            body = match.group(1)
            body_text = self._extract_link_body(body)
            page_match = re.search(r"<ri:page\b([^>]*)/?>", body, flags=re.I)
            url_match = re.search(r"<ri:url\b([^>]*)/?>", body, flags=re.I)
            attachment_match = re.search(r"<ri:attachment\b([^>]*)/?>", body, flags=re.I)
            if page_match:
                attrs = self._attrs(page_match.group(1))
                title = attrs.get("ri:content-title", "")
                space = attrs.get("ri:space-key", "")
                href = f"{self.base_url}/wiki/spaces/{space}/pages/search?title={title.replace(' ', '+')}" if self.base_url and title else title
                links.append({"type": "confluence_page", "text": body_text or title, "href": href})
            elif url_match:
                attrs = self._attrs(url_match.group(1))
                href = attrs.get("ri:value", "")
                links.append({"type": self._link_type(href), "text": body_text or href, "href": href})
            elif attachment_match:
                attrs = self._attrs(attachment_match.group(1))
                filename = attrs.get("ri:filename", "")
                links.append({"type": "attachment", "text": body_text or filename, "href": filename})

        for match in re.finditer(r"<ri:attachment\b([^>]*)/?>", html, flags=re.I):
            filename = self._attrs(match.group(1)).get("ri:filename", "")
            if filename and not any(link["type"] == "attachment" and link["href"] == filename for link in links):
                links.append({"type": "attachment", "text": filename, "href": filename})

        return links


    @staticmethod
    def _attrs(raw: str) -> Dict[str, str]:
        return {m.group(1): m.group(2) or m.group(3) or "" for m in re.finditer(r"([\w:-]+)=(?:\"([^\"]*)\"|'([^']*)')", raw)}

    @staticmethod
    def _strip_tags(value: str) -> str:
        return re.sub(r"<[^>]+>", "", value)

    @classmethod
    def _extract_link_body(cls, body: str) -> str:
        match = re.search(r"<ac:(?:plain-text-link-body|link-body)\b[^>]*>(.*?)</ac:(?:plain-text-link-body|link-body)>", body, flags=re.I | re.S)
        return cls._strip_tags(match.group(1)).strip() if match else ""

    @staticmethod
    def _storage_html(page_data: Dict[str, Any]) -> str:
        return page_data.get("body", {}).get("storage", {}).get("value", "")

    @staticmethod
    def _labels_from_page(page_data: Dict[str, Any]) -> List[str]:
        labels = page_data.get("metadata", {}).get("labels", {}).get("results", [])
        return [label.get("name", "") for label in labels if label.get("name")]

    @staticmethod
    def _page_ref(page: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(page.get("id", "")),
            "title": page.get("title"),
            "type": page.get("type"),
            "status": page.get("status"),
            "webui": page.get("_links", {}).get("webui"),
        }

    @staticmethod
    def _link_type(href: str) -> str:
        parsed = urlparse(href)
        if not parsed.scheme and not href.startswith("/"):
            return "relative"
        if parsed.scheme in {"http", "https"}:
            return "external"
        return "internal"
