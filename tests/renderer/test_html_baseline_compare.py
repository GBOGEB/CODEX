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


def test_nested_markup_inside_hidden_tags_is_not_visible_text() -> None:
    sig = semantic_signature(
        "<p>shown</p><noscript><p>fallback text</p><br></noscript><p>also</p>"
    )

    assert sig["visible_text_word_count"] == 2


def test_void_elements_do_not_misalign_hidden_text_tracking() -> None:
    sig = semantic_signature("<p>a<br>b<img src='x.png'></p><style>p{}</style><p>c</p>")

    assert sig["visible_text_word_count"] == 3


def test_whitespace_at_inline_boundaries_is_preserved() -> None:
    joined = semantic_signature("<h1>foo<span>bar</span></h1>")
    spaced = semantic_signature("<h1>foo <span>bar</span></h1>")

    assert joined["headings"] == ["foobar"]
    assert spaced["headings"] == ["foo bar"]
    assert compare_signatures(joined, spaced).keys() >= {"headings"}


def test_block_boundaries_separate_words() -> None:
    sig = semantic_signature("<div><p>one</p><p>two</p></div>")

    assert sig["visible_text_word_count"] == 2


def test_named_and_functional_inline_colors_are_tracked() -> None:
    red = semantic_signature('<p style="color: red; margin: 0">x</p>')
    blue = semantic_signature('<p style="color: blue; margin: 0">x</p>')
    rgb = semantic_signature('<p style="background-color: rgb(1, 2, 3)">x</p>')

    assert red["color_tokens"] == ["color: red"]
    assert rgb["color_tokens"] == ["background-color: rgb(1, 2, 3)"]
    assert set(compare_signatures(red, blue)) == {"color_tokens"}


def test_color_token_count_change_is_a_delta() -> None:
    one = semantic_signature('<p style="color:#fff">a</p><p>b</p>')
    both = semantic_signature('<p style="color:#fff">a</p><p style="color:#fff">b</p>')

    assert set(compare_signatures(one, both)) == {"color_token_count"}
