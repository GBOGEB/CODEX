from __future__ import annotations

import copy
import importlib.util
import sys
import types
from pathlib import Path

import yaml

BRIDGE_ROOT = Path(__file__).resolve().parents[1] / "rtm_integration" / "contract_followup" / "alat_clarification_bridge"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_validator_accepts_current_ssot_and_resolves_registers():
    validator = load_module("alat_validate_ssot", BRIDGE_ROOT / "tools" / "validate_ssot.py")

    errors = validator.validate(
        load_yaml(BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml"),
        rtm_data=load_yaml(BRIDGE_ROOT / "RTM_LINKS.yaml"),
        offer_data=load_yaml(BRIDGE_ROOT / "OFFER_REGISTER.yaml"),
    )

    assert errors == []


def test_validator_rejects_missing_rtm_link():
    validator = load_module("alat_validate_ssot_negative", BRIDGE_ROOT / "tools" / "validate_ssot.py")
    ssot = load_yaml(BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml")
    broken_ssot = copy.deepcopy(ssot)
    broken_ssot["questions"][0]["rtm_links"] = []

    errors = validator.validate(
        broken_ssot,
        rtm_data=load_yaml(BRIDGE_ROOT / "RTM_LINKS.yaml"),
        offer_data=load_yaml(BRIDGE_ROOT / "OFFER_REGISTER.yaml"),
    )

    assert any("parent question must have at least one RTM link" in error for error in errors)


def test_validator_rejects_unresolved_register_references():
    validator = load_module("alat_validate_ssot_unresolved", BRIDGE_ROOT / "tools" / "validate_ssot.py")
    ssot = load_yaml(BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml")
    broken_ssot = copy.deepcopy(ssot)
    broken_ssot["questions"][0]["rtm_links"].append("RTM-ALAT-MISSING")
    broken_ssot["questions"][0]["offer_actions"].append("OFFER-MISSING")

    errors = validator.validate(
        broken_ssot,
        rtm_data=load_yaml(BRIDGE_ROOT / "RTM_LINKS.yaml"),
        offer_data=load_yaml(BRIDGE_ROOT / "OFFER_REGISTER.yaml"),
    )

    assert any("RTM link 'RTM-ALAT-MISSING' is not defined" in error for error in errors)
    assert any("OFFER action 'OFFER-MISSING' is not defined" in error for error in errors)


def test_generator_writes_template_outputs(tmp_path):
    generator = load_module("alat_generate_bridge", BRIDGE_ROOT / "tools" / "generate_bridge.py")
    ssot = load_yaml(BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml")

    outputs = {
        "bidder_response.md": generator.generate_markdown(ssot),
        "bidder_response.html": generator.generate_html(ssot),
        "review_checklist.md": generator.generate_review_summary(ssot),
        "stakeholder_review.md": generator.render_question_template(BRIDGE_ROOT / "templates" / "stakeholder_review.md", ssot),
        "management_summary.md": generator.render_question_template(BRIDGE_ROOT / "templates" / "management_summary.md", ssot),
    }
    for name, content in outputs.items():
        (tmp_path / name).write_text(content, encoding="utf-8")

    for name in outputs:
        assert (tmp_path / name).is_file()
    assert "{{" not in (tmp_path / "stakeholder_review.md").read_text(encoding="utf-8")
    assert "{{" not in (tmp_path / "management_summary.md").read_text(encoding="utf-8")


def test_excel_generation_path_when_openpyxl_is_available(tmp_path, monkeypatch):
    generator = load_module("alat_generate_bridge_excel", BRIDGE_ROOT / "tools" / "generate_bridge.py")
    ssot = load_yaml(BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml")

    class FakeSheet:
        title = ""

        def __init__(self):
            self.rows = []

        def append(self, row):
            self.rows.append(row)

    class FakeWorkbook:
        def __init__(self):
            self.active = FakeSheet()

        def save(self, output_path):
            output_path.write_text("fake workbook", encoding="utf-8")

    fake_openpyxl = types.ModuleType("openpyxl")
    fake_openpyxl.Workbook = FakeWorkbook
    monkeypatch.setitem(sys.modules, "openpyxl", fake_openpyxl)

    output_path = generator.generate_excel_if_available(ssot, tmp_path)

    assert output_path == tmp_path / "alat_clarification_bridge.xlsx"
    assert output_path.read_text(encoding="utf-8") == "fake workbook"


def test_workflow_installs_real_openpyxl_and_guards_bridge_tests():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "build-clarification-bridge.yml").read_text(
        encoding="utf-8"
    )

    assert "pip install PyYAML openpyxl pytest" in workflow
    assert "python -c \"import openpyxl, yaml; print(f'openpyxl={openpyxl.__version__}')\"" in workflow
    assert "test -f tests/test_alat_clarification_bridge.py" in workflow
    assert "pytest --strict-config --strict-markers tests/test_alat_clarification_bridge.py" in workflow
    assert "test -f rtm_integration/contract_followup/alat_clarification_bridge/build/alat_clarification_bridge.xlsx" in workflow
