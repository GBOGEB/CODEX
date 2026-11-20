"""Source-bound regions and explicit field review for subordinate OCR evidence.

This module neither runs OCR nor grants document or engineering authority.
It binds a replayable crop to a source occurrence and compares actual OCR
text with an explicitly attributed transcription. Configuration agreement
is not independent-engine corroboration, and a transcription is not an
approval of the document's content, date of effect, or authenticity.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path

_DIGEST = re.compile(r"[0-9a-f]{64}")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{label} must be a SHA256 digest")
    return value


def _integer(value: object, lower: int, upper: int, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not lower <= value <= upper
    ):
        raise ValueError(f"{label} must be an integer in [{lower}, {upper}]")
    return value


def make_region(
    *,
    source_sha256: str,
    page_1based: int,
    parent_raster_sha256: str,
    bbox_xyxy: list[int],
) -> dict:
    """A physical occurrence, never a document ID inferred from an OCR string.

    Parent raster to PDF association still requires a source-render replay by
    the executor. Equal image pixels do not collapse distinct source pages.
    """
    _digest(source_sha256, "source")
    _digest(parent_raster_sha256, "parent raster")
    _integer(page_1based, 1, 1_000_000, "physical page")
    if not isinstance(bbox_xyxy, list) or len(bbox_xyxy) != 4:
        raise ValueError("region bbox must contain four pixel coordinates")
    for n in bbox_xyxy:
        _integer(n, 0, 1_000_000, "pixel coordinate")
    x0, y0, x1, y1 = bbox_xyxy
    if x1 <= x0 or y1 <= y0:
        raise ValueError("region must have positive width and height")
    value = {
        "schema": "ocr-field-region/1",
        "source_sha256": source_sha256,
        "page_1based": page_1based,
        "parent_raster_sha256": parent_raster_sha256,
        "bbox_xyxy": list(bbox_xyxy),
        "coordinate_frame": "ORIGINAL_PARENT_PIXELS",
    }
    return {**value, "region_id": _hash(_canonical(value))}


def validate_region(region: dict) -> dict:
    if not isinstance(region, dict):
        raise TypeError("region must be a mapping")
    expected = make_region(
        source_sha256=region.get("source_sha256"),
        page_1based=region.get("page_1based"),
        parent_raster_sha256=region.get("parent_raster_sha256"),
        bbox_xyxy=region.get("bbox_xyxy"),
    )
    if region != expected:
        raise ValueError("region identity or schema mismatch")
    return expected


def crop_region(
    parent_path: Path,
    region: dict,
    *,
    scale: int = 1,
    border: int = 16,
    contrast: str = "original",
) -> tuple[bytes, dict]:
    """Derive, hash and describe a bounded crop without modifying its parent.

    Only original pixels or deterministic grayscale autocontrast are supported.
    No text replacement, expected-answer whitelist, sharpening, or inpainting.
    """
    from PIL import Image, ImageOps
    from PIL import __version__ as pillow_version

    region = validate_region(region)
    _integer(scale, 1, 8, "scale")
    _integer(border, 0, 256, "white border")
    if contrast not in ("original", "autocontrast"):
        raise ValueError("unsupported contrast method")
    data = Path(parent_path).read_bytes()
    if _hash(data) != region["parent_raster_sha256"]:
        raise ValueError("parent raster digest mismatch")
    with Image.open(io.BytesIO(data)) as parent:
        if getattr(parent, "n_frames", 1) != 1:
            raise ValueError("only a single-frame parent is supported")
        x0, y0, x1, y1 = region["bbox_xyxy"]
        if x1 > parent.width or y1 > parent.height:
            raise ValueError("region extends beyond parent raster")
        width, height = (x1 - x0) * scale + 2 * border, (y1 - y0) * scale + 2 * border
        if width * height > 32_000_000:
            raise ValueError("derived crop exceeds the pixel budget")
        image = parent.convert("RGB").crop((x0, y0, x1, y1))
        parent_size = [parent.width, parent.height]
    if contrast == "autocontrast":
        image = ImageOps.autocontrast(image.convert("L"), cutoff=0)
    if scale != 1:
        image = image.resize(
            (image.width * scale, image.height * scale), Image.Resampling.LANCZOS
        )
    image = ImageOps.expand(image, border=border, fill="white")
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=False)
    png = output.getvalue()
    recipe = {
        "schema": "ocr-field-crop/1",
        "region": region,
        "parent_size": parent_size,
        "scale": scale,
        "white_border": border,
        "contrast": contrast,
        "resampler": "PIL_LANCZOS" if scale != 1 else "NONE",
        "implementation": "Pillow",
        "implementation_version": pillow_version,
        "crop_size": [image.width, image.height],
        "crop_sha256": _hash(png),
        "source_render_association": "EXECUTOR_REPLAY_REQUIRED",
        "authority_effect": "NONE",
    }
    recipe["recipe_sha256"] = _hash(_canonical(recipe))
    return png, recipe


def normalize_transcription(text: str) -> str:
    """Only NFC and whitespace; never repair digits, dates or diacritics."""
    if not isinstance(text, str):
        raise TypeError("transcription text must be a string")
    return " ".join(unicodedata.normalize("NFC", text).split())


def make_reference(
    region: dict,
    *,
    field: str,
    text: str,
    reviewer: str,
    basis: str,
) -> dict:
    region = validate_region(region)
    if not all(isinstance(v, str) and v.strip() for v in (field, reviewer)):
        raise ValueError("field and attributed reviewer are required")
    if basis not in ("ASSISTANT_VISUAL_TRANSCRIPTION", "OWNER_SUPPLIED_TRANSCRIPTION"):
        raise ValueError("reference basis must identify the transcription source")
    if not normalize_transcription(text):
        raise ValueError("reference text must not be empty")
    ref = {
        "schema": "ocr-field-reference/1",
        "region": region,
        "field": field,
        "text_verbatim": text,
        "reviewer": reviewer,
        "basis": basis,
        "authority_effect": "NONE",
        "acceptance_approval": False,
    }
    return {**ref, "reference_sha256": _hash(_canonical(ref))}


def bind_observation(
    region: dict,
    *,
    crop_receipt: dict,
    execution: dict,
    text: str,
) -> dict:
    """Bind an existing runtime execution receipt to a crop and field region.

    Structural binding and the existing runtime fingerprint are checked here;
    executor authenticity remains outside a caller-created JSON receipt.
    This function does not perform OCR or replay a PDF rendering.
    """
    region = validate_region(region)
    normalize_transcription(text)
    if not isinstance(crop_receipt, dict) or not isinstance(execution, dict):
        raise TypeError("crop and execution receipts are required")
    from .ocr_evidence_runtime_v1 import OCREvidenceRuntime

    models = execution.get("model_sha256s")
    if not isinstance(models, dict):
        raise TypeError("OCR execution models are required")
    fingerprint = OCREvidenceRuntime.execution_fingerprint(
        raster_sha256=execution.get("raster_sha256"),
        engine=execution.get("engine"),
        engine_version=execution.get("engine_version"),
        requested_languages=execution.get("requested_languages"),
        available_languages=list(models),
        model_sha256s=models,
        parameters=execution.get("parameters"),
    )
    if any(execution.get(k) != v for k, v in fingerprint.items()):
        raise ValueError("OCR execution fingerprint mismatch")
    _integer(execution.get("page_1based"), 1, 1_000_000, "execution physical page")
    crop = {k: v for k, v in crop_receipt.items() if k != "recipe_sha256"}
    if (
        crop.get("schema") != "ocr-field-crop/1"
        or crop_receipt.get("recipe_sha256") != _hash(_canonical(crop))
        or crop.get("region") != region
        or crop.get("authority_effect") != "NONE"
    ):
        raise ValueError("crop receipt or region binding mismatch")
    _digest(crop.get("crop_sha256"), "crop")
    body = {k: v for k, v in execution.items() if k != "execution_binding_sha256"}
    if (
        execution.get("execution_binding_sha256") != _hash(_canonical(body))
        or execution.get("source_sha256") != region["source_sha256"]
        or execution.get("page_1based") != region["page_1based"]
        or execution.get("raster_sha256") != crop["crop_sha256"]
        or execution.get("text_sha256") != _hash(text.encode("utf-8"))
        or execution.get("state") != "EXECUTED_DERIVED_UNVERIFIED"
        or execution.get("authority_effect") != "NONE"
    ):
        raise ValueError("OCR execution does not bind this source, page, crop and text")
    _digest(execution.get("cache_key_sha256"), "execution key")
    row = {
        "schema": "ocr-field-observation/1",
        "region_id": region["region_id"],
        "crop_receipt": copy.deepcopy(crop_receipt),
        "execution": copy.deepcopy(execution),
        "text_verbatim": text,
        "text_sha256": _hash(text.encode("utf-8")),
        "authority_effect": "NONE",
    }
    return {**row, "observation_sha256": _hash(_canonical(row))}


def qualify_field(reference: dict, observations: list[dict]) -> dict:
    """Report disagreement and per-configuration equality, without voting.

    A match is equality of the complete transcribed region after NFC/whitespace
    normalization. A longer number containing a desired substring cannot pass.
    Duplicate cached results cannot inflate the evaluated configuration count.
    """
    if not isinstance(reference, dict) or not isinstance(observations, list):
        raise TypeError("reference and observation list are required")
    expected = make_reference(
        reference.get("region"),
        field=reference.get("field"),
        text=reference.get("text_verbatim"),
        reviewer=reference.get("reviewer"),
        basis=reference.get("basis"),
    )
    if reference != expected:
        raise ValueError("reference identity or authority scope mismatch")
    seen = set()
    rows = []
    for observation in observations:
        if not isinstance(observation, dict):
            raise TypeError("observation must be a mapping")
        bound = bind_observation(
            reference["region"],
            crop_receipt=observation.get("crop_receipt"),
            execution=observation.get("execution"),
            text=observation.get("text_verbatim"),
        )
        if observation != bound:
            raise ValueError("observation identity mismatch")
        key = observation["execution"]["cache_key_sha256"]
        if key in seen:
            raise ValueError("duplicate OCR execution configuration")
        seen.add(key)
        rows.append(
            {
                "observation_sha256": observation["observation_sha256"],
                "execution_key": key,
                "text_verbatim": observation["text_verbatim"],
                "exact_match": normalize_transcription(observation["text_verbatim"])
                == normalize_transcription(reference["text_verbatim"]),
            }
        )
    matches = sum(row["exact_match"] for row in rows)
    state = (
        "NOT_EXECUTED"
        if not rows
        else (
            "ALL_CONFIGURATIONS_MATCH"
            if matches == len(rows)
            else (
                "CONFIGURATION_DEPENDENT_MATCH" if matches else "NO_CONFIGURATION_MATCH"
            )
        )
    )
    result = {
        "schema": "ocr-field-qualification/1",
        "reference_sha256": reference["reference_sha256"],
        "region_id": reference["region"]["region_id"],
        "field": reference["field"],
        "state": state,
        "configurations": len(rows),
        "matching_configurations": matches,
        "distinct_normalized_readings": sorted(
            {normalize_transcription(r["text_verbatim"]) for r in rows}
        ),
        "observations": rows,
        "comparison": "WHOLE_REGION_NFC_WHITESPACE_EQUALITY",
        "review_reference_basis": reference["basis"],
        "authority_effect": "NONE",
        "independent_engine_corroboration": False,
        "automatic_source_rewrite": False,
    }
    return {**result, "qualification_sha256": _hash(_canonical(result))}
