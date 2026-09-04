from pathlib import Path
from types import SimpleNamespace

from tools.output_identity import build_filename, create_identity, validate_identity


COMMIT = "0123456789abcdef0123456789abcdef01234567"
SHA256 = "a" * 64


def test_build_filename_is_deterministic():
    assert build_filename(
        theme="cost",
        artifact="master review",
        artifact_type="xlsx",
        version="24",
        timestamp_utc="20260831T083100Z",
        source_commit=COMMIT,
        extension="xlsx",
    ) == "QPS__COST__MASTER_REVIEW__XLSX__v24__20260831T083100Z__01234567.xlsx"


def test_create_and_validate_identity(tmp_path: Path):
    artifact = tmp_path / "candidate.xlsx"
    artifact.write_bytes(b"binary-test")
    args = SimpleNamespace(
        artifact_id="ART-COST-MASTER-024",
        theme="COST",
        artifact="MASTER_REVIEW",
        type="XLSX",
        version="v24",
        timestamp="20260831T083100Z",
        source_repository="GBOGEB/cryoplant-project",
        source_commit=COMMIT,
        source_path=["qps-cost-roundtrip/scripts/build_release.py"],
        build_id="BUILD-001",
        ssot_hash=[SHA256],
        evidence_receipt=["EVIDENCE_VERIFICATION_RECEIPT.json"],
        semantic_hash=SHA256,
        previous_release="v23",
        extension="xlsx",
        file=str(artifact),
    )
    identity = create_identity(args)
    data = identity.__dict__.copy()
    assert identity.filename.startswith("QPS__COST__MASTER_REVIEW__XLSX__v24__")
    assert identity.bytes == len(b"binary-test")
    assert not validate_identity(data)


def test_validate_rejects_filename_not_bound_to_identity():
    data = {
        "artifact_id": "ART-1",
        "theme": "COST",
        "artifact": "MASTER_REVIEW",
        "artifact_type": "XLSX",
        "version": "v24",
        "timestamp_utc": "20260831T083100Z",
        "source_repository": "GBOGEB/cryoplant-project",
        "source_commit": COMMIT,
        "source_paths": ["builder.py"],
        "build_id": "BUILD-1",
        "input_ssot_hashes": [SHA256],
        "evidence_receipts": [],
        "filename": "final.xlsx",
    }
    assert "filename_identity_mismatch" in validate_identity(data)


def test_validate_requires_source_path_and_build_id():
    data = {
        "artifact_id": "ART-1",
        "theme": "COST",
        "artifact": "MASTER_REVIEW",
        "artifact_type": "XLSX",
        "version": "v24",
        "timestamp_utc": "20260831T083100Z",
        "source_repository": "GBOGEB/cryoplant-project",
        "source_commit": COMMIT,
        "source_paths": [],
        "build_id": "",
        "input_ssot_hashes": [],
        "evidence_receipts": [],
        "filename": "QPS__COST__MASTER_REVIEW__XLSX__v24__20260831T083100Z__01234567.xlsx",
    }
    errors = validate_identity(data)
    assert "source_paths_empty" in errors
    assert "build_id_empty" in errors
