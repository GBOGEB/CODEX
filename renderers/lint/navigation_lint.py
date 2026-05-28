from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:")


@dataclass
class NavigationIssue:
    component: str
    severity: str
    message: str


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        for key in ("href", "src"):
            if key in attr_map and attr_map[key]:
                self.links.append(str(attr_map[key]))


def _extract_links(html_path: Path) -> list[str]:
    parser = _LinkParser()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    return parser.links


def validate_navigation_ids() -> list[NavigationIssue]:
    """Validate stable navigation and lineage requirements.

    Future implementation should:
    - validate slide-id uniqueness
    - validate figure references
    - validate local next/previous linkage
    - validate GitHub Pages anchor integrity
    """

    return []


def validate_docs_link_boundaries(
    docs_root: Path | None = None,
) -> list[NavigationIssue]:
    """Validate that internal links in docs/ HTML files do not escape the published site.

    Published roots are docs/ and outputs/ (both staged to GitHub Pages).
    Links resolving into either published root are allowed.
    External URLs (http/https/etc.) and anchor-only fragments are skipped.
    """
    if docs_root is None:
        docs_root = Path(__file__).resolve().parents[2] / "docs"

    if not docs_root.exists():
        return []

    repo_root = docs_root.parent
    allowed_roots = {docs_root.resolve(), (repo_root / "outputs").resolve()}

    issues: list[NavigationIssue] = []

    for html_file in sorted(docs_root.rglob("*.html")):
        for raw_link in _extract_links(html_file):
            link = raw_link.strip().split("#")[0].split("?")[0].strip()
            if not link:
                continue
            if any(link.startswith(p) for p in SKIP_PREFIXES):
                continue
            resolved = (html_file.parent / link).resolve()
            if not any(
                str(resolved).startswith(str(allowed) + "/") or resolved == allowed
                for allowed in allowed_roots
            ):
                rel_file = html_file.relative_to(repo_root)
                issues.append(
                    NavigationIssue(
                        component=str(rel_file),
                        severity="error",
                        message=f"link '{link}' escapes published site boundary → {resolved}",
                    )
                )

    return issues


def main() -> int:
    issues = [
        *validate_navigation_ids(),
        *validate_docs_link_boundaries(),
    ]
    if issues:
        for item in issues:
            print(f"[{item.severity}] {item.component}: {item.message}")
        return 1

    print("navigation governance checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

