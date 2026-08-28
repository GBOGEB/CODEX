"""Generate a deterministic semantic manifest for QPS release artifacts.

The extractor intentionally separates semantic comparison from exact binary hashes.
It uses only the Python standard library and supports XLSX, DOCX, PPTX and HTML.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def norm_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value or "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"[ \t]+", " ", value).strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(norm_text(value).encode("utf-8")).hexdigest()


def xml_root(zf: zipfile.ZipFile, name: str):
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        return None


def relmap(zf: zipfile.ZipFile, name: str) -> dict[str, str]:
    root = xml_root(zf, name)
    if root is None:
        return {}
    return {
        el.attrib.get("Id", ""): el.attrib.get("Target", "")
        for el in root
        if el.attrib.get("Id")
    }


def relationship_targets(zf: zipfile.ZipFile, name: str) -> list[tuple[str, str]]:
    root = xml_root(zf, name)
    if root is None:
        return []
    return [
        (el.attrib.get("Type", ""), el.attrib.get("Target", ""))
        for el in root.findall(f"{{{REL_NS}}}Relationship")
    ]


def resolve_part(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return str(PurePosixPath(PurePosixPath(base_part).parent, target))


def xlsx_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    root = xml_root(zf, "xl/sharedStrings.xml")
    if root is None:
        return []
    values = []
    for item in root.findall("s:si", NS):
        values.append(norm_text("".join(t.text or "" for t in item.findall(".//s:t", NS))))
    return values


def xlsx_cell_value(cell, shared_strings: list[str]) -> str | None:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        inline = cell.find("s:is", NS)
        if inline is None:
            return ""
        return norm_text("".join(t.text or "" for t in inline.findall(".//s:t", NS)))

    value = cell.find("s:v", NS)
    if value is None:
        return None
    raw = norm_text(value.text or "")
    if cell_type == "s":
        try:
            return shared_strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE" if raw == "0" else raw
    return raw


def xlsx_manifest(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        wb = xml_root(zf, "xl/workbook.xml")
        rels = relmap(zf, "xl/_rels/workbook.xml.rels")
        shared_strings = xlsx_shared_strings(zf)
        sheets = []
        defined = []
        formulas = {}
        controlled_values = {}
        tables = []
        chart_sources = []
        if wb is not None:
            for sh in wb.findall("s:sheets/s:sheet", NS):
                rid = sh.attrib.get(f"{{{NS['r']}}}id", "")
                target = rels.get(rid, "")
                if target and not target.startswith("xl/"):
                    target = "xl/" + target.lstrip("/")
                sheets.append({"name": sh.attrib.get("name", ""), "target": target})
            for dn in wb.findall("s:definedNames/s:definedName", NS):
                defined.append({"name": dn.attrib.get("name", ""), "value": norm_text(dn.text or "")})
        for sh in sheets:
            root = xml_root(zf, sh["target"])
            if root is None:
                continue
            for cell in root.findall(".//s:c", NS):
                ref = cell.attrib.get("r", "")
                formula = cell.find("s:f", NS)
                key = f"{sh['name']}!{ref}"
                if formula is not None:
                    formulas[key] = norm_text(formula.text or "")
                else:
                    resolved = xlsx_cell_value(cell, shared_strings)
                    if resolved is not None:
                        controlled_values[key] = resolved
        for name in sorted(n for n in zf.namelist() if n.startswith("xl/tables/") and n.endswith(".xml")):
            root = xml_root(zf, name)
            if root is not None:
                tables.append({"name": root.attrib.get("name", ""), "ref": root.attrib.get("ref", "")})
        formula_tags = {f"{{{NS['c']}}}f"}
        for name in sorted(n for n in zf.namelist() if n.startswith("xl/charts/") and n.endswith(".xml")):
            root = xml_root(zf, name)
            if root is not None:
                refs = sorted({norm_text(el.text or "") for el in root.iter() if el.tag in formula_tags and norm_text(el.text or "")})
                chart_sources.append({"chart": name, "sources": refs})
        return {
            "kind": "xlsx",
            "sheet_order": [s["name"] for s in sheets],
            "sheet_names": sorted(s["name"] for s in sheets),
            "defined_names": sorted(defined, key=lambda x: (x["name"], x["value"])),
            "normalized_formula_map": dict(sorted(formulas.items())),
            "normalized_value_map_for_controlled_cells": dict(sorted(controlled_values.items())),
            "table_names_and_ranges": sorted(tables, key=lambda x: (x["name"], x["ref"])),
            "chart_data_source_ranges": chart_sources,
        }


def docx_manifest(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        root = xml_root(zf, "word/document.xml")
        headings, paragraphs, tables, links = [], [], [], []
        if root is not None:
            for p in root.findall(".//w:p", NS):
                text = norm_text("".join(t.text or "" for t in p.findall(".//w:t", NS)))
                if not text:
                    continue
                paragraphs.append(sha256_text(text))
                style = p.find("w:pPr/w:pStyle", NS)
                sval = style.attrib.get(f"{{{NS['w']}}}val", "") if style is not None else ""
                if sval.lower().startswith("heading"):
                    headings.append(text)
                for h in p.findall(".//w:hyperlink", NS):
                    anchor = h.attrib.get(f"{{{NS['w']}}}anchor")
                    if anchor:
                        links.append(anchor)
            for tbl in root.findall(".//w:tbl", NS):
                rows = tbl.findall("w:tr", NS)
                row_text = []
                max_cols = 0
                for row in rows:
                    cells = row.findall("w:tc", NS)
                    max_cols = max(max_cols, len(cells))
                    row_text.append(" | ".join(norm_text("".join(t.text or "" for t in c.findall(".//w:t", NS))) for c in cells))
                tables.append({"rows": len(rows), "cols_max": max_cols, "text_hash": sha256_text("\n".join(row_text))})
        return {
            "kind": "docx",
            "heading_sequence": headings,
            "paragraph_text_hashes": paragraphs,
            "table_shape_and_text_hashes": tables,
            "internal_link_targets": sorted(set(links)),
        }


def pptx_notes_path(zf: zipfile.ZipFile, slide_path: str) -> str | None:
    slide_name = PurePosixPath(slide_path).name
    rel_path = str(PurePosixPath(slide_path).parent / "_rels" / f"{slide_name}.rels")
    for rel_type, target in relationship_targets(zf, rel_path):
        if rel_type.endswith("/notesSlide"):
            return resolve_part(slide_path, target)
    return None


def pptx_object_count(root) -> int:
    if root is None:
        return 0
    sp_tree = root.find("p:cSld/p:spTree", NS)
    if sp_tree is None:
        return 0
    object_tags = {
        f"{{{NS['p']}}}sp",
        f"{{{NS['p']}}}pic",
        f"{{{NS['p']}}}graphicFrame",
        f"{{{NS['p']}}}grpSp",
        f"{{{NS['p']}}}cxnSp",
    }
    return sum(1 for child in sp_tree if child.tag in object_tags)


def pptx_manifest(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        pres = xml_root(zf, "ppt/presentation.xml")
        rels = relmap(zf, "ppt/_rels/presentation.xml.rels")
        slide_paths = []
        if pres is not None:
            for sid in pres.findall("p:sldIdLst/p:sldId", NS):
                rid = sid.attrib.get(f"{{{NS['r']}}}id", "")
                target = rels.get(rid, "")
                if target and not target.startswith("ppt/"):
                    target = "ppt/" + target.lstrip("/")
                slide_paths.append(target)
        titles, text_hashes, counts, notes_hashes = [], [], [], []
        for spath in slide_paths:
            root = xml_root(zf, spath)
            texts = []
            if root is not None:
                texts = [norm_text(t.text or "") for t in root.findall(".//a:t", NS) if norm_text(t.text or "")]
            counts.append(pptx_object_count(root))
            titles.append(texts[0] if texts else "")
            text_hashes.append(sha256_text("\n".join(texts)))

            note_text = ""
            notes_path = pptx_notes_path(zf, spath)
            if notes_path:
                nroot = xml_root(zf, notes_path)
                if nroot is not None:
                    note_text = "\n".join(
                        norm_text(t.text or "")
                        for t in nroot.findall(".//a:t", NS)
                        if norm_text(t.text or "")
                    )
            notes_hashes.append(sha256_text(note_text))
        chart_hashes = []
        for name in sorted(n for n in zf.namelist() if n.startswith("ppt/charts/") and n.endswith(".xml")):
            root = xml_root(zf, name)
            refs = [] if root is None else sorted({norm_text(el.text or "") for el in root.findall(".//c:f", NS) if norm_text(el.text or "")})
            chart_hashes.append({"chart": name, "source_hash": sha256_text("\n".join(refs))})
        return {
            "kind": "pptx",
            "slide_order": slide_paths,
            "slide_titles": titles,
            "normalized_text_hashes": text_hashes,
            "object_count_by_slide": counts,
            "chart_data_hashes": chart_hashes,
            "notes_text_hashes": notes_hashes,
        }


def html_manifest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    ids = re.findall(r"\bid=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE)
    headings = [
        norm_text(re.sub(r"<[^>]+>", "", x))
        for x in re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", text, flags=re.IGNORECASE | re.DOTALL)
    ]
    assets = sorted(set(re.findall(r"(?:src|href)=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE)))
    visible = norm_text(
        re.sub(
            r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>",
            " ",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    )
    embedded = [
        sha256_text(x)
        for x in re.findall(
            r"<script[^>]+type=[\"']application/(?:json|ld\+json)[\"'][^>]*>(.*?)</script>",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    ]
    return {
        "kind": "html",
        "route_or_section_ids": ids,
        "heading_sequence": headings,
        "local_asset_paths": assets,
        "normalized_text_hashes": [sha256_text(visible)],
        "embedded_data_hashes": embedded,
    }


def build(path: Path) -> dict:
    ext = path.suffix.lower()
    handlers = {
        ".xlsx": xlsx_manifest,
        ".docx": docx_manifest,
        ".pptx": pptx_manifest,
        ".html": html_manifest,
        ".htm": html_manifest,
    }
    if ext not in handlers:
        raise SystemExit(f"Unsupported artifact type: {ext}")
    result = handlers[ext](path)
    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    result["artifact_name"] = path.name
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    result = build(args.artifact)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
