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

VALID_DOCUMENT_CORE_RECEIPT = {
    "schema": "qps.gmi_doceng.document_core_reentry_provider_proof/v1",
    "wave": "GMI-W275",
    "parent_qps_w274_merge_sha": "34f04bf08dc2f957f196f33ea1d73ae1a5b07070",
    "canonical_input": {
        "expected_sha256": "5bed44a7ae2c0bcbd875e1162cdde292a7d9c8dc717e7328cf4a6d6f0cc13051",
        "observed_sha256": "5bed44a7ae2c0bcbd875e1162cdde292a7d9c8dc717e7328cf4a6d6f0cc13051",
        "source_sha256": "ac6627f0a6cbe8c020941686cad249619184d8071a9efca721d0c960d41d63c9",
        "expected_record_count": 2692,
        "observed_record_count": 2692,
    },
    "document_core": {
        "schema": "gmi.document_core.requirements/v1",
        "record_count": 2692,
        "section_path_count": 218,
        "semantic_sha256": "0feff7dea41f274f44d4150c6e0ce8706df0f0b4def24fe33856cd6cea78a0be",
    },
    "checks": {
        "canonical_identity": "PASS",
        "population_identity": "PASS",
        "requirement_local_shape": "PASS",
        "deterministic_normalization": "PASS",
        "llm_invoked": False,
        "source_or_requirement_mutation": False,
        "canonical_lock_or_tag_performed": False,
    },
    "disposition": "ACCEPT_DOCUMENT_CORE_INGRESS_ONLY",
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


def _write_document_core_receipt(
    root: Path, payload: dict = VALID_DOCUMENT_CORE_RECEIPT
) -> None:
    path = root / "PROOFS/W275_DOCUMENT_CORE_REENTRY/w275_gmi_document_core_receipt.json"
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


def test_accepts_valid_document_core_provider_proof(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write_binding(tmp_path)
    _write_document_core_receipt(tmp_path)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "ACCEPT_DOCUMENT_CORE_PROVIDER_PROOF_BOUND"
    assert receipt["document_core_receipt_valid"] is True
    assert receipt["source_verification_level"] == "PROVIDER_BYTE_VERIFIED_DOCUMENT_CORE_INGRESS"
    assert (
        receipt["document_core_receipt"]["document_core"]["semantic_sha256"]
        == VALID_DOCUMENT_CORE_RECEIPT["document_core"]["semantic_sha256"]
    )


def test_rejects_document_core_proof_without_source_binding(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write_document_core_receipt(tmp_path)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "REJECT"
    assert "valid_source_binding_required" in receipt["document_core_receipt_errors"]


def test_rejects_document_core_semantic_sha_mismatch(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write_binding(tmp_path)
    malformed = json.loads(json.dumps(VALID_DOCUMENT_CORE_RECEIPT))
    malformed["document_core"]["semantic_sha256"] = "0" * 64
    _write_document_core_receipt(tmp_path, malformed)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "REJECT"
    assert "document_core_semantic_sha_invalid" in receipt["document_core_receipt_errors"]
