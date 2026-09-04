from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "governance" / "w52_repo_coverage.yaml"


def load_control():
    return yaml.safe_load(CONTROL.read_text())


def test_open_denominator_does_not_publish_whole_repo_ratio():
    data = load_control()
    assert data["coverage"]["denominator_state"] == "OPEN"
    assert data["coverage"]["publish_ratio"] is False


def test_penetration_is_separate_from_coverage():
    data = load_control()
    assert data["penetration"]["cryo_property_router_snapshot"]["coarse_fraction"] == 0.6
    assert data["coverage"]["denominator_state"] == "OPEN"


def test_dormant_modules_remain_visible():
    data = load_control()
    dormant = data["penetration"]["dormant_available"]
    assert "docs/wave_packages/runtime/federation_bridge_cli.py" in dormant
    assert "docs/wave_packages/runtime/runtime_bridge.py" in dormant
    assert "scripts/agent_runtime_monitor.py" in dormant


def test_bidirectional_roundtrip_requires_both_execution_legs():
    metrics = load_control()["bidirectionality"]["required_metrics"]
    assert "forward_executed" in metrics
    assert "reverse_executed" in metrics
    assert "roundtrip_success" in metrics


def test_no_formal_credit_created():
    assert load_control()["formal_credit_delta"] == 0
