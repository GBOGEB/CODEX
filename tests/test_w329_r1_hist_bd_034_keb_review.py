from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "federation/qps/W329_R1_HIST_BD_034_KEB_REVIEW.md"


def text() -> str:
    return REVIEW.read_text(encoding="utf-8")


def test_w329_keb_binds_exact_child_candidate_head():
    body = text()
    assert "GBOGEB/cryoplant-project" in body
    assert "#1650" in body
    assert "9ac6748a806ac7e260b37e1c9d95401670eed9d2" in body


def test_w329_keb_preserves_bt2_source_semantics():
    body = text()
    assert "minimum populations" in body
    assert "farthest user toward QRB/QDB" in body
    assert "Source-bound zero flow remains admissible" in body
    assert "abs(residual) <= tolerance" in body
    assert "Machine epsilon is confined" in body


def test_w329_keb_preserves_authority_boundary():
    body = text()
    assert "Authority transfer: false" in body
    assert "Formal credit delta: 0" in body
    assert "QPS #923 remains an independent" in body
    assert "Perpetuate — HOLD until final binding" in body
