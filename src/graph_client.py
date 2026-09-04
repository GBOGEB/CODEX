"""
Microsoft Graph API client for OneDrive/SharePoint file upload/download.

Mirrors src/confluence_client.py's shape: credentials via a config object with
a from_environment() classmethod, custom exception hierarchy, a session=
constructor parameter used purely as a test seam. Uses the client-credentials
(app-only) OAuth flow via msal -- the simplest flow for a background/service
scenario. Delegated/interactive auth is a different, heavier pattern and is
out of scope here.

Real use requires an Azure AD app registration this client cannot provision
itself: register an app in Azure Portal -> App registrations, record the
Tenant ID / Client ID, create a client secret under Certificates & secrets,
and grant Microsoft Graph Application permissions (Files.ReadWrite.All or
Sites.ReadWrite.All) with admin consent. Until GRAPH_TENANT_ID/
GRAPH_CLIENT_ID/GRAPH_CLIENT_SECRET are set to real values, real calls will
401 -- that is expected, not a bug in this module.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_GRAPH_API_ROOT = "https://graph.microsoft.com/v1.0"
_DEFAULT_SCOPES = ["https://graph.microsoft.com/.default"]

# Files.ReadWrite content endpoints only support this size via a single PUT;
# larger files need a resumable upload session, which this minimal client
# does not implement.
_SIMPLE_UPLOAD_MAX_BYTES = 4 * 1024 * 1024


class GraphError(RuntimeError):
    """Base exception for Microsoft Graph client failures."""


class GraphAuthError(GraphError):
    """Raised when Graph authentication or authorization fails."""


class GraphNotFoundError(GraphError):
    """Raised when a Graph drive item is not found."""


@dataclass
class GraphConfig:
    """Azure AD app-only credentials for the Microsoft Graph client-credentials flow."""

    tenant_id: str
    client_id: str
    client_secret: str
    scopes: list[str] = field(default_factory=lambda: list(_DEFAULT_SCOPES))
    timeout: int = 30

    @classmethod
    def from_environment(cls, timeout: int = 30) -> "GraphConfig":
        """Create a config from GRAPH_TENANT_ID / GRAPH_CLIENT_ID / GRAPH_CLIENT_SECRET.

        Secrets are never persisted to disk by this class -- there is no
        to_dict() or save_to_file(), matching the repo-wide convention of
        keeping credentials in-memory only.
        """

        tenant_id = os.getenv("GRAPH_TENANT_ID")
        client_id = os.getenv("GRAPH_CLIENT_ID")
        client_secret = os.getenv("GRAPH_CLIENT_SECRET")
        if not tenant_id or not client_id or not client_secret:
            raise GraphAuthError(
                "GRAPH_TENANT_ID, GRAPH_CLIENT_ID, and GRAPH_CLIENT_SECRET are required"
            )
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
        )


class GraphClient:
    """Small Microsoft Graph client for OneDrive/SharePoint file upload/download.

    Parameters
    ----------
    config:
        Azure AD app-only credentials.
    session:
        Optional preconfigured ``requests.Session`` for tests or custom adapters.
    msal_app:
        Optional preconfigured MSAL confidential-client application -- a
        deliberate test seam so tests never touch real MSAL internals.
    """

    def __init__(
        self,
        config: GraphConfig,
        session: Optional[requests.Session] = None,
        msal_app: Optional[Any] = None,
    ) -> None:
        self.config = config
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": "CODEX-Graph-Client/0.1"})
        self._msal_app = msal_app or self._build_msal_app()
        self._token: Optional[str] = None

    def _build_msal_app(self) -> Any:
        import msal  # noqa: PLC0415 - optional dependency, only needed for real auth

        return msal.ConfidentialClientApplication(
            client_id=self.config.client_id,
            client_credential=self.config.client_secret,
            authority=f"https://login.microsoftonline.com/{self.config.tenant_id}",
        )

    def _access_token(self) -> str:
        if self._token is not None:
            return self._token

        result = self._msal_app.acquire_token_for_client(scopes=self.config.scopes)
        token = result.get("access_token") if isinstance(result, dict) else None
        if not token:
            error_description = (
                result.get("error_description", "unknown error")
                if isinstance(result, dict)
                else "unknown error"
            )
            raise GraphAuthError(f"Failed to acquire Graph access token: {error_description}")

        self._token = token
        return token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token()}"}

    def _drive_item_url(self, drive_relative_path: str, drive_id: Optional[str] = None) -> str:
        path = drive_relative_path.strip("/")
        if drive_id:
            return f"{_GRAPH_API_ROOT}/drives/{drive_id}/root:/{path}:"
        return f"{_GRAPH_API_ROOT}/me/drive/root:/{path}:"

    def upload_file(
        self,
        local_path: Path,
        drive_relative_path: str,
        drive_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload a small file (<4MB) to OneDrive/SharePoint via a single PUT.

        Larger files require a resumable upload session
        (POST .../createUploadSession), which this minimal client does not
        implement.
        """

        resolved = Path(local_path)
        size = resolved.stat().st_size
        if size > _SIMPLE_UPLOAD_MAX_BYTES:
            raise GraphError(
                f"{resolved} is {size} bytes; simple upload supports at most "
                f"{_SIMPLE_UPLOAD_MAX_BYTES} bytes. Use a resumable upload session "
                "(not implemented in this client) for larger files."
            )

        url = f"{self._drive_item_url(drive_relative_path, drive_id)}/content"
        with resolved.open("rb") as handle:
            resp = self._session.put(
                url,
                headers=self._headers(),
                data=handle,
                timeout=self.config.timeout,
            )

        self._raise_for_status(resp, url)
        return resp.json()

    def download_file(
        self,
        drive_relative_path: str,
        local_path: Path,
        drive_id: Optional[str] = None,
    ) -> Path:
        """Download a file from OneDrive/SharePoint, streaming to disk."""

        url = f"{self._drive_item_url(drive_relative_path, drive_id)}/content"
        resp = self._session.get(
            url,
            headers=self._headers(),
            stream=True,
            timeout=self.config.timeout,
        )
        self._raise_for_status(resp, url)

        dest = Path(local_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)

        logger.info("Graph download saved -> %s", dest)
        return dest.resolve()

    def _raise_for_status(self, resp: requests.Response, url: str) -> None:
        if resp.status_code == 404:
            raise GraphNotFoundError(f"Graph drive item not found: {url}")
        if resp.status_code in {401, 403}:
            raise GraphAuthError(f"Graph authentication failed for {url}: HTTP {resp.status_code}")
        resp.raise_for_status()

    def __repr__(self) -> str:
        return f"GraphClient(tenant_id={self.config.tenant_id!r})"
