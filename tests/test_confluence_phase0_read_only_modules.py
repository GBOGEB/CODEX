import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from confluence_client import ConfluenceClient, ConfluenceNotFoundError
from html_to_markdown import storage_html_to_markdown
from output_writer import OutputWriter


class FakeResponse:
    def __init__(self, status_code=200, payload=None, chunks=None):
        self.status_code = status_code
        self._payload = payload or {}
        self._chunks = chunks or [b"payload"]

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=8192):
        yield from self._chunks


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.auth = None
        self.calls = []

    def get(self, url, params=None, stream=False, timeout=None):
        self.calls.append({"url": url, "params": params, "stream": stream, "timeout": timeout})
        if url.endswith("/missing"):
            return FakeResponse(status_code=404)
        if "/label" in url:
            return FakeResponse(payload={"results": [{"name": "phase-0"}]})
        if url.endswith("/space/ACR"):
            return FakeResponse(payload={"key": "ACR", "name": "ACR Space"})
        if "/space" in url:
            return FakeResponse(payload={"results": [{"key": "ACR"}]})
        if "/child/attachment" in url:
            return FakeResponse(payload={"results": [{"id": "att-1", "title": "a.pdf"}]})
        if "/child/page" in url:
            return FakeResponse(payload={"results": [{"id": "child-1", "title": "Child"}]})
        if "/content/1023934467" in url:
            return FakeResponse(payload={"id": "1023934467", "ancestors": [{"id": "parent-1"}]})
        if "/content" in url:
            return FakeResponse(payload={"results": [{"id": "1023934467", "title": "Page"}]})
        return FakeResponse(chunks=[b"abc", b"def"])


def sample_page():
    return {
        "id": "1023934467",
        "type": "page",
        "title": "DSBT Task 3 - Technical Support",
        "status": "current",
        "space": {"key": "ACR"},
        "version": {"number": 7},
        "ancestors": [{"id": "parent-1", "title": "Parent", "type": "page"}],
        "metadata": {"labels": {"results": [{"name": "phase-0"}]}},
        "_links": {"webui": "/wiki/spaces/ACR/pages/1023934467"},
        "body": {
            "storage": {
                "value": """
<h1>Support</h1>
<p>See <a href="https://example.com">external</a>.</p>
<ac:link><ri:page ri:space-key="ACR" ri:content-title="Sibling Page"/><ac:plain-text-link-body>Sibling</ac:plain-text-link-body></ac:link>
<ac:structured-macro ac:name="info"><ac:rich-text-body><p>Read only.</p></ac:rich-text-body></ac:structured-macro>
<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">python</ac:parameter><ac:plain-text-body>print('ok')</ac:plain-text-body></ac:structured-macro>
<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
<ac:image><ri:attachment ri:filename="diagram.png" /></ac:image>
"""
            }
        },
    }


def test_confluence_client_read_only_methods_and_download(tmp_path):
    session = FakeSession()
    client = ConfluenceClient("https://myrrha.atlassian.net", "user@example.com", "token", session=session)

    assert client.get_space("ACR")["key"] == "ACR"
    assert client.list_spaces()[0]["key"] == "ACR"
    assert client.list_pages_in_space("ACR")[0]["id"] == "1023934467"
    assert client.get_page_ancestors("1023934467")[0]["id"] == "parent-1"
    assert client.get_labels("1023934467") == ["phase-0"]

    saved = client.download_attachment("/download/attachments/1023934467/a.pdf", tmp_path / "a.pdf")
    assert Path(saved).read_bytes() == b"abcdef"
    assert all(
        (parsed.scheme == "https" and parsed.hostname == "myrrha.atlassian.net")
        for parsed in (urlparse(call["url"]) for call in session.calls)
    )


def test_confluence_client_download_missing_raises(tmp_path):
    client = ConfluenceClient("https://myrrha.atlassian.net", "user@example.com", "token", session=FakeSession())
    try:
        client.download_attachment("/missing", tmp_path / "missing.bin")
    except ConfluenceNotFoundError:
        return
    raise AssertionError("expected ConfluenceNotFoundError")


def test_storage_html_to_markdown_handles_confluence_tags():
    markdown = storage_html_to_markdown(sample_page()["body"]["storage"]["value"], base_url="https://myrrha.atlassian.net")

    assert "# Support" in markdown
    assert "[Sibling](https://myrrha.atlassian.net/wiki/spaces/ACR/pages/search?title=Sibling+Page)" in markdown
    assert "[INFO]" in markdown
    assert "```" in markdown
    assert "| A | B |" in markdown
    assert "![diagram.png](diagram.png)" in markdown


def test_output_writer_writes_complete_page_artifacts(tmp_path):
    writer = OutputWriter(output_root=tmp_path, base_url="https://myrrha.atlassian.net")
    written = writer.write_page(
        sample_page(),
        attachments=[{"id": "att-1", "title": "diagram.png", "metadata": {"mediaType": "image/png"}, "_links": {"download": "/download/attachments/1023934467/diagram.png"}}],
        children=[{"id": "child-1", "title": "Child", "type": "page"}],
    )

    assert set(written) == {"raw_storage_html", "content_md", "metadata_yaml", "links_json", "attachments_json", "hierarchy_json"}
    page_dir = tmp_path / "page_1023934467"
    metadata = yaml.safe_load((page_dir / "metadata.yaml").read_text())
    links = json.loads((page_dir / "links.json").read_text())
    attachments = json.loads((page_dir / "attachments.json").read_text())
    hierarchy = json.loads((page_dir / "hierarchy.json").read_text())

    assert metadata["counts"]["macros"] == 2
    assert metadata["labels"] == ["phase-0"]
    assert any(link["type"] == "confluence_page" for link in links["links"])
    assert attachments["attachments"][0]["absolute_download_url"].startswith("https://myrrha.atlassian.net/download")
    assert hierarchy["ancestors"][0]["id"] == "parent-1"
    assert hierarchy["children"][0]["id"] == "child-1"
