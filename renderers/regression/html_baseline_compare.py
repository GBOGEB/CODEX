from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


IGNORED_TEXT_TAGS = {"script", "style", "noscript"}


@dataclass
class RegressionResult:
    baseline: str
    candidate: str
    identical: bool
    notes: str
    semantic_identical: bool = False
    baseline_signature: dict[str, Any] | None = None
    candidate_signature: dict[str, Any] | None = None
    deltas: dict[str, Any] | None = None


class _SemanticHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tag_counts: dict[str, int] = {}
        self.links: list[str] = []
        self.headings: list[str] = []
        self.text_chunks: list[str] = []
        self.color_tokens: list[str] = []
        self._tag_stack: list[str] = []
        self._current_heading: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._tag_stack.append(tag)
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        attr_map = {name.lower(): value or "" for name, value in attrs}

        for attr in ("href", "src"):
            if attr in attr_map:
                self.links.append(attr_map[attr].split("#", 1)[0].strip())

        style = attr_map.get("style", "")
        for part in style.split(";"):
            if "#" in part:
                self.color_tokens.append(part.strip())

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_heading = ""

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._current_heading is not None and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading = " ".join(self._current_heading.split())
            if heading:
                self.headings.append(heading)
            self._current_heading = None
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._tag_stack and self._tag_stack[-1] in IGNORED_TEXT_TAGS:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._current_heading is not None:
            self._current_heading += " " + cleaned
        self.text_chunks.append(cleaned)


def semantic_signature(html: str) -> dict[str, Any]:
    parser = _SemanticHtmlParser()
    parser.feed(html)
    visible_text = " ".join(parser.text_chunks)
    return {
        "tag_counts": dict(sorted(parser.tag_counts.items())),
        "link_count": len([link for link in parser.links if link]),
        "links": sorted(link for link in parser.links if link),
        "heading_count": len(parser.headings),
        "headings": parser.headings,
        "visible_text_word_count": len(visible_text.split()),
        "color_token_count": len(parser.color_tokens),
        "color_tokens": sorted(set(parser.color_tokens)),
    }


def compare_signatures(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    deltas: dict[str, Any] = {}
    for key in ("tag_counts", "links", "headings", "visible_text_word_count", "color_tokens"):
        if baseline.get(key) != candidate.get(key):
            deltas[key] = {
                "baseline": baseline.get(key),
                "candidate": candidate.get(key),
            }
    return deltas


class HtmlBaselineComparator:
    """Deterministic HTML regression comparison with semantic receipts."""

    def compare(self, baseline_path: str, candidate_path: str) -> RegressionResult:
        baseline = Path(baseline_path).read_text(encoding='utf-8')
        candidate = Path(candidate_path).read_text(encoding='utf-8')

        identical = baseline == candidate
        baseline_signature = semantic_signature(baseline)
        candidate_signature = semantic_signature(candidate)
        deltas = compare_signatures(baseline_signature, candidate_signature)

        return RegressionResult(
            baseline=baseline_path,
            candidate=candidate_path,
            identical=identical,
            semantic_identical=not deltas,
            baseline_signature=baseline_signature,
            candidate_signature=candidate_signature,
            deltas=deltas,
            notes='semantic HTML comparison receipt emitted',
        )


if __name__ == '__main__':
    print('html baseline comparator active')
