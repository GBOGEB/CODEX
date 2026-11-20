"""
Wave 15 — OCR Orchestration & Engineering Evidence Runtime.

This module implements the first executable policy layer for deciding when OCR
is allowed, how OCR output is governed, and how engineering evidence lineage is
preserved.

Core rule:
    evidence image/vector/document remains primary;
    OCR is a subordinate sidecar unless explicitly promoted by validation.
"""

from __future__ import annotations

import copy
import csv
import io
import json
import math
import re
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from hashlib import sha256
from pathlib import Path


class EvidenceFormat(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    SVG = "svg"
    PPTX = "pptx"
    VSDX = "vsdx"
    DRAWIO = "drawio"
    DWG = "dwg"
    HTML = "html"
    UNKNOWN = "unknown"


class OCRDecision(str, Enum):
    SKIP = "skip"
    CONDITIONAL = "conditional"
    REQUIRED = "required"
    DEFER_DWG_RENDER = "defer_dwg_render"


@dataclass
class EvidenceAsset:
    asset_id: str
    path: str
    source_format: EvidenceFormat
    size_bytes: int
    sha256: str
    embedded_text_chars: int = 0
    raster_confidence: float = 0.0
    semantic_vector_confidence: float = 0.0
    notes: list[str] = field(default_factory=list)
    resolved_path: str | None = None


@dataclass
class OCRSidecar:
    asset_id: str
    decision: OCRDecision
    confidence: float
    text_preview: str = ""
    promoted_to_authoritative: bool = False
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    execution: dict | None = None


@dataclass
class EvidenceLineageRecord:
    asset_id: str
    original_path: str
    evidence_primary: bool
    derived_artifacts: list[str] = field(default_factory=list)
    sidecar: OCRSidecar | None = None
    preservation_policy: str = "preserve_full_frame"


class OCREvidenceRuntime:
    """
    Conditional OCR and evidence-lineage engine.

    The runtime does not perform OCR directly. It decides whether OCR should be
    run, stores the governance decision, and preserves the evidence hierarchy.
    OCR executors can be attached later as plugins.
    """

    LOW_TEXT_THRESHOLD = 80
    HIGH_VECTOR_CONFIDENCE = 0.75
    MIN_PROMOTION_CONFIDENCE = 0.92

    @staticmethod
    def parse_tesseract_tsv(text: str) -> list[dict]:
        """Validate the executor's actual format; exit code zero is insufficient.

        A custom tessdata directory may lack the named 'tsv' config file.
        Tesseract can then return plain text despite an otherwise successful
        invocation. Never turn that response into a successful empty parse.
        Confidence is preserved as the engine's raw score, not a probability.
        """
        expected = [
            "level",
            "page_num",
            "block_num",
            "par_num",
            "line_num",
            "word_num",
            "left",
            "top",
            "width",
            "height",
            "conf",
            "text",
        ]
        if not isinstance(text, str):
            raise TypeError("OCR TSV text required")
        reader = csv.DictReader(
            io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE
        )
        if reader.fieldnames != expected:
            raise ValueError("OCR output is not the required Tesseract TSV schema")
        words = []
        pages = {}
        for row in reader:
            if None in row or any(row.get(k) is None for k in expected):
                raise ValueError("truncated or extra-column OCR TSV row")
            try:
                level = int(row["level"])
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid OCR TSV level") from exc
            if level not in range(1, 6):
                raise ValueError("invalid OCR TSV level")
            if level == 1:
                try:
                    page_id = int(row["page_num"])
                    bounds = tuple(
                        int(row[k]) for k in ("left", "top", "width", "height")
                    )
                except (TypeError, ValueError) as exc:
                    raise ValueError("invalid OCR TSV page geometry") from exc
                if (
                    page_id < 1
                    or page_id in pages
                    or min(bounds) < 0
                    or min(bounds[2:]) == 0
                ):
                    raise ValueError("invalid or duplicate OCR TSV page geometry")
                pages[page_id] = bounds
                continue
            if level != 5:
                continue
            try:
                word = {k: int(row[k]) for k in expected[1:10]}
                confidence = float(row["conf"])
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid OCR TSV word geometry or confidence") from exc
            if (
                word["page_num"] < 1
                or any(v < 0 for v in word.values())
                or not math.isfinite(confidence)
                or not -1 <= confidence <= 100
                or (row["text"].strip() and (word["width"] == 0 or word["height"] == 0))
            ):
                raise ValueError("invalid OCR TSV word geometry or confidence")
            bounds = pages.get(word["page_num"])
            if bounds is None or not (
                bounds[0]
                <= word["left"]
                <= word["left"] + word["width"]
                <= bounds[0] + bounds[2]
                and bounds[1]
                <= word["top"]
                <= word["top"] + word["height"]
                <= bounds[1] + bounds[3]
            ):
                raise ValueError("OCR TSV word is outside its declared page")
            if not row["text"].strip():
                continue
            word.update(text=row["text"], confidence_raw=confidence)
            words.append(word)
        if not pages:
            raise ValueError("OCR TSV contains no declared page")
        return words

    def decide_ocr(self, asset: EvidenceAsset) -> OCRSidecar:
        if asset.source_format == EvidenceFormat.DWG:
            return OCRSidecar(
                asset_id=asset.asset_id,
                decision=OCRDecision.DEFER_DWG_RENDER,
                confidence=0.0,
                reason="DWG must be rendered to PDF or high-resolution image before OCR.",
                warnings=["Do not OCR raw DWG directly."],
            )

        if asset.source_format in {
            EvidenceFormat.SVG,
            EvidenceFormat.DRAWIO,
            EvidenceFormat.VSDX,
        }:
            if asset.semantic_vector_confidence >= self.HIGH_VECTOR_CONFIDENCE:
                return OCRSidecar(
                    asset_id=asset.asset_id,
                    decision=OCRDecision.SKIP,
                    confidence=asset.semantic_vector_confidence,
                    reason="Vector semantic text/shape extraction preferred over OCR.",
                )
            return OCRSidecar(
                asset_id=asset.asset_id,
                decision=OCRDecision.CONDITIONAL,
                confidence=asset.semantic_vector_confidence,
                reason="Vector semantics incomplete; OCR may be used as secondary sidecar.",
            )

        if asset.source_format == EvidenceFormat.PDF:
            if asset.embedded_text_chars >= self.LOW_TEXT_THRESHOLD:
                return OCRSidecar(
                    asset_id=asset.asset_id,
                    decision=OCRDecision.SKIP,
                    confidence=0.85,
                    reason="PDF has sufficient embedded text; OCR would increase intrusion risk.",
                )
            return OCRSidecar(
                asset_id=asset.asset_id,
                decision=OCRDecision.REQUIRED,
                confidence=0.65,
                reason="PDF has low embedded text; likely scanned or image-heavy.",
            )

        if asset.source_format == EvidenceFormat.IMAGE:
            return OCRSidecar(
                asset_id=asset.asset_id,
                decision=OCRDecision.CONDITIONAL,
                confidence=asset.raster_confidence,
                reason="Image remains primary evidence; OCR allowed only as collapsible sidecar.",
                warnings=["Never replace image with OCR text."],
            )

        return OCRSidecar(
            asset_id=asset.asset_id,
            decision=OCRDecision.CONDITIONAL,
            confidence=0.5,
            reason="Unknown or mixed format; OCR requires reviewer confirmation.",
        )

    def may_promote_ocr(self, sidecar: OCRSidecar) -> bool:
        """Compatibility gate: OCR confidence never confers source authority.

        A source-bound transcription review may validate selected fields in a
        separate governed workflow. It cannot make this policy runtime the
        approver of document identity, contractual status or engineering truth.
        """
        return False

    def build_lineage(
        self, asset: EvidenceAsset, sidecar: OCRSidecar
    ) -> EvidenceLineageRecord:
        if sidecar.asset_id != asset.asset_id:
            raise ValueError("OCR sidecar belongs to another source asset")
        if sidecar.execution is not None:
            self._validate_execution(asset, sidecar.execution)
        # Do not mutate an earlier observation when creating a derived record.
        bound_sidecar = replace(
            sidecar,
            promoted_to_authoritative=False,
            warnings=list(sidecar.warnings),
            execution=copy.deepcopy(sidecar.execution),
        )
        return EvidenceLineageRecord(
            asset_id=asset.asset_id,
            original_path=asset.path,
            evidence_primary=True,
            derived_artifacts=["ocr_sidecar"] if sidecar.execution is not None else [],
            sidecar=bound_sidecar,
        )

    @staticmethod
    def execution_fingerprint(
        *,
        raster_sha256: str,
        engine: str,
        engine_version: str,
        requested_languages: list[str],
        available_languages: list[str],
        model_sha256s: dict[str, str],
        parameters: dict,
    ) -> dict:
        """Fail closed on absent language models; key every OCR-affecting input.

        Pixel-identical source occurrences may share an OCR result. Their source
        hash and physical page remain separate in record_execution(), never
        inferred from cache reuse. Recognition confidence is not calibrated
        correctness and is deliberately absent from the authority decision.
        """
        digest = re.compile(r"^[0-9a-f]{64}$")
        if not isinstance(raster_sha256, str) or not digest.fullmatch(raster_sha256):
            raise ValueError("raster SHA256 required")
        if not all(isinstance(x, str) and x.strip() for x in (engine, engine_version)):
            raise ValueError("OCR engine and version required")
        if (
            not isinstance(requested_languages, list)
            or not requested_languages
            or not all(
                isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_/-]+", x)
                for x in requested_languages
            )
            or len(set(requested_languages)) != len(requested_languages)
        ):
            raise ValueError("ordered, distinct OCR languages required")
        if not isinstance(available_languages, list) or not all(
            isinstance(x, str) for x in available_languages
        ):
            raise ValueError("available OCR languages must be explicit")
        missing = sorted(set(requested_languages) - set(available_languages))
        if missing:
            raise ValueError("missing OCR languages: " + ", ".join(missing))
        if (
            not isinstance(model_sha256s, dict)
            or not set(requested_languages).issubset(model_sha256s)
            or any(
                not isinstance(k, str)
                or not re.fullmatch(r"[A-Za-z0-9_/-]+", k)
                or not isinstance(v, str)
                or not digest.fullmatch(v)
                for k, v in model_sha256s.items()
            )
        ):
            raise ValueError("exact model SHA256 required for each requested language")
        if not isinstance(parameters, dict):
            raise TypeError("OCR parameters must be a dictionary")
        if "tesseract" in engine.lower():
            psm = parameters.get("psm")
            if isinstance(psm, bool) or not isinstance(psm, int) or not 0 <= psm <= 13:
                raise ValueError(
                    "Tesseract psm must be an explicit integer from 0 to 13"
                )
            if psm in (0, 1, 12) and "osd" not in model_sha256s:
                raise ValueError(
                    "orientation detection requires the exact osd model SHA256"
                )
        spec = {
            "schema": "ocr-execution-fingerprint/1",
            "raster_sha256": raster_sha256,
            "raster_digest_method": "SHA256_OF_RENDERED_FILE_BYTES",
            "engine": engine,
            "engine_version": engine_version,
            "requested_languages": list(requested_languages),
            # Include auxiliary resources (for example osd), not only languages.
            "model_sha256s": dict(sorted(model_sha256s.items())),
            "parameters": parameters,
        }
        try:
            canonical = json.dumps(
                spec,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("OCR parameters must be finite JSON data") from exc
        # Detach mutable parameter lists/dicts from the caller.
        result = json.loads(canonical)
        result["cache_key_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
        return result

    def record_execution(
        self,
        asset: EvidenceAsset,
        sidecar: OCRSidecar,
        *,
        page_1based: int,
        raster_path: Path,
        text: str,
        engine: str,
        engine_version: str,
        requested_languages: list[str],
        available_languages: list[str],
        model_sha256s: dict[str, str],
        parameters: dict,
    ) -> OCRSidecar:
        """Bind an executed result to verified source and raster bytes.

        This records an executor's result; it does not run OCR or attest that
        the caller's engine parameters were actually used. That provenance
        requires the executor log alongside this deterministic receipt.
        """
        if sidecar.asset_id != asset.asset_id:
            raise ValueError("OCR sidecar belongs to another source asset")
        if sidecar.decision not in {OCRDecision.REQUIRED, OCRDecision.CONDITIONAL}:
            raise ValueError("OCR decision does not permit an execution record")
        if (
            isinstance(page_1based, bool)
            or not isinstance(page_1based, int)
            or page_1based < 1
        ):
            raise ValueError("physical page must be a positive integer")
        if not isinstance(text, str):
            raise TypeError("OCR text must be a string")
        source = Path(asset.resolved_path or asset.path)
        if not source.is_file():
            raise ValueError("source bytes do not match asset SHA256")
        source_bytes = source.read_bytes()
        if (
            sha256(source_bytes).hexdigest() != asset.sha256
            or len(source_bytes) != asset.size_bytes
        ):
            raise ValueError("source bytes do not match asset SHA256 or size")
        if asset.source_format == EvidenceFormat.PDF:
            try:
                from pypdf import PdfReader
                from pypdf.errors import PdfReadError
            except ImportError as exc:
                raise RuntimeError(
                    "pypdf required to verify physical PDF page bounds"
                ) from exc
            try:
                pdf = PdfReader(io.BytesIO(source_bytes), strict=True)
                if pdf.is_encrypted or page_1based > len(pdf.pages):
                    raise ValueError(
                        "physical PDF page unavailable or source is encrypted"
                    )
            except PdfReadError as exc:
                raise ValueError("source PDF cannot be inspected") from exc
            page_validation = "PHYSICAL_PDF_PAGE_BOUNDS_VERIFIED"
        elif asset.source_format == EvidenceFormat.IMAGE:
            if page_1based != 1:
                raise ValueError("image source has one frame in this adapter")
            page_validation = "SINGLE_IMAGE_FRAME_ASSERTED"
        else:
            page_validation = "PAGE_ASSOCIATION_CALLER_ASSERTED"
        raster = Path(raster_path)
        if not raster.is_file():
            raise ValueError("rendered raster bytes required")
        fingerprint = self.execution_fingerprint(
            raster_sha256=self._digest_path(raster),
            engine=engine,
            engine_version=engine_version,
            requested_languages=requested_languages,
            available_languages=available_languages,
            model_sha256s=model_sha256s,
            parameters=parameters,
        )
        execution = {
            **fingerprint,
            "source_sha256": asset.sha256,
            "page_1based": page_1based,
            "page_validation": page_validation,
            "source_read_mode": "IMMUTABLE_BYTES_SNAPSHOT",
            "render_source_association": "CALLER_ASSERTED; EXECUTOR_REPLAY_REQUIRED",
            "text_sha256": sha256(text.encode("utf-8")).hexdigest(),
            "state": "EXECUTED_DERIVED_UNVERIFIED",
            "authority_effect": "NONE",
        }
        execution["execution_binding_sha256"] = sha256(
            json.dumps(
                execution,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        return replace(
            sidecar,
            execution=execution,
            text_preview=text[:160],
            promoted_to_authoritative=False,
            warnings=list(sidecar.warnings),
        )

    def _validate_execution(self, asset: EvidenceAsset, execution: dict) -> None:
        """Reject partial or internally inconsistent receipts before lineage use."""
        if (
            not isinstance(execution, dict)
            or execution.get("source_sha256") != asset.sha256
        ):
            raise ValueError("OCR execution source digest differs from asset")
        required = {
            "raster_sha256",
            "engine",
            "engine_version",
            "requested_languages",
            "model_sha256s",
            "parameters",
            "text_sha256",
            "page_1based",
            "page_validation",
            "render_source_association",
            "cache_key_sha256",
            "raster_digest_method",
            "state",
            "authority_effect",
            "schema",
        }
        required.add("execution_binding_sha256")
        if not required.issubset(execution):
            raise ValueError("incomplete OCR execution receipt")
        if (
            execution["state"] != "EXECUTED_DERIVED_UNVERIFIED"
            or execution["authority_effect"] != "NONE"
            or not isinstance(execution["text_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", execution["text_sha256"])
            or isinstance(execution["page_1based"], bool)
            or not isinstance(execution["page_1based"], int)
            or execution["page_1based"] < 1
            or not isinstance(execution["model_sha256s"], dict)
        ):
            raise ValueError("invalid OCR execution scope or digest")
        fingerprint = self.execution_fingerprint(
            raster_sha256=execution["raster_sha256"],
            engine=execution["engine"],
            engine_version=execution["engine_version"],
            requested_languages=execution["requested_languages"],
            available_languages=list(execution["model_sha256s"]),
            model_sha256s=execution["model_sha256s"],
            parameters=execution["parameters"],
        )
        if any(execution.get(k) != v for k, v in fingerprint.items()):
            raise ValueError("OCR execution fingerprint mismatch")
        bound = {k: v for k, v in execution.items() if k != "execution_binding_sha256"}
        observed = sha256(
            json.dumps(
                bound,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        if observed != execution["execution_binding_sha256"]:
            raise ValueError("OCR source/page/text execution binding mismatch")

    @staticmethod
    def _digest_path(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def asset_from_path(path: Path, root: Path | None = None) -> EvidenceAsset:
        ext = path.suffix.lower().lstrip(".")
        if ext in {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}:
            fmt = EvidenceFormat.IMAGE
        else:
            fmt = (
                EvidenceFormat(ext)
                if ext in EvidenceFormat._value2member_map_
                else EvidenceFormat.UNKNOWN
            )
        digest = OCREvidenceRuntime._digest_path(path)
        rel_path = str(path.relative_to(root)) if root else str(path)
        return EvidenceAsset(
            asset_id=digest[:16],
            path=rel_path,
            source_format=fmt,
            size_bytes=path.stat().st_size,
            sha256=digest,
            resolved_path=str(path.resolve()),
        )

    @staticmethod
    def to_json(lineage: EvidenceLineageRecord) -> str:
        return json.dumps(asdict(lineage), indent=2, sort_keys=True)


if __name__ == "__main__":
    demo_asset = EvidenceAsset(
        asset_id="demo-image-001",
        path="examples/qps/wcs_hcc_skid.png",
        source_format=EvidenceFormat.IMAGE,
        size_bytes=2048000,
        sha256="demo",
        raster_confidence=0.88,
        notes=["High-value engineering image; preserve as primary evidence."],
    )

    runtime = OCREvidenceRuntime()
    decision = runtime.decide_ocr(demo_asset)
    lineage = runtime.build_lineage(demo_asset, decision)
    print(runtime.to_json(lineage))
