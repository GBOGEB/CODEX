from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph_client import (  # noqa: E402
    GraphAuthError,
    GraphClient,
    GraphConfig,
    GraphNotFoundError,
)


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
        self.calls = []

    def put(self, url, headers=None, data=None, timeout=None):
        self.calls.append({"method": "PUT", "url": url, "headers": headers})
        if url.endswith("/missing:/content"):
            return FakeResponse(status_code=404)
        return FakeResponse(payload={"id": "item-1", "name": Path(url).stem})

    def get(self, url, headers=None, stream=False, timeout=None):
        self.calls.append({"method": "GET", "url": url, "headers": headers, "stream": stream})
        if url.endswith("/missing:/content"):
            return FakeResponse(status_code=404)
        if url.endswith("/denied:/content"):
            return FakeResponse(status_code=403)
        return FakeResponse(chunks=[b"abc", b"def"])


class FakeMsalApp:
    def __init__(self, token="fake-token", error=None):
        self._token = token
        self._error = error
        self.acquire_calls = []

    def acquire_token_for_client(self, scopes):
        self.acquire_calls.append(scopes)
        if self._error:
            return {"error": "invalid_client", "error_description": self._error}
        return {"access_token": self._token}


def make_config(**overrides) -> GraphConfig:
    defaults = dict(tenant_id="tenant-1", client_id="client-1", client_secret="secret-1")
    defaults.update(overrides)
    return GraphConfig(**defaults)


def test_config_from_environment_reads_required_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GRAPH_TENANT_ID", "tenant-1")
    monkeypatch.setenv("GRAPH_CLIENT_ID", "client-1")
    monkeypatch.setenv("GRAPH_CLIENT_SECRET", "secret-1")

    config = GraphConfig.from_environment()

    assert config.tenant_id == "tenant-1"
    assert config.client_id == "client-1"
    assert config.client_secret == "secret-1"


def test_config_from_environment_requires_all_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GRAPH_TENANT_ID", raising=False)
    monkeypatch.delenv("GRAPH_CLIENT_ID", raising=False)
    monkeypatch.delenv("GRAPH_CLIENT_SECRET", raising=False)

    with pytest.raises(GraphAuthError):
        GraphConfig.from_environment()


def test_upload_file_puts_content_and_returns_item(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(make_config(), session=session, msal_app=FakeMsalApp())

    local_file = tmp_path / "report.pdf"
    local_file.write_bytes(b"pdf-bytes")

    result = client.upload_file(local_file, "QPS/reports/report.pdf")

    assert result["id"] == "item-1"
    assert session.calls[0]["method"] == "PUT"
    assert "QPS/reports/report.pdf" in session.calls[0]["url"]
    assert session.calls[0]["headers"]["Authorization"] == "Bearer fake-token"


def test_upload_file_rejects_oversized_files(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(make_config(), session=session, msal_app=FakeMsalApp())

    local_file = tmp_path / "big.bin"
    with local_file.open("wb") as handle:
        handle.seek(4 * 1024 * 1024)
        handle.write(b"0")

    with pytest.raises(Exception, match="simple upload supports at most"):
        client.upload_file(local_file, "big.bin")


def test_download_file_streams_to_disk(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(make_config(), session=session, msal_app=FakeMsalApp())

    destination = tmp_path / "nested" / "downloaded.txt"
    result = client.download_file("QPS/reports/report.pdf", destination)

    assert result == destination.resolve()
    assert destination.read_bytes() == b"abcdef"


def test_download_file_raises_not_found(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(make_config(), session=session, msal_app=FakeMsalApp())

    with pytest.raises(GraphNotFoundError):
        client.download_file("missing", tmp_path / "out.txt")


def test_download_file_raises_auth_error_on_403(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(make_config(), session=session, msal_app=FakeMsalApp())

    with pytest.raises(GraphAuthError):
        client.download_file("denied", tmp_path / "out.txt")


def test_upload_file_raises_auth_error_when_token_acquisition_fails(tmp_path: Path) -> None:
    session = FakeSession()
    client = GraphClient(
        make_config(),
        session=session,
        msal_app=FakeMsalApp(error="AADSTS7000215: invalid client secret"),
    )

    local_file = tmp_path / "report.pdf"
    local_file.write_bytes(b"pdf-bytes")

    with pytest.raises(GraphAuthError, match="invalid client secret"):
        client.upload_file(local_file, "report.pdf")
