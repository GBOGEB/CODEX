from src.federation.identity_broker import FederationIdentityBroker


def test_token_reuse_across_lanes_is_blocked():
    broker = FederationIdentityBroker(
        allowed_tenants={"tenant-a"},
        allowed_repositories={"GBOGEB/CODEX"},
    )
    broker.issue_office365_graph_session("token-1", metadata={"tenant": "tenant-a"})

    try:
        broker.issue_github_session("token-1", metadata={"repository": "GBOGEB/CODEX"})
        assert False, "Expected ValueError for cross-lane token reuse"
    except ValueError as exc:
        assert "Token reuse across lanes" in str(exc)


def test_markdown_telemetry_is_redacted():
    broker = FederationIdentityBroker(
        allowed_tenants={"tenant-a"},
        allowed_repositories={"GBOGEB/CODEX"},
    )
    broker.issue_office365_graph_session("sensitive-token", metadata={"tenant": "tenant-a"})
    telemetry = broker.render_markdown_ascii_telemetry()
    assert "sensitive-token" not in telemetry
    assert "office365_graph_session" in telemetry
