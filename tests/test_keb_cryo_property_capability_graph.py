from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "governance" / "qps" / "keb_cryo_property_capability_graph.yaml"


def load_graph():
    return yaml.safe_load(GRAPH.read_text())


def test_abacus_is_external_physics_authority():
    graph = load_graph()
    assert graph["external_authority"]["repository"] == "GBOGEB/ABACUS"
    assert graph["external_authority"]["rule"] == "CODEX_MUST_NOT_DUPLICATE_OR_SELF_PROMOTE_PHYSICS_PROVIDER"


def test_dormant_runtime_nodes_are_explicit():
    graph = load_graph()
    dormant = {n["id"] for n in graph["nodes"] if n["lifecycle"] == "DORMANT_AVAILABLE"}
    assert {
        "KEB-NODE-FED-BRIDGE-CLI",
        "KEB-NODE-RUNTIME-BRIDGE",
        "KEB-NODE-AGENT-MONITOR",
    } <= dormant


def test_cryo_router_is_not_yet_on_duty():
    graph = load_graph()
    router = next(n for n in graph["nodes"] if n["id"] == "KEB-NODE-CRYO-PROPERTY-ROUTER")
    assert router["lifecycle"] == "PLANNED"


def test_heii_fail_closed_gate_exists():
    graph = load_graph()
    gate = graph["promotion_gates"]["BOUND_TO_TESTED"]
    assert "HeII_invalid_provider_fail_closed" in gate


def test_formal_credit_remains_zero():
    assert load_graph()["formal_credit_delta"] == 0
