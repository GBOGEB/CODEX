from __future__ import annotations

from pathlib import Path

from receipt_validation import SNAPSHOT, load_and_validate
from snapshot_promotion import evaluate


def test_snapshot_receipt_accepts_real_png() -> None:
    receipt = load_and_validate()
    assert receipt["decision"] == "accept"
    assert receipt["checks"]["dimensions"]["pass"] is True
    assert receipt["checks"]["clipping"]["pass"] is True
    assert receipt["checks"]["viewport_overflow"]["pass"] is True
    assert receipt["checks"]["text_visibility"]["pass"] is True
    assert receipt["checks"]["contrast"]["pass"] is True
    assert receipt["checks"]["element_coverage"]["pass"] is True
    assert receipt["checks"]["semantic_parity"]["pass"] is True


def test_snapshot_hash_tamper_is_rejected() -> None:
    original = SNAPSHOT.read_bytes()
    try:
        SNAPSHOT.write_bytes(original + b"tamper")
        try:
            load_and_validate()
        except ValueError as exc:
            assert "content-address validation failed" in str(exc)
        else:
            raise AssertionError("tampered snapshot was accepted")
    finally:
        SNAPSHOT.write_bytes(original)


def test_six_surface_promotion() -> None:
    result = evaluate()
    assert result["decision"] == "PROMOTE"
    assert "snapshot_png" in result["surfaces"]
    assert len(result["surfaces"]) >= 6
    assert all(result["checks"].values())


if __name__ == "__main__":
    test_snapshot_receipt_accepts_real_png()
    test_snapshot_hash_tamper_is_rejected()
    test_six_surface_promotion()
    print("A10 snapshot receipt tests: PASS")
