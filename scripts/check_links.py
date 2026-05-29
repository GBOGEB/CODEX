import re
from html.parser import HTMLParser
from pathlib import Path


class HtmlLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
        if "src" in attrs_dict:
            self.links.append(attrs_dict["src"])


MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
YAML_PATH_KEY_RE = re.compile(
    r"^\s*[\w-]*(?:url|href|src|path|file|link)[\w-]*\s*:\s*[\"']?([^\"'#\s]+)",
    re.IGNORECASE | re.MULTILINE,
)
CSS_URL_RE = re.compile(r"url\(([^)]+)\)", re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:")
CHECKED_PAGE_EXTENSIONS = {".html", ".htm", ".md", ".yaml", ".yml", ".css"}

repo_root = Path(".").resolve()
docs_root = (repo_root / "docs").resolve()
allowed_site_roots = ("outputs",)
errors = []


def normalize_link(raw_link: str) -> str:
    cleaned = raw_link.strip().strip("'\"")
    return cleaned.split("#", 1)[0].split("?", 1)[0].strip()


def extract_links(file_path: Path) -> list[tuple[str, str]]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    suffix = file_path.suffix.lower()
    if suffix == ".html":
        parser = HtmlLinkParser()
        parser.feed(content)
        return [(link, "html") for link in parser.links]
    if suffix == ".md":
        return [(match.group(1), "md") for match in MARKDOWN_LINK_RE.finditer(content)]
    if suffix in {".yaml", ".yml"}:
        links = []
        for match in YAML_PATH_KEY_RE.finditer(content):
            candidate = match.group(1).strip()
            candidate_no_fragment = normalize_link(candidate)
            candidate_ext = Path(candidate_no_fragment).suffix.lower()
            if (
                "/" in candidate
                or "." in candidate
                or candidate.startswith(("./", "../"))
            ) and not candidate.endswith(":") and candidate_ext in CHECKED_PAGE_EXTENSIONS:
                links.append((candidate, "yaml"))
        return links
    if suffix == ".css":
        return [(match.group(1), "css") for match in CSS_URL_RE.finditer(content)]
    return []


def validate_link(source_file: Path, href: str, link_kind: str) -> None:
    if href.startswith(SKIP_PREFIXES):
        return

    path_href = normalize_link(href)
    if not path_href:
        return

    if link_kind == "yaml":
        if path_href.startswith("/"):
            target = (repo_root / path_href.lstrip("/")).resolve()
        elif path_href.startswith(("./", "../")):
            target = (source_file.parent / path_href).resolve()
        else:
            target = (repo_root / path_href).resolve()
    else:
        if path_href.startswith("/"):
            if source_file.is_relative_to(docs_root) and link_kind == "html":
                target = (docs_root / path_href.lstrip("/")).resolve()
            else:
                target = (repo_root / path_href.lstrip("/")).resolve()
        else:
            target = (source_file.parent / path_href).resolve()

    if source_file.is_relative_to(docs_root) and link_kind == "html":
        try:
            target.relative_to(docs_root)
        except ValueError:
            try:
                target.relative_to(repo_root)
                if any(
                    target.is_relative_to(repo_root / allowed_root)
                    for allowed_root in allowed_site_roots
                ) and target.exists():
                    return
            except ValueError:
                pass
            errors.append(f"{source_file}: link escapes docs root -> {href}")
            return
        if not target.exists():
            errors.append(f"{source_file}: broken link -> {href}")
        return

    try:
        target.relative_to(repo_root)
    except ValueError:
        errors.append(f"{source_file}: link escapes repo root -> {href}")
        return
    if not target.exists():
        errors.append(f"{source_file}: broken link -> {href}")


files_to_check = sorted(
    set(docs_root.rglob("*.html"))
    | set(docs_root.rglob("*.md"))
    | set(docs_root.rglob("*.yaml"))
    | set(docs_root.rglob("*.yml"))
    | set(docs_root.rglob("*.css"))
)
readme = repo_root / "README.md"
if readme.exists():
    files_to_check.append(readme)

for source_file in files_to_check:
    for href, link_kind in extract_links(source_file):
        validate_link(source_file, href, link_kind)

if errors:
    raise SystemExit("\n".join(errors[:100]))

print("link check passed")
