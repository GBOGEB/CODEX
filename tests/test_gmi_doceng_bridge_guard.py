import json
from pathlib import Path

from scripts.gmi_doceng_bridge_guard import CORE_PATHS, build_receipt


CLI_BYTES = b"print('bridge')\n"
VALID_BINDING = {
    "schema": "gmi.doceng.source_binding/v1",
    "package": "GMI-DOCENG-001",
    "status": "POINTER_BOUND_BYTES_NOT_REHASHED",
    "source_role": "AUTHORITATIVE_MASTER_CANDIDATE",
    "repository": "GBOGEB/DOCX_RTM_Automation",
    "indexed_source_commit": "193cafd25ea343c01036342400dca4eaa0252536",
    "path": "addenda/QPS_Addendum_II_Master.docx",
    "git_blob": "d95e6a15e28e0bf9e810e434b79b62e396511aaf",
    "size_bytes": 5063178,
    "sha256": "ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9",
}


def _write(root: Path, rel: str, data: bytes = b"x") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _seed_core(root: Path) -> str:
    import hashlib

    for rel in CORE_PATHS:
        _write(root, rel, CLI_BYTES if rel == "ARTIFACTS/cli.py" else b"x")
    return hashlib.sha256(CLI_BYTES).hexdigest()


def _write_binding(root: Path, payload: dict = VALID_BINDING) -> None:
    path = root / "ARTIFACTS/input/source_binding.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_rejects_missing_core(tmp_path: Path) -> None:
    receipt = build_receipt(tmp_path, "0" * 64)
    assert receipt["disposition"] == "REJECT"
    assert receipt["missing_core_paths"]


def test_defers_when_core_valid_but_source_identity_missing(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "DEFER_SOURCE_BINDING"
    assert receipt["source_verification_level"] == "NO_SOURCE_IDENTITY"


def test_accepts_valid_pointer_without_claiming_byte_rehash(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write_binding(tmp_path)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "ACCEPT_SOURCE_POINTER_BOUND"
    assert receipt["source_binding_valid"] is True
    assert receipt["source_verification_level"] == "POINTER_BOUND_BYTES_NOT_REHASHED"
    assert receipt["source_binding"]["sha256"] == VALID_BINDING["sha256"]


def test_rejects_malformed_pointer_binding(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    malformed = dict(VALID_BINDING)
    malformed["git_blob"] = "not-a-git-object"
    _write_binding(tmp_path, malformed)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "REJECT"
    assert "git_blob_invalid" in receipt["source_binding_errors"]


def test_materialized_source_takes_precedence_over_pointer(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write_binding(tmp_path)
    _write(tmp_path, "ARTIFACTS/input/Master.md", b"# authoritative source\n")
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "ACCEPT_MATERIALIZED_CORE"
    assert receipt["source_verification_level"] == "LOCAL_SOURCE_PRESENT"
    assert receipt["authoritative_source_present"] == ["ARTIFACTS/input/Master.md"]
