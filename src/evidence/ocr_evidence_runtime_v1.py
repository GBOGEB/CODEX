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

from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Optional
import json


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
    notes: List[str] = field(default_factory=list)


@dataclass
class OCRSidecar:
    asset_id: str
    decision: OCRDecision
    confidence: float
    text_preview: str = ""
    promoted_to_authoritative: bool = False
    reason: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class EvidenceLineageRecord:
    asset_id: str
    original_path: str
    evidence_primary: bool
    derived_artifacts: List[str] = field(default_factory=list)
    sidecar: Optional[OCRSidecar] = None
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

    def decide_ocr(self, asset: EvidenceAsset) -> OCRSidecar:
        if asset.source_format == EvidenceFormat.DWG:
            return OCRSidecar(
                asset_id=asset.asset_id,
                decision=OCRDecision.DEFER_DWG_RENDER,
                confidence=0.0,
                reason="DWG must be rendered to PDF or high-resolution image before OCR.",
                warnings=["Do not OCR raw DWG directly."],
            )

        if asset.source_format in {EvidenceFormat.SVG, EvidenceFormat.DRAWIO, EvidenceFormat.VSDX}:
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
        return (
            sidecar.confidence >= self.MIN_PROMOTION_CONFIDENCE
            and sidecar.decision in {OCRDecision.REQUIRED, OCRDecision.CONDITIONAL}
            and not sidecar.warnings
        )

    def build_lineage(self, asset: EvidenceAsset, sidecar: OCRSidecar) -> EvidenceLineageRecord:
        sidecar.promoted_to_authoritative = self.may_promote_ocr(sidecar)
        return EvidenceLineageRecord(
            asset_id=asset.asset_id,
            original_path=asset.path,
            evidence_primary=True,
            derived_artifacts=["ocr_sidecar"] if sidecar.decision != OCRDecision.SKIP else [],
            sidecar=sidecar,
        )

    @staticmethod
    def asset_from_path(path: Path, root: Optional[Path] = None) -> EvidenceAsset:
        ext = path.suffix.lower().lstrip(".")
        fmt = EvidenceFormat(ext) if ext in EvidenceFormat._value2member_map_ else EvidenceFormat.UNKNOWN
        digest = sha256(path.read_bytes()).hexdigest()
        rel_path = str(path.relative_to(root)) if root else str(path)
        return EvidenceAsset(
            asset_id=digest[:16],
            path=rel_path,
            source_format=fmt,
            size_bytes=path.stat().st_size,
            sha256=digest,
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
