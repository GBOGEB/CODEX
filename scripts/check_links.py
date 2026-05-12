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

errors = []
for html in Path('docs').rglob('*.html'):
    parser = LinkParser()
    parser.feed(html.read_text(encoding='utf-8', errors='ignore'))
    for href in parser.links:
        if href.startswith(('http://','https://','#','mailto:')):
            continue
        target = (html.parent / href).resolve()
        if not target.exists():
            errors.append(f"{html}: broken link -> {href}")

if errors:
    raise SystemExit("\n".join(errors[:100]))
print("link check passed")
