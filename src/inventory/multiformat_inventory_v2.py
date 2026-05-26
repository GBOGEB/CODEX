"""
Wave 14 — Multi-format Inventory and Extraction Pipeline V2.

This module implements the reusable abstraction layer for the Engineering Deck
Convergence Platform. It is intentionally plugin-style rather than one large
script so new engineering formats can be added safely.

Phase coverage in this file:
- Phase 1: multi-type inventory, naming groups, duplicate hashes, links
- Phase 2: lightweight text extraction stubs and first-5-slide contracts

Deferred by design:
- OCR execution
- DWG rendering/conversion
- full Visio shape extraction
- deep engineering SSOT dimension extraction
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol
import json
import re


SUPPORTED_EXTENSIONS = {
    ".pptx",
    ".xlsx",
    ".docx",
    ".pdf",
    ".svg",
    ".vsdx",
    ".drawio",
    ".html",
    ".htm",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
    ".dwg",
}

ENGINEERING_TAG_PATTERNS = {
    "QPLANT": r"\bQPLANT\b|\bQP\.\b",
    "WCS": r"\bWCS\b|WCS\.HCC|WCS_CCB",
    "QPR": r"\bQPR\b",
    "WSH": r"\bWSH\b|WSH_CCB",
    "QSN": r"\bQSN\b|QSN_CCB",
    "External Helium User": r"QCELL|QVE|External Helium User",
    "MIT": r"\bMIT\b|OPC UA|PROFINET",
    "MIS": r"\bMIS\b|interlock|hardwired",
    "MCS": r"\bMCS\b|Broker",
    "PCW": r"\bPCW\b|PAB12|Process Cooling Water",
    "RCW": r"\bRCW\b|HV06|Recovery Cooling Water",
    "HVAC": r"HV03|HV02|HVAC|ventilation",
    "Electrical": r"ES02|electrical|400V|diesel",
}

DRAWING_TYPE_PATTERNS = {
    "P&ID": r"P&ID|PID|instrumentation diagram",
    "PFD": r"PFD|process flow diagram",
    "GA": r"\bGA\b|general arrangement",
    "Floor plan": r"floor|level 0|room layout|building layout",
    "Roof routing": r"roof|roof routing|top view",
    "Side view": r"side view|north view|south view|east|west",
    "Section/slice": r"section|cross-section|slice",
}

HELIUM_LOGISTICS_DEFAULTS = {
    "first_fill_l": 200,
    "daily_fill_l": 50,
    "max_event_loss_l": 200,
    "rolling_10_day_loss_l": 50,
    "monthly_equivalent_gas_m3": 150,
}


@dataclass
class FileInventoryRecord:
    path: str
    extension: str
    size_bytes: int
    modified_time: float
    sha256: str
    naming_group: str
    duplicate_group: Optional[str] = None
    category_tags: List[str] = field(default_factory=list)
    drawing_type: Optional[str] = None
    extractor: Optional[str] = None
    summary: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)


class ExtractorPlugin(Protocol):
    name: str
    extensions: set[str]

    def extract_summary(self, path: Path) -> str:
        ...


class BaseExtractor:
    name = "base"
    extensions: set[str] = set()

    def extract_summary(self, path: Path) -> str:
        return "Extraction not implemented for this format yet."


class PptxExtractor(BaseExtractor):
    name = "pptx_first5_summary"
    extensions = {".pptx"}

    def extract_summary(self, path: Path) -> str:
        return (
            "PPTX extraction contract: read first 5 slides for title, agenda, "
            "included/excluded scope, style guide, and engineering topics."
        )


class SvgExtractor(BaseExtractor):
    name = "svg_text_nodes"
    extensions = {".svg"}

    def extract_summary(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
        nodes = re.findall(r"<(?:title|desc|text)[^>]*>(.*?)</(?:title|desc|text)>", text, flags=re.I | re.S)
        cleaned = [re.sub(r"\s+", " ", node).strip() for node in nodes if node.strip()]
        return "; ".join(cleaned[:20]) or "SVG found, no title/desc/text nodes detected."


class PdfExtractor(BaseExtractor):
    name = "pdf_text_or_conditional_ocr_contract"
    extensions = {".pdf"}

    def extract_summary(self, path: Path) -> str:
        return "PDF extraction contract: use embedded text first; OCR only low-text or scanned pages."


class SpreadsheetExtractor(BaseExtractor):
    name = "xlsx_sheet_header_contract"
    extensions = {".xlsx"}

    def extract_summary(self, path: Path) -> str:
        return "XLSX extraction contract: collect sheet names, key headers, and first rows summary."


class DocxExtractor(BaseExtractor):
    name = "docx_heading_summary_contract"
    extensions = {".docx"}

    def extract_summary(self, path: Path) -> str:
        return "DOCX extraction contract: collect headings and first section summaries."


class ImageExtractor(BaseExtractor):
    name = "image_ocr_sidecar_contract"
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}

    def extract_summary(self, path: Path) -> str:
        return "Image extraction contract: preserve image as evidence; OCR only as sidecar metadata."


class VisioExtractor(BaseExtractor):
    name = "visio_shape_text_contract"
    extensions = {".vsdx"}

    def extract_summary(self, path: Path) -> str:
        return "Visio extraction contract: parse page names and shape text; map connectors to graph edges."


class DrawioExtractor(BaseExtractor):
    name = "drawio_graph_contract"
    extensions = {".drawio"}

    def extract_summary(self, path: Path) -> str:
        return "draw.io extraction contract: parse XML cells, labels, nodes, connectors, and graph edges."


class DwgExtractor(BaseExtractor):
    name = "dwg_render_then_ocr_contract"
    extensions = {".dwg"}

    def extract_summary(self, path: Path) -> str:
        return "DWG extraction contract: render/convert to PDF or high-resolution PNG first; then OCR/text extraction."


class HtmlExtractor(BaseExtractor):
    name = "html_fragment_text_contract"
    extensions = {".html", ".htm"}

    def extract_summary(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()[:1000]


class MultiFormatInventoryV2:
    def __init__(self, root: Path):
        self.root = root
        self.plugins: List[ExtractorPlugin] = [
            PptxExtractor(),
            SpreadsheetExtractor(),
            DocxExtractor(),
            PdfExtractor(),
            SvgExtractor(),
            VisioExtractor(),
            DrawioExtractor(),
            HtmlExtractor(),
            ImageExtractor(),
            DwgExtractor(),
        ]

    def scan(self) -> List[FileInventoryRecord]:
        records = [self._record_file(path) for path in self._iter_supported_files()]
        return self._assign_duplicate_groups(records)

    def _iter_supported_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path

    def _record_file(self, path: Path) -> FileInventoryRecord:
        digest = self._hash_file(path)
        name_text = path.stem.replace("_", " ").replace("-", " ")
        plugin = self._plugin_for(path)
        summary = plugin.extract_summary(path) if plugin else None
        semantic_text = f"{path.name} {summary or ''}"

        return FileInventoryRecord(
            path=str(path.relative_to(self.root)),
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
            modified_time=path.stat().st_mtime,
            sha256=digest,
            naming_group=self._naming_group(name_text),
            category_tags=self._classify_tags(semantic_text),
            drawing_type=self._classify_drawing_type(semantic_text),
            extractor=plugin.name if plugin else None,
            summary=summary,
            links={"relative": str(path.relative_to(self.root))},
        )

    def _plugin_for(self, path: Path) -> Optional[ExtractorPlugin]:
        ext = path.suffix.lower()
        return next((plugin for plugin in self.plugins if ext in plugin.extensions), None)

    @staticmethod
    def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
        hasher = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _naming_group(name_text: str) -> str:
        tokens = re.findall(r"[A-Za-z0-9]+", name_text.upper())
        useful = [token for token in tokens if len(token) > 1]
        return "_".join(useful[:4]) or "UNGROUPED"

    @staticmethod
    def _classify_tags(text: str) -> List[str]:
        return [tag for tag, pattern in ENGINEERING_TAG_PATTERNS.items() if re.search(pattern, text, flags=re.I)]

    @staticmethod
    def _classify_drawing_type(text: str) -> Optional[str]:
        for drawing_type, pattern in DRAWING_TYPE_PATTERNS.items():
            if re.search(pattern, text, flags=re.I):
                return drawing_type
        return None

    @staticmethod
    def _assign_duplicate_groups(records: List[FileInventoryRecord]) -> List[FileInventoryRecord]:
        by_hash: Dict[str, List[FileInventoryRecord]] = {}
        for record in records:
            by_hash.setdefault(record.sha256, []).append(record)

        for index, (_, group) in enumerate(by_hash.items(), start=1):
            if len(group) > 1:
                group_id = f"DUP-{index:04d}"
                for record in group:
                    record.duplicate_group = group_id
        return records

    @staticmethod
    def to_json(records: List[FileInventoryRecord]) -> str:
        payload = {
            "schema": "edcp.multiformat_inventory.v2",
            "helium_logistics_defaults": HELIUM_LOGISTICS_DEFAULTS,
            "records": [asdict(record) for record in records],
        }
        return json.dumps(payload, indent=2, sort_keys=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EDCP multi-format inventory V2")
    parser.add_argument("root", help="Root folder to scan")
    args = parser.parse_args()

    inventory = MultiFormatInventoryV2(Path(args.root))
    print(inventory.to_json(inventory.scan()))
