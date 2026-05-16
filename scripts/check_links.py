from html.parser import HTMLParser
from pathlib import Path

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

docs_root = Path('docs').resolve()
repo_root = Path('.').resolve()
allowed_site_roots = ('outputs',)
errors = []
for html in docs_root.rglob('*.html'):
    parser = LinkParser()
    parser.feed(html.read_text(encoding='utf-8', errors='ignore'))
    for href in parser.links:
        if href.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        path_href = href.split('#', 1)[0].split('?', 1)[0]
        if not path_href:
            continue
        if path_href.startswith('/'):
            target = (docs_root / path_href.lstrip('/')).resolve()
        else:
            target = (html.parent / path_href).resolve()
        try:
            target.relative_to(docs_root)
        except ValueError:
            try:
                target.relative_to(repo_root)
                if any(
                    target.is_relative_to(repo_root / root)
                    for root in allowed_site_roots
                ) and target.exists():
                    continue
            except ValueError:
                pass
            errors.append(f"{html}: link escapes docs root -> {href}")
            continue
        if not target.exists():
            errors.append(f"{html}: broken link -> {href}")

if errors:
    raise SystemExit("\n".join(errors[:100]))
print("link check passed")
