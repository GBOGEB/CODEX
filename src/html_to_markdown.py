"""
html_to_markdown.py
───────────────────
Convert Confluence storage-format HTML to clean Markdown.

This Phase 0 implementation is dependency-light so read-only ingestion can run
inside restricted CI environments. It pre-processes Confluence namespace tags
into normal HTML-like structures and then performs a conservative stdlib-only
Markdown projection.
"""

from __future__ import annotations

import logging
import re
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────

def storage_html_to_markdown(html: str, base_url: str = "") -> str:
    """Convert Confluence storage HTML to a clean Markdown string."""
    if not html or not html.strip():
        return ""

    normalized = _expand_ac_links(html, base_url.rstrip("/"))
    normalized = _expand_ac_images(normalized, base_url.rstrip("/"))
    normalized = _expand_ac_macros(normalized)
    normalized = _strip_unknown_ac_tags(normalized)

    parser = _MarkdownHTMLParser()
    parser.feed(normalized)
    parser.close()
    return _post_process(parser.markdown())


# ──────────────────────────────────────────────────────────────────────
# Pre-processors
# ──────────────────────────────────────────────────────────────────────

def _expand_ac_links(html: str, base_url: str) -> str:
    """Replace common <ac:link> forms with standard Markdown links."""

    def repl(match: re.Match[str]) -> str:
        body = match.group(0)
        page = re.search(r"<ri:page\b([^>]*)/?>", body)
        url = re.search(r"<ri:url\b([^>]*)/?>", body)
        attachment = re.search(r"<ri:attachment\b([^>]*)/?>", body)
        text_match = re.search(r"<ac:(?:plain-text-link-body|link-body)[^>]*>(.*?)</ac:(?:plain-text-link-body|link-body)>", body, re.S)
        href = "#"
        link_text = ""
        if page:
            attrs = _attrs(page.group(1))
            title = attrs.get("ri:content-title", "")
            space = attrs.get("ri:space-key", "")
            href = f"{base_url}/wiki/spaces/{space}/pages/search?title={quote_plus(title)}" if base_url and title else title
            link_text = title
        elif url:
            attrs = _attrs(url.group(1))
            href = attrs.get("ri:value", "#")
            link_text = href
        elif attachment:
            attrs = _attrs(attachment.group(1))
            href = attrs.get("ri:filename", "#")
            link_text = href
        if text_match:
            link_text = _strip_tags(text_match.group(1)).strip() or link_text
        return f'<a href="{escape(href, quote=True)}">{escape(link_text or href)}</a>'

    return re.sub(r"<ac:link\b[^>]*>.*?</ac:link>", repl, html, flags=re.S)


def _expand_ac_images(html: str, base_url: str) -> str:
    """Replace common <ac:image> forms with standard <img> tags."""

    def repl(match: re.Match[str]) -> str:
        body = match.group(0)
        image_attrs = _attrs(match.group(1))
        attachment = re.search(r"<ri:attachment\b([^>]*)/?>", body)
        url = re.search(r"<ri:url\b([^>]*)/?>", body)
        src = ""
        alt = image_attrs.get("ac:alt", "")
        if attachment:
            attrs = _attrs(attachment.group(1))
            src = attrs.get("ri:filename", "attachment")
            alt = alt or src
        elif url:
            attrs = _attrs(url.group(1))
            src = attrs.get("ri:value", "")
            alt = alt or src
        return f'<img src="{escape(src, quote=True)}" alt="{escape(alt, quote=True)}" />'

    return re.sub(r"<ac:image\b([^>]*)>.*?</ac:image>", repl, html, flags=re.S)


def _expand_ac_macros(html: str) -> str:
    """Convert known <ac:structured-macro> types to simple HTML equivalents."""

    def repl(match: re.Match[str]) -> str:
        attrs = _attrs(match.group(1))
        name = attrs.get("ac:name", "unknown")
        body = match.group(2)
        plain_body = _macro_body(body, "plain-text-body")
        rich_body = _macro_body(body, "rich-text-body")
        if name == "code":
            language = _macro_parameter(body, "language")
            klass = f' class="{escape(language, quote=True)}"' if language else ""
            code = escape(unescape(_strip_tags(plain_body or rich_body)))
            return f"<pre><code{klass}>{code}</code></pre>"
        if name in {"info", "note", "warning", "tip"}:
            return f"<blockquote><strong>[{name.upper()}]</strong> {rich_body or plain_body}</blockquote>"
        if name in {"panel", "expand"}:
            title = _macro_parameter(body, "title") or name.title()
            return f"<div><strong>{escape(title)}</strong>{rich_body or plain_body}</div>"
        if name == "toc":
            return ""
        logger.debug("Unknown macro '%s' — wrapping as notice.", name)
        return f"<blockquote><em>[Confluence macro: {escape(name)}]</em>{rich_body or plain_body}</blockquote>"

    return re.sub(r"<ac:structured-macro\b([^>]*)>(.*?)</ac:structured-macro>", repl, html, flags=re.S)


def _strip_unknown_ac_tags(html: str) -> str:
    """Remove remaining ac:/ri: namespace wrappers while preserving content."""
    html = re.sub(r"</?(?:ac|ri):[^>]+>", "", html)
    return html


# ──────────────────────────────────────────────────────────────────────
# Post-processor
# ──────────────────────────────────────────────────────────────────────

def _post_process(md: str) -> str:
    """Clean up Markdown artefacts."""
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = "\n".join(line.rstrip() for line in md.splitlines())
    return md.strip()


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _attrs(raw: str) -> dict[str, str]:
    return {m.group(1): unescape(m.group(2) or m.group(3) or "") for m in re.finditer(r"([\w:-]+)=(?:\"([^\"]*)\"|'([^']*)')", raw)}


def _macro_body(body: str, body_name: str) -> str:
    match = re.search(rf"<ac:{body_name}\b[^>]*>(.*?)</ac:{body_name}>", body, re.S)
    return match.group(1) if match else ""


def _macro_parameter(body: str, name: str) -> str:
    pattern = rf"<ac:parameter\b[^>]*ac:name=['\"]{re.escape(name)}['\"][^>]*>(.*?)</ac:parameter>"
    match = re.search(pattern, body, re.S)
    return _strip_tags(match.group(1)).strip() if match else ""


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


class _MarkdownHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.link_stack: list[dict[str, str]] = []
        self.heading_level: int | None = None
        self.in_pre = False
        self.in_code = False
        self.table_rows: list[list[str]] = []
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None
        self.list_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k: v or "" for k, v in attrs_list}
        if re.fullmatch(r"h[1-6]", tag):
            self._block()
            self.heading_level = int(tag[1])
            self.parts.append("#" * self.heading_level + " ")
        elif tag == "p":
            self._block()
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "a":
            self.link_stack.append({"href": attrs.get("href", ""), "text": ""})
        elif tag == "img":
            self.parts.append(f"![{attrs.get('alt', '')}]({attrs.get('src', '')})")
        elif tag == "pre":
            self._block()
            self.in_pre = True
            self.parts.append("```\n")
        elif tag == "code":
            self.in_code = True
            if not self.in_pre:
                self.parts.append("`")
        elif tag == "blockquote":
            self._block()
            self.parts.append("> ")
        elif tag in {"ul", "ol"}:
            self.list_stack.append(tag)
            self._block()
        elif tag == "li":
            self.parts.append("- ")
        elif tag == "table":
            self._block()
            self.table_rows = []
        elif tag == "tr":
            self.current_row = []
        elif tag in {"td", "th"}:
            self.current_cell = []
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")

    def handle_endtag(self, tag: str) -> None:
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n\n")
            self.heading_level = None
        elif tag == "p":
            self.parts.append("\n\n")
        elif tag == "a" and self.link_stack:
            link = self.link_stack.pop()
            self.parts.append(f"[{link['text'].strip() or link['href']}]({link['href']})")
        elif tag == "pre":
            self.parts.append("\n```\n\n")
            self.in_pre = False
        elif tag == "code":
            if not self.in_pre:
                self.parts.append("`")
            self.in_code = False
        elif tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag in {"td", "th"} and self.current_cell is not None and self.current_row is not None:
            self.current_row.append(" ".join(self.current_cell).strip())
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if any(self.current_row):
                self.table_rows.append(self.current_row)
            self.current_row = None
        elif tag == "table":
            self.parts.append(_table_to_markdown(self.table_rows))
            self.table_rows = []

    def handle_data(self, data: str) -> None:
        if not data:
            return
        text = unescape(data)
        if self.link_stack:
            self.link_stack[-1]["text"] += text
        elif self.current_cell is not None:
            self.current_cell.append(text.strip())
        else:
            self.parts.append(text if self.in_pre else re.sub(r"\s+", " ", text))

    def markdown(self) -> str:
        return "".join(self.parts)

    def _block(self) -> None:
        current = "".join(self.parts)
        if current and not current.endswith("\n\n"):
            self.parts.append("\n\n")


def _table_to_markdown(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * width) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
    return "\n" + "\n".join(lines) + "\n\n"
