from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "federation/qps/W331_R2_HIST_BD_034_KEB_FINAL.md"


def review_text() -> str:
    return REVIEW.read_text(encoding="utf-8")


def test_final_keb_binding_uses_canonical_child_merge():
    body = review_text()
    assert "#1651" in body
    assert "082c50516713710b9fbaedc8398b295f164be1a8" in body
    assert "4158da2e6fd77d660e5bb9496fb7c417f316904c" in body


def test_final_keb_binding_preserves_semantic_guards():
    body = review_text()
    assert "protected or signed owner provenance" in body
    assert "farthest user toward QRB/QDB" in body
    assert "Source-bound zero flow remains valid" in body
    assert "abs(residual) <= tolerance" in body
    assert "Machine epsilon is used only" in body


def test_final_keb_binding_cannot_promote_child_authority():
    body = review_text()
    assert "Authority transfer is false" in body
    assert "QPS #923 remains independent" in body
    assert "Perpetuate — PROVISIONAL" in body
