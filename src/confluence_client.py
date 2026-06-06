"""
Read-only Confluence Cloud REST API client for Phase 0 ingestion.

The client intentionally exposes only GET/download operations. It does not
publish, update, delete, or otherwise mutate Confluence content while Phase 0
read-only ingestion is being stabilized.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests

logger = logging.getLogger(__name__)


class ConfluenceError(RuntimeError):
    """Base exception for Confluence client failures."""


class ConfluenceNotFoundError(ConfluenceError):
    """Raised when a Confluence resource is not found."""


class ConfluenceAuthError(ConfluenceError):
    """Raised when Confluence authentication or authorization fails."""


class ConfluenceClient:
    """Small read-only client for the Confluence Cloud v1 REST API.

    Parameters
    ----------
    base_url:
        Atlassian site root, for example ``https://myrrha.atlassian.net``.
    email:
        Atlassian account email used for Basic Auth.
    api_token:
        Atlassian API token used for Basic Auth.
    timeout:
        Per-request timeout in seconds.
    session:
        Optional preconfigured ``requests.Session`` for tests or custom adapters.
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_root = f"{self.base_url}/wiki/rest/api"
        self.email = email
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.auth = (email, api_token)
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "CODEX-Confluence-GitHub-Bridge/0.1",
            }
        )

    @classmethod
    def from_environment(cls, timeout: int = 30) -> "ConfluenceClient":
        """Create a client from Phase 0 Confluence environment variables."""
        base_url = os.getenv("CONFLUENCE_BASE_URL", "https://myrrha.atlassian.net")
        email = os.getenv("CONFLUENCE_EMAIL")
        api_token = os.getenv("CONFLUENCE_API_TOKEN")
        if not email or not api_token:
            raise ConfluenceAuthError("CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN are required")
        return cls(base_url=base_url, email=email, api_token=api_token, timeout=timeout)

    def _url(self, path: str) -> str:
        """Build an absolute Confluence REST API URL from an API path."""
        return urljoin(f"{self.api_root}/", path.lstrip("/"))

    def _get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a read-only GET request and return decoded JSON."""
        url = self._url(path)
        logger.debug("GET %s params=%s", url, params)
        resp = self._session.get(url, params=params, timeout=self.timeout)

        if resp.status_code == 404:
            raise ConfluenceNotFoundError(f"Confluence resource not found: {url}")
        if resp.status_code in {401, 403}:
            raise ConfluenceAuthError(f"Confluence authentication failed for {url}: HTTP {resp.status_code}")
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, dict):
            raise ConfluenceError(f"Expected JSON object from {url}, got {type(payload).__name__}")
        return payload

    def _get_results(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return all visible results for paged read-only endpoints."""
        results: List[Dict[str, Any]] = []
        start = 0
        while True:
            page_params = dict(params or {})
            page_params.setdefault("limit", limit)
            page_params["start"] = start
            payload = self._get_json(path, params=page_params)
            batch = payload.get("results", [])
            results.extend(batch)
            if len(batch) < int(page_params["limit"]):
                break
            start += len(batch)
        return results

    def get_page(self, page_id: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """Return a page with storage body and hierarchy metadata by default."""
        expansion = expand or "body.storage,version,ancestors,children.page,space,metadata.labels"
        return self._get_json(f"/content/{page_id}", params={"expand": expansion})

    def get_attachments(self, page_id: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Return attachment records for a page."""
        return self._get_results(f"/content/{page_id}/child/attachment", limit=limit)

    def get_children(self, page_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Return child pages for a page."""
        return self._get_results(
            f"/content/{page_id}/child/page",
            params={"expand": "version,ancestors"},
            limit=limit,
        )

    def download_attachment(
        self,
        download_path: str,
        dest_path: "os.PathLike[str]",
    ) -> str:
        from pathlib import Path

        parsed = urlparse(download_path)
        full_url = download_path if parsed.scheme else f"{self.base_url}{download_path}"
        resp = self._session.get(full_url, stream=True, timeout=self.timeout)

        if resp.status_code == 404:
            raise ConfluenceNotFoundError(
                f"Attachment not found: {full_url}"
            )
        if resp.status_code in {401, 403}:
            raise ConfluenceAuthError(f"Confluence authentication failed for {full_url}: HTTP {resp.status_code}")
        resp.raise_for_status()

        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

        logger.info("Attachment saved → %s", dest)
        return str(dest.resolve())

    def get_space(self, space_key: str) -> Dict[str, Any]:
        """Return space metadata for a given space key."""
        return self._get_json(f"/space/{space_key}")

    def list_spaces(
        self,
        space_type: str = "global",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List all spaces visible to the authenticated user."""
        return self._get_results(
            "/space",
            params={"type": space_type},
            limit=limit,
        )

    def list_pages_in_space(
        self,
        space_key: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List all pages in a space (shallow — no body expansion)."""
        return self._get_results(
            "/content",
            params={
                "spaceKey": space_key,
                "type": "page",
                "expand": "version,ancestors",
            },
            limit=limit,
        )

    def get_page_ancestors(self, page_id: str) -> List[Dict[str, Any]]:
        """Return ancestor chain (breadcrumb) for a page."""
        page = self._get_json(
            f"/content/{page_id}",
            params={"expand": "ancestors"},
        )
        return page.get("ancestors", [])

    def get_labels(self, page_id: str) -> List[str]:
        """Return list of label strings attached to a page."""
        labels = self._get_results(f"/content/{page_id}/label", limit=100)
        return [lbl["name"] for lbl in labels if "name" in lbl]

    # ── Representation ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"ConfluenceClient("
            f"base_url={self.base_url!r}, "
            f"email={self.email!r})"
        )
