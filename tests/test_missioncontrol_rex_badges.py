import importlib.util
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_missioncontrol_rex_badges.py"
spec = importlib.util.spec_from_file_location("build_missioncontrol_rex_badges", SCRIPT)
rex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rex)

CONTRACT = yaml.safe_load(rex.CONTRACT.read_text(encoding="utf-8"))
LEDGER = yaml.safe_load(rex.LEDGER.read_text(encoding="utf-8"))
RECORD = {
    "rex_id": "REX-T-001",
    "signature": "RUNTIME.GITHUB_ACTIONS.ZERO_STEP_PREEXECUTION",
    "family": "RUNTIME",
    "frequency": {"observed_count": 8, "unit": "jobs"},
    "recurrence": "CROSS_WORKFLOW_RECURRING",
    "last_seen": 34578800214,
    "action_moniker": "RUNTIME",
    "repair_method": "repair runner allocation",
    "control_guard": ["distinguish zero steps"],
    "control_status": "DEFERRED",
    "lookup_tags": ["runner"],
}


def _build(lanes=(), events=(), records=(RECORD,)):
    return rex.build(
        CONTRACT,
        {
            "records": list(records),
            "measurement_window": {"label": "W", "date": "2026-09-11"},
        },
        {"lanes": list(lanes)},
        {"events": list(events)},
    )


def test_committed_projection_is_current_and_mirrored():
    expected = rex.build(
        CONTRACT,
        LEDGER,
        json.loads(rex.CONTROL_PLANE.read_text(encoding="utf-8")),
        json.loads(rex.CONTROL_EVENTS.read_text(encoding="utf-8")),
    )
    canonical = json.loads(rex.OUTPUT.read_text(encoding="utf-8"))
    pages = json.loads(rex.PAGES_OUTPUT.read_text(encoding="utf-8"))
    assert canonical == pages == json.loads(json.dumps(expected))


def test_projection_carries_contract_compact_fields_for_every_ledger_record():
    payload = _build(records=LEDGER["records"])
    assert payload["omnipresent_badge"] is True
    assert payload["compact_fields"] == CONTRACT["ui"]["compact_fields"]
    assert set(payload["records"]) == {r["rex_id"] for r in LEDGER["records"]}
    for record in payload["records"].values():
        for field in CONTRACT["ui"]["compact_fields"]:
            assert field in record
        assert record["seen_before"] is True


def test_exact_signature_or_id_is_seen_exact():
    payload = _build(
        lanes=[
            {
                "id": "L1",
                "current_atom": "ATOM",
                "blocker": "blocked by runtime.github_actions.zero_step_preexecution",
            }
        ],
        events=[{"id": "EV-1", "type": "FIRST_RED", "summary": "see REX-T-001"}],
    )
    by_key = {(b["surface"], b["item_id"]): b for b in payload["badges"]}
    assert by_key[("blocker", "L1")]["decision_hint"] == "SEEN_EXACT"
    assert by_key[("blocker", "L1")]["rex_ids"] == ["REX-T-001"]
    assert by_key[("first_red", "EV-1")]["rex_ids"] == ["REX-T-001"]
    assert by_key[("active_atom", "L1")]["decision_hint"] == "NEVER_SEEN"


def test_tag_or_family_words_alone_never_fabricate_a_match():
    payload = _build(lanes=[{"id": "L1", "blocker": "RUNTIME runner blocked"}])
    (only,) = payload["badges"]
    assert only["decision_hint"] == "NEVER_SEEN"
    assert only["rex_ids"] == []
    assert payload["similarity"] == "NOT_COMPUTED"


def test_missing_ledger_values_are_unknown_not_zero():
    payload = _build(records=[{"rex_id": "REX-T-002"}])
    record = payload["records"]["REX-T-002"]
    for field in (
        "recurrence_count",
        "recurrence_class",
        "last_seen",
        "prior_fix",
        "control_guard",
    ):
        assert record[field] == "UNKNOWN"


def test_surfaces_split_rendered_from_absent():
    payload = _build()
    show_on = CONTRACT["ui"]["show_on"]
    assert sorted(
        payload["surfaces"]["rendered"] + payload["surfaces"]["not_on_this_page"]
    ) == sorted(show_on)
    assert set(payload["surfaces"]["rendered"]) == set(rex.RENDERED_SURFACES)


def test_page_renders_badge_on_each_rendered_surface():
    js = (ROOT / "docs" / "assets" / "missioncontrol" / "control-plane.js").read_text(
        encoding="utf-8"
    )
    assert "data/missioncontrol_rex_badges.json" in js
    for surface in rex.RENDERED_SURFACES:
        assert f"rexBadge('{surface}'" in js
