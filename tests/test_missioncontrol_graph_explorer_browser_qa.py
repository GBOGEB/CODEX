from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qa_missioncontrol_graph_explorer.py"
WORKFLOW = ROOT / ".github" / "workflows" / "missioncontrol-graph-explorer-browser-qa.yml"
MANIFEST = ROOT / "mission_control" / "mycelium" / "control_manifest.yaml"


def test_graph_explorer_browser_qa_contract_is_governed() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")

    for token in (
        "plotly_active",
        "plotly_fallback",
        "smart_label_density",
        "smart_label_count",
        "accessible_node_names",
        "keyboard_node_activation",
        "accessible_named_nodes",
        "keyboard_access_pass",
        "engineering",
        "control",
        "observability",
        "golden-focus",
        "single-focus",
        "horizontal_overflow",
        "interaction_receipt.json",
        "authority_transfer",
        "formal_credit_delta",
        "engineering_credit_delta",
    ):
        assert token in script

    assert "missioncontrol-graph-explorer-browser-qa" in workflow
    assert "render_missioncontrol_graph_matplotlib.py" in workflow
    assert "qa_missioncontrol_graph_explorer.py" in workflow
    assert "graph_explorer_browser_qa" in manifest


def test_browser_qa_does_not_depend_on_live_plotly_cdn() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert "PLOTLY_STUB" in script
    assert "route.fulfill" in script
    assert "intentionally unavailable for fallback QA" in script


def test_graph_explorer_nodes_keep_accessible_names_when_labels_hide() -> None:
    html = (ROOT / "docs" / "missioncontrol_graph_explorer.html").read_text(
        encoding="utf-8"
    )
    assert 'role="button"' in html
    assert 'aria-label="' in html
    assert "e.key==='Enter'||e.key===' '" in html
    assert "label-hidden" in html
