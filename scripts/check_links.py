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

repo_root = Path(".").resolve()
docs_root = (repo_root / "docs").resolve()
allowed_site_roots = ("outputs",)
errors = []


def normalize_link(raw_link: str) -> str:
    cleaned = raw_link.strip().strip("'\"")
    return cleaned.split("#", 1)[0].split("?", 1)[0].strip()


def extract_links(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    suffix = file_path.suffix.lower()
    if suffix == ".html":
        parser = HtmlLinkParser()
        parser.feed(content)
        return parser.links
    if suffix == ".md":
        return [match.group(1) for match in MARKDOWN_LINK_RE.finditer(content)]
    if suffix in {".yaml", ".yml"}:
        return [match.group(1) for match in YAML_PATH_KEY_RE.finditer(content)]
    if suffix == ".css":
        return [match.group(1) for match in CSS_URL_RE.finditer(content)]
    return []


def validate_link(source_file: Path, href: str) -> None:
    if href.startswith(SKIP_PREFIXES):
        return

    path_href = normalize_link(href)
    if not path_href:
        return

    if path_href.startswith("/"):
        if source_file.is_relative_to(docs_root):
            target = (docs_root / path_href.lstrip("/")).resolve()
        else:
            target = (repo_root / path_href.lstrip("/")).resolve()
    else:
        target = (source_file.parent / path_href).resolve()

    if source_file.is_relative_to(docs_root):
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
    for href in extract_links(source_file):
        validate_link(source_file, href)

if errors:
    raise SystemExit("\n".join(errors[:100]))

print("link check passed")
