from pathlib import Path

from scripts.gmi_doceng_bridge_guard import CORE_PATHS, build_receipt


CLI_BYTES = b"print('bridge')\n"


def _write(root: Path, rel: str, data: bytes = b"x") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _seed_core(root: Path) -> str:
    import hashlib

    for rel in CORE_PATHS:
        _write(root, rel, CLI_BYTES if rel == "ARTIFACTS/cli.py" else b"x")
    return hashlib.sha256(CLI_BYTES).hexdigest()


def test_rejects_missing_core(tmp_path: Path) -> None:
    receipt = build_receipt(tmp_path, "0" * 64)
    assert receipt["disposition"] == "REJECT"
    assert receipt["missing_core_paths"]


def test_defers_when_core_valid_but_authoritative_source_missing(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "DEFER_SOURCE_BINDING"
    assert receipt["cli_hash_match"] is True


def test_accepts_materialized_core_when_source_is_bound(tmp_path: Path) -> None:
    cli_sha = _seed_core(tmp_path)
    _write(tmp_path, "ARTIFACTS/input/Master.md", b"# authoritative source\n")
    receipt = build_receipt(tmp_path, cli_sha)
    assert receipt["disposition"] == "ACCEPT_MATERIALIZED_CORE"
    assert receipt["authoritative_source_present"] == ["ARTIFACTS/input/Master.md"]
