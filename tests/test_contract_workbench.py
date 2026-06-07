from __future__ import annotations

import copy
import json
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contract_workbench.generator import ContractWorkbenchError, build_dependency_trace, generate_outputs, load_contract, validate_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "MASTER_input" / "contracts" / "master-contract" / "contract.yaml"
SCHEMA = ROOT / "MASTER_input" / "schemas" / "contract_schema.yaml"


def _broken_contract(tmp_path: Path, contract: dict, mutation) -> Path:
    broken = copy.deepcopy(contract)
    mutation(broken)
    path = tmp_path / "broken.yaml"
    path.write_text(yaml.safe_dump(broken), encoding="utf-8")
    return path


def test_master_contract_ssot_validates_and_traces_lineage() -> None:
    contract = load_contract(CONTRACT)

    assert validate_contract(contract) == []
    trace = build_dependency_trace(contract)

    assert trace["authority"] == "YAML_SSOT"
    ssot_lineage = next(item for item in trace["lineage"] if item["requirement_id"] == "REQ-SSOT-001")
    assert ssot_lineage["rtm"] == ["RTM-001"]
    assert ssot_lineage["questions"] == ["Q-001"]
    assert ssot_lineage["change_requests"] == ["CR-0001"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda c: c["questions"][0].update(parent_id="Q-MISSING"), "unknown parent"),
        (lambda c: c["requirements"][0].update(owner="STK-MISSING"), "unknown owner"),
        (lambda c: c["requirements"][0].update(status="Invented"), "unsupported status"),
        (lambda c: c["requirements"][0].update(rtm_links=["RTM-MISSING"]), "unknown RTM link"),
        (lambda c: c["requirements"].append(copy.deepcopy(c["requirements"][0])), "duplicate or missing ids"),
        (lambda c: c["lifecycle"]["phases"].reverse(), "ascending sequence order"),
    ],
)
def test_master_contract_rejects_governance_violations(tmp_path: Path, mutation, message: str) -> None:
    path = _broken_contract(tmp_path, load_contract(CONTRACT), mutation)

    with pytest.raises(ContractWorkbenchError, match=message):
        validate_contract(load_contract(path))


def test_generate_outputs_creates_excel_html_trace_dashboard_manifest_and_checkpoint(tmp_path: Path) -> None:
    outputs = generate_outputs(
        contract_path=CONTRACT,
        schema_path=SCHEMA,
        output_dir=tmp_path / "generated",
        checkpoint_dir=tmp_path / "checkpoints",
        generated_at="20260605T000000Z",
    )

    excel = Path(outputs["excel"])
    html = Path(outputs["html"])
    trace = Path(outputs["trace"])
    dashboard = Path(outputs["dashboard"])
    checkpoint = Path(outputs["checkpoint"])
    manifest = Path(outputs["manifest"])

    assert excel.exists()
    assert html.exists()
    assert trace.exists()
    assert dashboard.exists()
    assert checkpoint.exists()
    assert manifest.exists()

    with zipfile.ZipFile(excel) as workbook:
        workbook_xml = workbook.read("xl/workbook.xml").decode()
        assert "Requirements" in workbook_xml
        assert "Change Requests" in workbook_xml
        assert "Trace" in workbook_xml

    html_text = html.read_text(encoding="utf-8")
    assert "Generated artefacts are not the System of Record" in html_text
    assert "Questions" in html_text
    assert "generated_outputs_are_system_of_record</td><td>False" in html_text

    trace_json = json.loads(trace.read_text(encoding="utf-8"))
    assert trace_json["contract_id"] == "MASTER-CW-001"
    assert trace_json["lineage"][1]["depends_on"] == ["REQ-SSOT-001"]

    dashboard_json = json.loads(dashboard.read_text(encoding="utf-8"))
    assert dashboard_json["authority"] == "YAML_SSOT"
    assert dashboard_json["generated_at"] == "20260605T000000Z"
    assert dashboard_json["requirements"] == 3

    manifest_json = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_json["derivatives_are_system_of_record"] is False
    assert set(manifest_json["outputs"]) == {"excel", "html", "trace", "dashboard", "checkpoint"}
    assert set(manifest_json["output_hashes"]) == {"excel", "html", "trace", "dashboard", "checkpoint"}
    assert all(len(value) == 64 for value in manifest_json["output_hashes"].values())


def test_generate_outputs_is_deterministic_for_hash_manifest(tmp_path: Path) -> None:
    first = generate_outputs(
        contract_path=CONTRACT,
        schema_path=SCHEMA,
        output_dir=tmp_path / "first" / "generated",
        checkpoint_dir=tmp_path / "first" / "checkpoints",
        generated_at="20260605T000000Z",
    )
    second = generate_outputs(
        contract_path=CONTRACT,
        schema_path=SCHEMA,
        output_dir=tmp_path / "second" / "generated",
        checkpoint_dir=tmp_path / "second" / "checkpoints",
        generated_at="20260605T000000Z",
    )

    first_manifest = json.loads(Path(first["manifest"]).read_text(encoding="utf-8"))
    second_manifest = json.loads(Path(second["manifest"]).read_text(encoding="utf-8"))

    assert first_manifest["output_hashes"] == second_manifest["output_hashes"]
