#!/usr/bin/env python3
"""Check that local SVG assets referenced in docs exist."""
import re
import sys
from pathlib import Path

DOCS_ROOT = Path("docs")

# Match src/data/href attributes and Markdown image/link syntax pointing to .svg files
_ATTR_RE = re.compile(r'(?:src|data|href)=["\']([^"\']+\.svg)["\']', re.IGNORECASE)
_MD_RE = re.compile(r'(?:!\[[^\]]*\]|(?<!!)\[[^\]]*\])\(([^)]+\.svg)\)', re.IGNORECASE)


def _local_svg_refs(text: str, base: Path) -> list[Path]:
    """Return resolved paths for local (non-URL) SVG references found in *text*."""
    refs = []
    for pattern in (_ATTR_RE, _MD_RE):
        for match in pattern.finditer(text):
            target = match.group(1).split("#")[0].split("?")[0]
            if target.startswith(("http://", "https://", "//")):
                continue
            refs.append((base / target).resolve())
    return refs


def main() -> int:
    if not DOCS_ROOT.exists():
        print("svg link check: docs/ directory not found, skipping")
        return 0

    repo_root = Path(".").resolve()
    errors = []
    for ext in ("*.html", "*.md"):
        for doc in DOCS_ROOT.rglob(ext):
            text = doc.read_text(encoding="utf-8", errors="replace")
            for resolved in _local_svg_refs(text, doc.parent):
                if not resolved.exists():
                    try:
                        rel = resolved.relative_to(repo_root)
                    except ValueError:
                        rel = resolved
                    errors.append(f"{doc}: broken SVG reference -> {rel}")

    if errors:
        print("svg link check: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("svg link check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
