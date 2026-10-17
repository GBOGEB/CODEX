"""Contract QA: no evidence promotion during Mycelium federation crosswalk."""
import json
from pathlib import Path
from scripts.missioncontrol_federated_crosswalk import build
from mission_control.mycelium.continuity.mycelium_continuity.graph import validate_graph

SOURCE = Path(__file__).resolve().parents[1] / "docs/data/missioncontrol_federated_dag_v1.json"


def test_crosswalk_validates_against_existing_mycelium() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    g = build(data)
    check = validate_graph(g)
    assert check["nodes"] == 18
    assert check["edges"] == 20
    assert check["sipoc_edges"] == 12
    assert all(e["binding"] == "DECLARED" for e in g["edges"])
    assert all(n["evidence"] == "DECLARED" for n in g["nodes"])
    assert g["dispatch_authorized"] is False
    assert g["native_rex_receipts_accepted"] is None
    assert g["master_dags_canonical_path"] is None
    assert g["first_admitted_main_merge"] is None


def test_crosswalk_rejects_mutation_claim() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    data["snapshot"]["mutation_enabled"] = True
    try:
        build(data)
    except AssertionError:
        pass
    else:
        raise AssertionError("mutation promotion not rejected")
