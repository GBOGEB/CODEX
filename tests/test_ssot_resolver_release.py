from pathlib import Path

import pytest
import yaml

from tools.ssot_resolver import SsotResolutionError, resolve_ssot

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ssot" / "manifest.yaml"


def _write_manifest(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_release_identity_resolves_to_authoritative_yaml():
    node = resolve_ssot("CODEX_RELEASE_IDENTITY")
    assert node["path"] == "ssot/domain/repo/release.yaml"
    assert node["authority_class"] == "LOCAL_AUTHORITATIVE"
    assert len(node["sha256"]) == 64


def test_qps_is_remote_and_immutable():
    node = resolve_ssot("QPS_ENGINEERING_TRUTH")
    assert node["authority_class"] == "REMOTE_AUTHORITATIVE"
    assert node["owner"] == "GBOGEB/cryoplant-project"
    assert node["mutation_allowed"] is False


def test_unknown_logical_id_fails_closed():
    with pytest.raises(SsotResolutionError, match="UNKNOWN_ID"):
        resolve_ssot("DOES_NOT_EXIST")


def test_duplicate_authority_fails_closed(tmp_path):
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    data["authorities"]["duplicate"] = dict(data["authorities"]["master_contract"])
    manifest = _write_manifest(tmp_path, data)
    with pytest.raises(SsotResolutionError, match="DUPLICATE_AUTHORITY"):
        resolve_ssot("MASTER_CONTRACT_GOVERNANCE", manifest)


def test_remote_mutation_permission_fails_closed(tmp_path):
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    data["authorities"]["qps_engineering_truth"]["mutation_allowed"] = True
    manifest = _write_manifest(tmp_path, data)
    with pytest.raises(SsotResolutionError, match="REMOTE_MUTATION_ALLOWED"):
        resolve_ssot("QPS_ENGINEERING_TRUTH", manifest)


def test_missing_local_file_fails_closed(tmp_path):
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    data["authorities"]["master_contract"]["path"] = "does/not/exist.yaml"
    manifest = _write_manifest(tmp_path, data)
    with pytest.raises(SsotResolutionError, match="MISSING_FILE"):
        resolve_ssot("MASTER_CONTRACT_GOVERNANCE", manifest)
