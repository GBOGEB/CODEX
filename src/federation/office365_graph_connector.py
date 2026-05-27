from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import requests


@dataclass(frozen=True)
class BinaryIndexEntry:
    file_id: str
    tenant: str
    version_id: str
    checksum_sha256: str
    source_url: str
    classification: str
    local_path: str
    indexed_at: str


class Office365GraphConnector:
    """Lightweight Office365 Graph adapter for binary metadata and download."""

    def __init__(
        self,
        token: str,
        tenant: str,
        graph_base_url: str = "https://graph.microsoft.com/v1.0",
        cache_root: str | Path = "outputs/office365_cache",
        allowed_tenants: set[str] | None = None,
        request_timeout: int = 20,
    ):
        if not token:
            raise ValueError("token is required")
        self.token = token
        self.tenant = tenant
        self.graph_base_url = graph_base_url.rstrip("/")
        self.cache_root = Path(cache_root)
        self.cache_root.mkdir(parents=True, exist_ok=True)
        self.allowed_tenants = allowed_tenants or set()
        self.request_timeout = request_timeout
        if self.allowed_tenants and tenant not in self.allowed_tenants:
            raise ValueError(f"Tenant not allowed: {tenant}")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get_json(self, url: str) -> dict[str, Any]:
        response = requests.get(url, headers=self._headers(), timeout=self.request_timeout)
        response.raise_for_status()
        return response.json()

    def _get_binary(self, url: str) -> bytes:
        response = requests.get(url, headers=self._headers(), timeout=self.request_timeout)
        response.raise_for_status()
        return response.content

    def list_library_items(self, drive_id: str, folder_path: str = "") -> list[dict[str, Any]]:
        if folder_path:
            endpoint = f"{self.graph_base_url}/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            endpoint = f"{self.graph_base_url}/drives/{drive_id}/root/children"
        payload = self._get_json(endpoint)
        return list(payload.get("value", []))

    def fetch_file_metadata(self, drive_id: str, item_id: str) -> dict[str, Any]:
        endpoint = f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}"
        return self._get_json(endpoint)

    def download_binary(self, drive_id: str, item_id: str, target_name: str | None = None) -> Path:
        endpoint = f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}/content"
        payload = self._get_binary(endpoint)
        filename = target_name or f"{item_id}.bin"
        output_path = self.cache_root / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)
        return output_path

    @staticmethod
    def checksum_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def verify_checksum(self, path: Path, expected_sha256: str) -> bool:
        return self.checksum_sha256(path) == expected_sha256

    def prune_cache(self, max_age_hours: int = 24) -> list[Path]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        removed: list[Path] = []
        for path in self.cache_root.rglob("*"):
            if not path.is_file():
                continue
            modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if modified < cutoff:
                path.unlink(missing_ok=True)
                removed.append(path)
        return removed

    def build_binary_index_entry(
        self,
        metadata: dict[str, Any],
        local_path: Path,
        classification: str,
    ) -> BinaryIndexEntry:
        version = metadata.get("eTag") or metadata.get("cTag") or "unknown"
        source_url = metadata.get("webUrl") or metadata.get("@microsoft.graph.downloadUrl") or ""
        file_id = metadata.get("id", local_path.stem)
        return BinaryIndexEntry(
            file_id=file_id,
            tenant=self.tenant,
            version_id=str(version),
            checksum_sha256=self.checksum_sha256(local_path),
            source_url=source_url,
            classification=classification,
            local_path=str(local_path),
            indexed_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def write_binary_index_ledger(entries: list[BinaryIndexEntry], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "entries": [entry.__dict__ for entry in entries],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
