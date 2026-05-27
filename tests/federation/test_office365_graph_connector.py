from pathlib import Path

from src.federation.office365_graph_connector import Office365GraphConnector


class FakeConnector(Office365GraphConnector):
    def __init__(self, cache_root: Path):
        super().__init__(
            token="token",
            tenant="tenant-a",
            cache_root=cache_root,
            allowed_tenants={"tenant-a"},
        )

    def _get_json(self, url: str):
        if url.endswith("/children"):
            return {"value": [{"id": "item-1", "name": "design.docx"}]}
        return {
            "id": "item-1",
            "eTag": "v1",
            "webUrl": "https://example/file",
        }

    def _get_binary(self, url: str):
        return b"binary-data"


def test_download_and_checksum(tmp_path: Path):
    connector = FakeConnector(tmp_path)
    out = connector.download_binary("drive", "item-1", "design.docx")
    assert out.exists()
    checksum = connector.checksum_sha256(out)
    assert connector.verify_checksum(out, checksum)


def test_binary_index_ledger(tmp_path: Path):
    connector = FakeConnector(tmp_path)
    local = connector.download_binary("drive", "item-1", "design.docx")
    metadata = connector.fetch_file_metadata("drive", "item-1")
    entry = connector.build_binary_index_entry(metadata, local, "engineering-pid")
    ledger = connector.write_binary_index_ledger([entry], tmp_path / "ledger" / "index.json")
    assert ledger.exists()
    assert "engineering-pid" in ledger.read_text(encoding="utf-8")
