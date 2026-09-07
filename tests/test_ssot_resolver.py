from pathlib import Path

import pytest
import yaml

from codex.ssot_resolver import SSOTResolutionError, resolve_ssot
from tools.ssot_resolver import resolve_ssot as canonical_resolve_ssot


def test_package_import_is_compatibility_alias():
    assert resolve_ssot is canonical_resolve_ssot


def test_resolves_local_release_authority():
    node = resolve_ssot("CODEX_RELEASE_IDENTITY")
    assert node["authority_class"] == "LOCAL_AUTHORITATIVE"
    assert node["writable"] is True
    assert node["resolved_path"].endswith("ssot/domain/repo/release.yaml")


def test_resolves_bound_authority_ids():
    expected = {
        "CODEX_MASTER_CONTRACT": "ssot/master_contract_ssot_v0_2.yaml",
        "CODEX_SEMANTIC_VOCABULARY": "PIPELINE/GLOSSARY.yaml",
        "CODEX_RUNTIME_GOVERNANCE": "SSOT/g10_runtime_governance_ssot.yaml",
        "CODEX_MCP_GOVERNANCE": "SSOT/github_mcp_agentic_orchestration_ssot.yaml",
        "CODEX_RUNTIME_REGISTRY": "ssot/registry/runtime_registry.yaml",
        "TRI_REPO_RELEASE_ASSURANCE_CONTRACT": "release/TRI_REPO_RELEASE_ASSURANCE_CONTRACT_v1.yaml",
    }
    for logical_id, suffix in expected.items():
        node = resolve_ssot(logical_id)
        assert node["authority_class"] == "LOCAL_AUTHORITATIVE"
        assert node["resolved_path"].endswith(suffix)


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


def test_duplicate_authority_fails_closed(tmp_path: Path):
    manifest = yaml.safe_load(Path("ssot/manifest.yaml").read_text(encoding="utf-8"))
    manifest["authorities"]["duplicate"] = dict(manifest["authorities"]["master_contract"])
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(SSOTResolutionError, match="DUPLICATE_AUTHORITY"):
        resolve_ssot("CODEX_MASTER_CONTRACT", path)


def test_remote_mutation_fails_closed(tmp_path: Path):
    manifest = yaml.safe_load(Path("ssot/manifest.yaml").read_text(encoding="utf-8"))
    manifest["authorities"]["qps_engineering_truth"]["mutation_allowed"] = True
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(SSOTResolutionError, match="REMOTE_MUTATION_ALLOWED"):
        resolve_ssot("QPS_ENGINEERING_TRUTH", path)


def test_historical_authority_fails_closed(tmp_path: Path):
    manifest = yaml.safe_load(Path("ssot/manifest.yaml").read_text(encoding="utf-8"))
    manifest["authorities"]["master_contract"]["lifecycle"] = "HISTORICAL"
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(SSOTResolutionError, match="NON_ACTIVE_AUTHORITY"):
        resolve_ssot("CODEX_MASTER_CONTRACT", path)
