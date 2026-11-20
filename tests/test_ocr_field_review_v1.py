"""Generic OCR field controls; real recognition is a separate qualification."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evidence import ocr_field_review_v1 as f
from src.evidence.ocr_evidence_runtime_v1 import OCREvidenceRuntime


def digest(data):
    return hashlib.sha256(data).hexdigest()


def setup(tmp_path, text="06.03.2024"):
    parent = tmp_path / "parent.png"
    im = Image.new("RGB", (240, 80), "white")
    ImageDraw.Draw(im).text((20, 20), "Generic 73Q", fill="black")
    im.save(parent)
    sha = digest(parent.read_bytes())
    region = f.make_region(
        source_sha256=sha,
        page_1based=1,
        parent_raster_sha256=sha,
        bbox_xyxy=[10, 10, 220, 60],
    )
    png, crop = f.crop_region(parent, region, scale=2)
    raster = tmp_path / "crop.png"
    raster.write_bytes(png)
    runtime = OCREvidenceRuntime()
    asset = runtime.asset_from_path(parent)
    side = runtime.record_execution(
        asset,
        runtime.decide_ocr(asset),
        page_1based=1,
        raster_path=raster,
        text=text,
        engine="tesseract",
        engine_version="synthetic-fixture",
        requested_languages=["eng"],
        available_languages=["eng"],
        model_sha256s={"eng": "a" * 64},
        parameters={"psm": 7},
    )
    runtime.build_lineage(asset, side)
    observation = f.bind_observation(
        region, crop_receipt=crop, execution=side.execution, text=text
    )
    ref = f.make_reference(
        region,
        field="date",
        text="06.03.2024",
        reviewer="synthetic-reviewer",
        basis="ASSISTANT_VISUAL_TRANSCRIPTION",
    )
    return parent, region, crop, side.execution, observation, ref


def test_crop_replays_and_parent_is_immutable(tmp_path):
    parent, region, crop, *_ = setup(tmp_path)
    before = parent.read_bytes()
    png, replay = f.crop_region(parent, region, scale=2)
    assert crop == replay and digest(png) == crop["crop_sha256"]
    assert parent.read_bytes() == before


def test_region_identity_changes_for_occurrence_and_bounds(tmp_path):
    _, region, *_ = setup(tmp_path)
    kwargs = {
        k: region[k]
        for k in ("source_sha256", "page_1based", "parent_raster_sha256", "bbox_xyxy")
    }
    mutations = [
        {"source_sha256": "1" * 64},
        {"page_1based": 2},
        {"parent_raster_sha256": "2" * 64},
        {"bbox_xyxy": [11, 10, 220, 60]},
    ]
    ids = [f.make_region(**{**kwargs, **m})["region_id"] for m in mutations]
    assert len(set(ids)) == 4 and region["region_id"] not in ids


@pytest.mark.parametrize(
    "bbox", [[0, 0, 0, 2], [False, 0, 1, 2], [-1, 0, 1, 2], [0, 0, 2], [0, 0, 1.1, 2]]
)
def test_invalid_region_bounds_rejected(bbox):
    with pytest.raises(ValueError):
        f.make_region(
            source_sha256="a" * 64,
            page_1based=1,
            parent_raster_sha256="b" * 64,
            bbox_xyxy=bbox,
        )


@pytest.mark.parametrize(
    "change",
    [
        {"scale": True},
        {"scale": 0},
        {"scale": 9},
        {"border": -1},
        {"contrast": "expected-answer"},
    ],
)
def test_unsupported_transform_rejected(tmp_path, change):
    parent, region, *_ = setup(tmp_path)
    with pytest.raises(ValueError):
        f.crop_region(parent, region, **change)


def test_parent_replacement_and_escaping_crop_rejected(tmp_path):
    parent, region, *_ = setup(tmp_path)
    large = f.make_region(
        source_sha256=region["source_sha256"],
        page_1based=1,
        parent_raster_sha256=region["parent_raster_sha256"],
        bbox_xyxy=[0, 0, 241, 80],
    )
    with pytest.raises(ValueError, match="beyond"):
        f.crop_region(parent, large)
    parent.write_bytes(b"changed")
    with pytest.raises(ValueError, match="digest"):
        f.crop_region(parent, region)


def test_matching_reference_does_not_grant_authority(tmp_path):
    *_, obs, ref = setup(tmp_path)
    result = f.qualify_field(ref, [obs])
    assert result["state"] == "ALL_CONFIGURATIONS_MATCH"
    assert result["authority_effect"] == "NONE"
    assert not result["independent_engine_corroboration"]
    assert not result["automatic_source_rewrite"]


@pytest.mark.parametrize(
    "text", ["08.03.2024", "106.03.2024", "06.03.2024 extra", "06.O3.2024"]
)
def test_wrong_digit_substring_and_extra_text_never_pass(tmp_path, text):
    *_, obs, ref = setup(tmp_path, text)
    assert f.qualify_field(ref, [obs])["state"] == "NO_CONFIGURATION_MATCH"


def test_empty_execution_is_not_success(tmp_path):
    *_, ref = setup(tmp_path)
    result = f.qualify_field(ref, [])
    assert result["state"] == "NOT_EXECUTED" and result["configurations"] == 0


def test_duplicate_cache_cannot_inflate_configuration_count(tmp_path):
    *_, obs, ref = setup(tmp_path)
    with pytest.raises(ValueError, match="duplicate OCR"):
        f.qualify_field(ref, [obs, copy.deepcopy(obs)])


def test_changed_occurrence_cannot_borrow_a_result(tmp_path):
    _, region, crop, execution, *_ = setup(tmp_path)
    new = f.make_region(
        source_sha256=region["source_sha256"],
        page_1based=2,
        parent_raster_sha256=region["parent_raster_sha256"],
        bbox_xyxy=region["bbox_xyxy"],
    )
    with pytest.raises(ValueError, match="crop receipt"):
        f.bind_observation(
            new, crop_receipt=crop, execution=execution, text="06.03.2024"
        )


def test_edited_execution_text_and_rehashed_parameters_fail(tmp_path):
    _, region, crop, execution, *_ = setup(tmp_path)
    with pytest.raises(ValueError, match="does not bind"):
        f.bind_observation(
            region, crop_receipt=crop, execution=execution, text="08.03.2024"
        )
    execution["parameters"]["psm"] = 8
    body = {k: v for k, v in execution.items() if k != "execution_binding_sha256"}
    execution["execution_binding_sha256"] = digest(
        json.dumps(
            body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    )
    with pytest.raises(ValueError, match="fingerprint"):
        f.bind_observation(
            region, crop_receipt=crop, execution=execution, text="06.03.2024"
        )


def test_mutated_observation_or_reference_is_rejected(tmp_path):
    *_, obs, ref = setup(tmp_path)
    obs["text_verbatim"] = "08.03.2024"
    with pytest.raises(ValueError):
        f.qualify_field(ref, [obs])
    ref["acceptance_approval"] = True
    with pytest.raises(ValueError, match="reference identity"):
        f.qualify_field(ref, [])


def test_unicode_normalization_keeps_diacritics_and_confusables():
    assert f.normalize_transcription("Cafe\u0301\n  12") == "Café 12"
    assert f.normalize_transcription("Café") != f.normalize_transcription("Cafe")
    assert f.normalize_transcription("73Q") != f.normalize_transcription("730")


def test_crop_transform_changes_result_identity(tmp_path):
    parent, region, crop, *_ = setup(tmp_path)
    _, other = f.crop_region(parent, region, scale=2, contrast="autocontrast")
    assert other["recipe_sha256"] != crop["recipe_sha256"]
    assert other["region"] == crop["region"]


def test_bound_observation_is_detached_from_caller(tmp_path):
    _, _, crop, execution, obs, _ = setup(tmp_path)
    crop["region"]["bbox_xyxy"][0] = 999
    execution["parameters"]["psm"] = 99
    assert obs["crop_receipt"]["region"]["bbox_xyxy"][0] == 10
    assert obs["execution"]["parameters"]["psm"] == 7


def test_wrong_container_types_are_explicit(tmp_path):
    _, region, crop, execution, obs, ref = setup(tmp_path)
    with pytest.raises(TypeError, match="region must"):
        f.validate_region(None)
    with pytest.raises(TypeError, match="crop and execution"):
        f.bind_observation(region, crop_receipt=None, execution=execution, text="x")
    execution["model_sha256s"] = None
    with pytest.raises(TypeError, match="models"):
        f.bind_observation(region, crop_receipt=crop, execution=execution, text="x")
    with pytest.raises(TypeError, match="reference and"):
        f.qualify_field(ref, None)
    with pytest.raises(TypeError, match="observation must"):
        f.qualify_field(ref, [None])
    with pytest.raises(TypeError, match="transcription text"):
        f.bind_observation(
            region, crop_receipt=crop, execution=obs["execution"], text=None
        )
