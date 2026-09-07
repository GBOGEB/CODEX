import pytest

from codex.ssot_resolver import SSOTResolutionError, resolve_ssot


def test_resolves_local_release_authority():
    node = resolve_ssot("CODEX_RELEASE_IDENTITY")
    assert node["authority_class"] == "LOCAL_AUTHORITATIVE"
    assert node["writable"] is True
    assert node["resolved_path"].endswith("VERSION.json")


def test_qps_engineering_truth_is_remote_and_read_only():
    node = resolve_ssot("QPS_ENGINEERING_TRUTH")
    assert node["owner_repository"] == "GBOGEB/cryoplant-project"
    assert node["authority_class"] == "REMOTE_AUTHORITATIVE"
    assert node["mutation_allowed"] is False
    assert node["writable"] is False


def test_remote_engineering_truth_cannot_be_requested_as_local():
    with pytest.raises(SSOTResolutionError, match="REMOTE_AUTHORITY"):
        resolve_ssot("QPS_ENGINEERING_TRUTH", require_local=True)


def test_unknown_logical_id_fails_closed():
    with pytest.raises(SSOTResolutionError, match="UNKNOWN_ID"):
        resolve_ssot("NOT_A_REAL_AUTHORITY")
