from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = REPO_ROOT / "MASTER_input" / "contracts" / "master-contract" / "contract.yaml"
DEFAULT_SCHEMA = REPO_ROOT / "MASTER_input" / "schemas" / "contract_schema.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "MASTER_input" / "generated"
DEFAULT_CHECKPOINT_DIR = REPO_ROOT / "MASTER_input" / "checkpoints"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class ContractWorkbenchError(ValueError):
    """Raised when the MASTER Contract Workbench SSOT is invalid."""


@dataclass(frozen=True)
class Sheet:
    name: str
    headers: list[str]
    rows: list[list[Any]]


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    """Load a YAML 1.2 contract SSOT document."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ContractWorkbenchError(f"Contract SSOT must be a mapping: {path}")
    return data


def _load_schema(path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ContractWorkbenchError(f"Contract schema must be a mapping: {path}")
    return data


def _duplicate_ids(items: list[dict[str, Any]], label: str) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        item_id = item.get("id")
        if not item_id:
            duplicates.add("<missing>")
        elif item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    return [f"{label} contains duplicate or missing ids: {sorted(duplicates)}"] if duplicates else []


def validate_contract(contract: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    """Validate section presence, lifecycle, ownership, RTM and question hierarchy rules."""
    schema = schema or _load_schema()
    errors: list[str] = []

    for section in schema.get("required_top_level_sections", []):
        if section not in contract:
            errors.append(f"missing required section: {section}")

    if contract.get("metadata", {}).get("authority") != "YAML_SSOT":
        errors.append("metadata.authority must be YAML_SSOT")
    if contract.get("metadata", {}).get("generated_outputs_are_system_of_record") is not False:
        errors.append("generated outputs must not be marked as the system of record")

    stakeholders = contract.get("stakeholders", [])
    lifecycle_phases = contract.get("lifecycle", {}).get("phases", [])
    requirements = contract.get("requirements", [])
    questions = contract.get("questions", [])
    rtm_items = contract.get("rtm", [])
    change_requests = contract.get("change_requests", [])

    errors.extend(_duplicate_ids(stakeholders, "stakeholders"))
    errors.extend(_duplicate_ids(lifecycle_phases, "lifecycle phases"))
    errors.extend(_duplicate_ids(requirements, "requirements"))
    errors.extend(_duplicate_ids(questions, "questions"))
    errors.extend(_duplicate_ids(rtm_items, "RTM"))
    errors.extend(_duplicate_ids(change_requests, "change requests"))

    stakeholder_ids = {item.get("id") for item in stakeholders}
    lifecycle_names = {item.get("name") for item in lifecycle_phases}
    allowed_phases = set(schema.get("allowed_lifecycle_phases", []))
    requirement_ids = {item.get("id") for item in requirements}
    question_ids = {item.get("id") for item in questions}
    rtm_ids = {item.get("id") for item in rtm_items}
    rtm_requirement_ids = {item.get("requirement_id") for item in rtm_items}
    allowed_requirement_statuses = set(schema.get("allowed_requirement_statuses", []))
    allowed_question_statuses = set(schema.get("allowed_question_statuses", []))

    lifecycle_sequences = [phase.get("sequence") for phase in lifecycle_phases]
    if lifecycle_sequences != sorted(lifecycle_sequences):
        errors.append("lifecycle phases must be declared in ascending sequence order")

    unsupported_phases = lifecycle_names - allowed_phases
    if unsupported_phases:
        errors.append(f"lifecycle contains unsupported phases: {sorted(unsupported_phases)}")

    for requirement in requirements:
        req_id = requirement.get("id", "<missing>")
        if requirement.get("owner") not in stakeholder_ids:
            errors.append(f"requirement {req_id} has unknown owner {requirement.get('owner')}")
        if requirement.get("lifecycle_phase") not in lifecycle_names:
            errors.append(f"requirement {req_id} has unknown lifecycle phase {requirement.get('lifecycle_phase')}")
        if requirement.get("status") not in allowed_requirement_statuses:
            errors.append(f"requirement {req_id} has unsupported status {requirement.get('status')}")
        for dependency in requirement.get("depends_on", []):
            if dependency not in requirement_ids:
                errors.append(f"requirement {req_id} depends on unknown requirement {dependency}")
        for rtm_link in requirement.get("rtm_links", []):
            if rtm_link not in rtm_ids:
                errors.append(f"requirement {req_id} references unknown RTM link {rtm_link}")
        if not set(requirement.get("rtm_links", [])) and req_id not in rtm_requirement_ids:
            errors.append(f"requirement {req_id} has no RTM coverage")

    for rtm in rtm_items:
        rtm_id = rtm.get("id", "<missing>")
        if rtm.get("requirement_id") not in requirement_ids:
            errors.append(f"RTM item {rtm_id} references unknown requirement {rtm.get('requirement_id')}")

    root_questions = 0
    for question in questions:
        question_id = question.get("id", "<missing>")
        parent_id = question.get("parent_id")
        if parent_id is None:
            root_questions += 1
        elif parent_id not in question_ids:
            errors.append(f"question {question_id} references unknown parent {parent_id}")
        if question.get("requirement_id") not in requirement_ids:
            errors.append(f"question {question_id} references unknown requirement {question.get('requirement_id')}")
        if question.get("lifecycle_phase") not in lifecycle_names:
            errors.append(f"question {question_id} has unknown lifecycle phase {question.get('lifecycle_phase')}")
        if question.get("status") not in allowed_question_statuses:
            errors.append(f"question {question_id} has unsupported status {question.get('status')}")
    if question_ids and root_questions == 0:
        errors.append("question hierarchy must include at least one root question")

    for change_request in change_requests:
        cr_id = change_request.get("id", "<missing>")
        for req_id in change_request.get("affected_requirements", []):
            if req_id not in requirement_ids:
                errors.append(f"change request {cr_id} references unknown requirement {req_id}")

    if errors:
        raise ContractWorkbenchError("; ".join(errors))
    return errors


def build_dependency_trace(contract: dict[str, Any]) -> dict[str, Any]:
    """Build requirement dependency, RTM, question and change-request lineage."""
    questions_by_requirement: dict[str, list[str]] = {}
    for question in contract.get("questions", []):
        questions_by_requirement.setdefault(question.get("requirement_id"), []).append(question.get("id"))

    cr_by_requirement: dict[str, list[str]] = {}
    for change_request in contract.get("change_requests", []):
        for req_id in change_request.get("affected_requirements", []):
            cr_by_requirement.setdefault(req_id, []).append(change_request.get("id"))

    rtm_by_requirement: dict[str, list[str]] = {}
    for rtm in contract.get("rtm", []):
        rtm_by_requirement.setdefault(rtm.get("requirement_id"), []).append(rtm.get("id"))

    lineage = []
    for requirement in contract.get("requirements", []):
        req_id = requirement.get("id")
        lineage.append(
            {
                "requirement_id": req_id,
                "owner": requirement.get("owner"),
                "lifecycle_phase": requirement.get("lifecycle_phase"),
                "depends_on": requirement.get("depends_on", []),
                "rtm": sorted(set(requirement.get("rtm_links", []) + rtm_by_requirement.get(req_id, []))),
                "questions": questions_by_requirement.get(req_id, []),
                "change_requests": cr_by_requirement.get(req_id, []),
            }
        )
    return {
        "contract_id": contract.get("metadata", {}).get("contract_id"),
        "version": contract.get("metadata", {}).get("version"),
        "authority": contract.get("metadata", {}).get("authority"),
        "lineage": lineage,
    }


def _sheets(contract: dict[str, Any], trace: dict[str, Any]) -> list[Sheet]:
    metadata = contract.get("metadata", {})
    return [
        Sheet("Metadata", ["Field", "Value"], [[key, value] for key, value in metadata.items()]),
        Sheet("Lifecycle", ["ID", "Name", "Sequence", "Target"], [[p.get("id"), p.get("name"), p.get("sequence"), p.get("target")] for p in contract.get("lifecycle", {}).get("phases", [])]),
        Sheet("Stakeholders", ["ID", "Name", "Role", "Responsibilities"], [[s.get("id"), s.get("name"), s.get("role"), ", ".join(s.get("responsibilities", []))] for s in contract.get("stakeholders", [])]),
        Sheet("Requirements", ["ID", "Title", "Owner", "Lifecycle", "Status", "Depends On", "RTM"], [[r.get("id"), r.get("title"), r.get("owner"), r.get("lifecycle_phase"), r.get("status"), ", ".join(r.get("depends_on", [])), ", ".join(r.get("rtm_links", []))] for r in contract.get("requirements", [])]),
        Sheet("Questions", ["ID", "Parent", "Requirement", "Lifecycle", "Status", "Question"], [[q.get("id"), q.get("parent_id") or "ROOT", q.get("requirement_id"), q.get("lifecycle_phase"), q.get("status"), q.get("question")] for q in contract.get("questions", [])]),
        Sheet("RTM", ["ID", "Requirement", "Verification", "Evidence"], [[r.get("id"), r.get("requirement_id"), r.get("verification_method"), r.get("evidence")] for r in contract.get("rtm", [])]),
        Sheet("Change Requests", ["ID", "Title", "Status", "Source", "Requirements", "Decision"], [[c.get("id"), c.get("title"), c.get("status"), c.get("source"), ", ".join(c.get("affected_requirements", [])), c.get("decision")] for c in contract.get("change_requests", [])]),
        Sheet("Changelog", ["Version", "Date", "Author", "Summary"], [[c.get("version"), c.get("date"), c.get("author"), c.get("summary")] for c in contract.get("changelog", [])]),
        Sheet("Trace", ["Requirement", "Owner", "Lifecycle", "Depends On", "RTM", "Questions", "Change Requests"], [[l.get("requirement_id"), l.get("owner"), l.get("lifecycle_phase"), ", ".join(l.get("depends_on", [])), ", ".join(l.get("rtm", [])), ", ".join(l.get("questions", [])), ", ".join(l.get("change_requests", []))] for l in trace.get("lineage", [])]),
    ]


def _cell_ref(row: int, col: int) -> str:
    letters = ""
    while col:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"


def _sheet_xml(sheet: Sheet) -> str:
    rows = [sheet.headers] + sheet.rows
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            cell_value = json.dumps(value, default=str) if isinstance(value, (dict, list)) else str(value if value is not None else "")
            text = xml_escape(cell_value)
            cells.append(f'<c r="{_cell_ref(row_index, col_index)}" t="inlineStr"><is><t>{text}</t></is></c>')
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(row_xml)}</sheetData></worksheet>'


def _write_zip_entry(archive: zipfile.ZipFile, name: str, payload: str) -> None:
    entry = zipfile.ZipInfo(name, ZIP_EPOCH)
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o644 << 16
    archive.writestr(entry, payload)


def _write_xlsx(path: Path, sheets: list[Sheet]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_entries = "".join(f'<sheet name="{xml_escape(sheet.name[:31])}" sheetId="{index}" r:id="rId{index}"/>' for index, sheet in enumerate(sheets, start=1))
    rel_entries = "".join(f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>' for index in range(1, len(sheets) + 1))
    content_overrides = "".join(f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for index in range(1, len(sheets) + 1))
    with zipfile.ZipFile(path, "w") as xlsx:
        _write_zip_entry(xlsx, "[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>{content_overrides}</Types>')
        _write_zip_entry(xlsx, "_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        _write_zip_entry(xlsx, "xl/workbook.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheet_entries}</sheets></workbook>')
        _write_zip_entry(xlsx, "xl/_rels/workbook.xml.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rel_entries}</Relationships>')
        for index, sheet in enumerate(sheets, start=1):
            _write_zip_entry(xlsx, f"xl/worksheets/sheet{index}.xml", _sheet_xml(sheet))


def _display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return str(value)


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = "".join("<tr>" + "".join(f"<td>{escape(_display(value))}</td>" for value in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _write_html(path: Path, contract: dict[str, Any], sheets: list[Sheet]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nav = "".join(f'<li><a href="#{escape(sheet.name.lower().replace(" ", "-"))}">{escape(sheet.name)}</a></li>' for sheet in sheets)
    sections = "".join(f'<section id="{escape(sheet.name.lower().replace(" ", "-"))}"><h2>{escape(sheet.name)}</h2>{_table(sheet.headers, sheet.rows)}</section>' for sheet in sheets)
    strategic = "".join(f"<p>{escape(line)}</p>" for line in contract.get("governance", {}).get("strategic_statement", []))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(contract.get('metadata', {}).get('title', 'MASTER Contract Workbench'))}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2937; }}
nav ul {{ display: flex; flex-wrap: wrap; gap: .75rem; padding: 0; list-style: none; }}
nav a {{ background: #1f4e79; color: white; padding: .45rem .7rem; border-radius: .35rem; text-decoration: none; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
th, td {{ border: 1px solid #d1d5db; padding: .5rem; text-align: left; vertical-align: top; }}
th {{ background: #f3f4f6; }}
.banner {{ border-left: .4rem solid #c00000; background: #fff7ed; padding: 1rem; }}
</style>
</head>
<body>
<h1>{escape(contract.get('metadata', {}).get('title', 'MASTER Contract Workbench'))}</h1>
<div class="banner"><strong>Authority:</strong> YAML SSOT. Generated artefacts are not the System of Record.{strategic}</div>
<nav><h2>Navigation</h2><ul>{nav}</ul></nav>
{sections}
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _generated_at_value(generated_at: str | None = None) -> str:
    if generated_at:
        return generated_at
    if os.environ.get("SOURCE_DATE_EPOCH"):
        epoch = int(os.environ["SOURCE_DATE_EPOCH"])
        return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _output_hashes(outputs: dict[str, Path]) -> dict[str, str]:
    return {name: _sha256(path) for name, path in sorted(outputs.items())}


def _portable_source(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def generate_outputs(
    contract_path: Path = DEFAULT_CONTRACT,
    schema_path: Path = DEFAULT_SCHEMA,
    output_dir: Path = DEFAULT_OUTPUT,
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR,
    generated_at: str | None = None,
) -> dict[str, str]:
    """Validate the YAML SSOT and generate synchronized Excel, HTML and trace outputs."""
    contract = load_contract(contract_path)
    schema = _load_schema(schema_path)
    validate_contract(contract, schema)
    trace = build_dependency_trace(contract)
    sheets = _sheets(contract, trace)

    contract_id = contract.get("metadata", {}).get("contract_id", "MASTER-CW")
    timestamp = _generated_at_value(generated_at)
    excel_path = output_dir / "excel" / f"{contract_id}.xlsx"
    html_path = output_dir / "html" / f"{contract_id}.html"
    trace_path = output_dir / "reports" / f"{contract_id}.trace.json"
    dashboard_path = output_dir / "dashboards" / f"{contract_id}.dashboard.json"
    manifest_path = output_dir / "reports" / f"{contract_id}.manifest.json"
    checkpoint_path = checkpoint_dir / f"{contract_id}-{contract.get('metadata', {}).get('version', '0.0.0')}.json"

    _write_xlsx(excel_path, sheets)
    _write_html(html_path, contract, sheets)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(json.dumps({"contract_id": contract_id, "generated_at": timestamp, "requirements": len(contract.get("requirements", [])), "questions": len(contract.get("questions", [])), "change_requests": len(contract.get("change_requests", [])), "authority": "YAML_SSOT"}, indent=2), encoding="utf-8")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    source = _portable_source(contract_path)
    checkpoint_path.write_text(json.dumps({"contract_id": contract_id, "version": contract.get("metadata", {}).get("version"), "generated_at": timestamp, "source": source, "trace": trace}, indent=2), encoding="utf-8")

    derivative_paths = {"excel": excel_path, "html": html_path, "trace": trace_path, "dashboard": dashboard_path, "checkpoint": checkpoint_path}
    derivative_refs = {
        "excel": f"generated/excel/{excel_path.name}",
        "html": f"generated/html/{html_path.name}",
        "trace": f"generated/reports/{trace_path.name}",
        "dashboard": f"generated/dashboards/{dashboard_path.name}",
        "checkpoint": f"checkpoints/{checkpoint_path.name}",
    }
    manifest_path.write_text(json.dumps({"contract_id": contract_id, "generated_at": timestamp, "source": source, "derivatives_are_system_of_record": False, "outputs": derivative_refs, "output_hashes": _output_hashes(derivative_paths)}, indent=2), encoding="utf-8")
    return {"excel": str(excel_path), "html": str(html_path), "trace": str(trace_path), "dashboard": str(dashboard_path), "checkpoint": str(checkpoint_path), "manifest": str(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MASTER Contract Workbench derivatives from YAML SSOT.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--checkpoint-output", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--generated-at", help="Optional deterministic UTC generation stamp, for example 20260605T000000Z.")
    args = parser.parse_args()
    outputs = generate_outputs(args.contract, args.schema, args.output, args.checkpoint_output, args.generated_at)
    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
