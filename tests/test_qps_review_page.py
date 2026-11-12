"""The QPS lineage review page is generated from the review YAML records and kept current."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEM = REPO_ROOT / "docs/qps-slide-system"


def _builder():
    spec = importlib.util.spec_from_file_location("build_qps_review_page", REPO_ROOT / "tools/build_qps_review_page.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_review_page_is_current():
    builder = _builder()
    assert builder.stale_outputs(builder.render_all()) == [], "regenerate: python tools/build_qps_review_page.py"


def test_hand_edit_is_detected(monkeypatch, tmp_path):
    builder = _builder()
    outputs = builder.render_all()
    edited = tmp_path / builder.REVIEW_PATH
    edited.parent.mkdir(parents=True)
    edited.write_text(outputs[builder.REVIEW_PATH].replace("</h1>", " (hand edit)</h1>"), encoding="utf-8")
    monkeypatch.setattr(builder, "SYSTEM", tmp_path)
    assert builder.stale_outputs(outputs) == [builder.REVIEW_PATH]
    monkeypatch.setattr(builder, "render_all", lambda: outputs)
    assert builder.main(["--check"]) == 1
    assert builder.main([]) == 0
    assert builder.main(["--check"]) == 0


def test_render_is_deterministic():
    builder = _builder()
    assert builder.render_all() == builder.render_all()


def test_every_review_record_is_on_the_page_side_by_side():
    builder = _builder()
    page = (SYSTEM / builder.REVIEW_PATH).read_text(encoding="utf-8")
    assert "placeholder" not in page
    for review in builder.load_reviews():
        section = page.split(f'<section class="review" id="{review["stem"]}">', 1)[1].split("</section>", 1)[0]
        source, curated = section.split("<h3>Source slide</h3>", 1)[1].split("<h3>Curated slide</h3>", 1)
        assert review["source_slide"] in source and review["curated_slide"] in curated
        for item in [*review["comments"], *review["lineage"]]:
            assert str(item) in section
        for obj in review["extracted_objects"]:
            assert str(next(iter(obj.values()))) in section


def test_slides_and_objects_link_to_node_pages():
    builder = _builder()
    page = builder.render_all()[builder.REVIEW_PATH]
    # sbsbw01: SBSBW.01.* is listed by node QPS; QPLANT.WCS is a node record.
    assert '<a href="node/qps.html">QPS</a>' in page
    assert '<a href="node/wcs.html">QPLANT.WCS</a>' in page


def test_every_relative_link_resolves():
    builder = _builder()
    page = SYSTEM / builder.REVIEW_PATH
    for href in re.findall(r'href="([^"#:]+)"', page.read_text(encoding="utf-8")):
        assert (page.parent / href).resolve().exists(), f"broken link {href}"


def _write_reviews(tmp_path: Path, records: dict[str, dict]) -> Path:
    reviews_dir = tmp_path / "lineage"
    reviews_dir.mkdir()
    for stem, record in records.items():
        base = {
            "source_slide": "S.original", "curated_slide": "S.curated", "reviewer": "r", "status": "draft",
            "comments": [], "extracted_objects": [], "lineage": [],
        }
        (reviews_dir / f"{stem}.review.yaml").write_text(yaml.safe_dump({"review": {**base, **record}}), encoding="utf-8")
    return reviews_dir


@pytest.mark.parametrize(
    ("record", "message"),
    [
        ({"comments": "one comment"}, "'comments' must be a list"),
        ({"status": ""}, "'status' must be a non-empty string"),
        ({"extracted_objects": [{"node": "QPS", "subsystem": "X"}]}, "must be a one-key mapping"),
        ({"extracted_objects": ["QPS"]}, "must be a one-key mapping"),
    ],
)
def test_invalid_records_fail_closed(tmp_path, record, message):
    builder = _builder()
    with pytest.raises(builder.ReviewError, match=re.escape(message)):
        builder.load_reviews(_write_reviews(tmp_path, {"a": record}), builder.SCHEMA)


def test_missing_key_and_empty_dir_fail_closed(tmp_path):
    builder = _builder()
    reviews_dir = tmp_path / "lineage"
    reviews_dir.mkdir()
    with pytest.raises(builder.ReviewError, match="no review records"):
        builder.load_reviews(reviews_dir, builder.SCHEMA)
    (reviews_dir / "a.review.yaml").write_text(yaml.safe_dump({"review": {"source_slide": "S"}}), encoding="utf-8")
    with pytest.raises(builder.ReviewError, match="missing keys"):
        builder.load_reviews(reviews_dir, builder.SCHEMA)
