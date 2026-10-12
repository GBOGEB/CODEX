from __future__ import annotations

from pathlib import Path

from renderers.regression.html_baseline_compare import (
    HtmlBaselineComparator,
    compare_signatures,
    semantic_signature,
)

BASELINE = """<!doctype html>
<html><head><title>T</title><style>h1 { color: #ff0000; }</style></head>
<body>
  <h1>Render  QA</h1>
  <p style="color: #112233; margin: 0">Hello world</p>
  <a href="page.html#section">Link</a>
  <script>var hidden = "not visible text";</script>
</body></html>
"""


def _write(tmp_path: Path, name: str, html: str) -> Path:
    path = tmp_path / name
    path.write_text(html, encoding="utf-8")
    return path


def test_signature_extracts_semantic_features() -> None:
    sig = semantic_signature(BASELINE)

    assert sig["headings"] == ["Render QA"]
    assert sig["heading_count"] == 1
    # Fragment identifiers are stripped from links.
    assert sig["links"] == ["page.html"]
    assert sig["link_count"] == 1
    assert sig["color_tokens"] == ["color: #112233"]
    assert sig["tag_counts"]["h1"] == 1
    # Text inside <script>/<style> is not counted as visible text.
    # Words: T, Render, QA, Hello, world, Link.
    assert sig["visible_text_word_count"] == 6


def test_identical_files_are_byte_and_semantic_identical(tmp_path: Path) -> None:
    baseline = _write(tmp_path, "baseline.html", BASELINE)
    candidate = _write(tmp_path, "candidate.html", BASELINE)

    result = HtmlBaselineComparator().compare(str(baseline), str(candidate))

    assert result.identical is True
    assert result.semantic_identical is True
    assert result.deltas == {}


def test_whitespace_only_change_is_semantic_identical(tmp_path: Path) -> None:
    reformatted = BASELINE.replace("\n  ", "\n\n      ")
    baseline = _write(tmp_path, "baseline.html", BASELINE)
    candidate = _write(tmp_path, "candidate.html", reformatted)

    result = HtmlBaselineComparator().compare(str(baseline), str(candidate))

    assert result.identical is False
    assert result.semantic_identical is True


def test_semantic_change_is_reported_in_deltas(tmp_path: Path) -> None:
    changed = BASELINE.replace("Render  QA", "Render Review").replace(
        "page.html", "other.html"
    )
    baseline = _write(tmp_path, "baseline.html", BASELINE)
    candidate = _write(tmp_path, "candidate.html", changed)

    result = HtmlBaselineComparator().compare(str(baseline), str(candidate))

    assert result.semantic_identical is False
    assert result.deltas is not None
    assert result.deltas["headings"] == {
        "baseline": ["Render QA"],
        "candidate": ["Render Review"],
    }
    assert result.deltas["links"] == {
        "baseline": ["page.html"],
        "candidate": ["other.html"],
    }


def test_compare_signatures_only_reports_changed_keys() -> None:
    sig = semantic_signature(BASELINE)
    other = dict(sig, color_tokens=["color: #000000"])

    assert compare_signatures(sig, sig) == {}
    assert set(compare_signatures(sig, other)) == {"color_tokens"}
