from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any


LANE_OFFICE365 = "office365_graph_session"
LANE_GITHUB = "github_session"
LANE_APPLE = "apple_personal_session"
ALLOWED_LANES = {LANE_OFFICE365, LANE_GITHUB, LANE_APPLE}


@dataclass(frozen=True)
class SessionRecord:
    lane: str
    issued_at: datetime
    expires_at: datetime
    scope: str
    token_fingerprint: str
    metadata: dict[str, Any]


class FederationIdentityBroker:
    """Issues scoped, lane-separated sessions with redacted telemetry."""

    def __init__(
        self,
        allowed_tenants: set[str] | None = None,
        allowed_repositories: set[str] | None = None,
        token_reuse_across_lanes: bool = False,
        apple_lane_enabled: bool = False,
    ):
        self.allowed_tenants = allowed_tenants or set()
        self.allowed_repositories = allowed_repositories or set()
        self.token_reuse_across_lanes = token_reuse_across_lanes
        self.apple_lane_enabled = apple_lane_enabled
        self.sessions: dict[str, SessionRecord] = {}
        self._token_lane_by_fingerprint: dict[str, str] = {}

    @staticmethod
    def _fingerprint(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]

    def _enforce_lane_rules(self, lane: str, metadata: dict[str, Any]) -> None:
        if lane not in ALLOWED_LANES:
            raise ValueError(f"Unsupported lane: {lane}")

        if lane == LANE_OFFICE365 and self.allowed_tenants:
            tenant = str(metadata.get("tenant", ""))
            if tenant not in self.allowed_tenants:
                raise ValueError(f"Tenant not allowed: {tenant}")

        if lane == LANE_GITHUB and self.allowed_repositories:
            repository = str(metadata.get("repository", ""))
            if repository and repository not in self.allowed_repositories:
                raise ValueError(f"Repository not allowed: {repository}")

        if lane == LANE_APPLE and not self.apple_lane_enabled:
            raise ValueError("apple_personal_session lane is disabled")

        if lane == LANE_APPLE and metadata.get("tenant_type") == "corporate":
            raise ValueError("Apple personal lane cannot be used for corporate tenant access")

    def _issue(
        self,
        lane: str,
        token: str,
        ttl_minutes: int,
        scope: str,
        metadata: dict[str, Any] | None = None,
    ) -> SessionRecord:
        metadata = metadata or {}
        self._enforce_lane_rules(lane, metadata)
        if not token:
            raise ValueError("token is required")

        fingerprint = self._fingerprint(token)
        existing_lane = self._token_lane_by_fingerprint.get(fingerprint)
        if existing_lane and existing_lane != lane and not self.token_reuse_across_lanes:
            raise ValueError("Token reuse across lanes is forbidden by policy")

        now = datetime.now(timezone.utc)
        record = SessionRecord(
            lane=lane,
            issued_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            scope=scope,
            token_fingerprint=fingerprint,
            metadata=dict(metadata),
        )
        self.sessions[lane] = record
        self._token_lane_by_fingerprint[fingerprint] = lane
        return record

    def issue_office365_graph_session(
        self,
        token: str,
        ttl_minutes: int = 30,
        metadata: dict[str, Any] | None = None,
    ) -> SessionRecord:
        return self._issue(LANE_OFFICE365, token, ttl_minutes, scope="graph.read", metadata=metadata)

    def issue_github_session(
        self,
        token: str,
        ttl_minutes: int = 30,
        metadata: dict[str, Any] | None = None,
    ) -> SessionRecord:
        return self._issue(LANE_GITHUB, token, ttl_minutes, scope="github.api", metadata=metadata)

    def issue_apple_personal_session(
        self,
        token: str,
        ttl_minutes: int = 30,
        metadata: dict[str, Any] | None = None,
    ) -> SessionRecord:
        return self._issue(LANE_APPLE, token, ttl_minutes, scope="apple.personal", metadata=metadata)

    def render_markdown_ascii_telemetry(self) -> str:
        lines = [
            "## [FEDERATION IDENTITY BROKER]",
            "---",
            "| Lane | Scope | Expires (UTC) | Fingerprint |",
            "|---|---|---|---|",
        ]
        if not self.sessions:
            lines.append("| (none) | - | - | - |")
        for lane in sorted(self.sessions):
            session = self.sessions[lane]
            lines.append(
                f"| {session.lane} | {session.scope} | {session.expires_at.isoformat()} | {session.token_fingerprint} |"
            )
        lines.append("\n*Telemetry redacted: raw token values are never logged.*")
        return "\n".join(lines) + "\n"
