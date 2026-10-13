import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import render_portal_tiles as rpt


def test_checked_in_portal_matches_ssot():
    assert rpt.main(["--check"]) == 0


def test_traceability_is_computed_from_chain_status():
    trace = {"chains": [{"status": "complete"}, {"status": "partial"}, {"status": "complete"}, {"status": "partial"}]}
    tile = rpt.traceability_tile(trace)
    assert ">50%<" in tile
    assert "2 of 4 chains complete" in tile
    assert "status partial" in tile


def test_traceability_all_complete_is_ready():
    tile = rpt.traceability_tile({"chains": [{"status": "complete"}]})
    assert ">100%<" in tile and "status ready" in tile


def test_traceability_without_chains_does_not_invent_a_number():
    assert ">n/a<" in rpt.traceability_tile({})


def test_release_readiness_is_labelled_declared():
    runtime = {
        "runtime": {"version": "W007", "generated_on": "2026-06-05"},
        "coverage_metrics": {"release_readiness_percent": 72},
    }
    tile = rpt.readiness_tile(runtime)
    assert ">72%<" in tile
    assert "declared W007 2026-06-05, not measured" in tile


def test_render_requires_markers():
    try:
        rpt.render("<html></html>", "<b>x</b>", "docs/x.html")
    except SystemExit as exc:
        assert "docs/x.html: portal-tiles markers not found" in str(exc)
    else:
        raise AssertionError("render() accepted a page without markers")


def test_render_replaces_only_the_marked_block():
    page = f"<p>before</p>{rpt.BEGIN}old{rpt.END}<p>after</p>"
    out = rpt.render(page, rpt.traceability_tile({"chains": [{"status": "partial"}]}))
    assert out.startswith("<p>before</p>") and out.endswith("<p>after</p>")
    assert "old" not in out and ">0%<" in out


def test_every_dashboard_page_is_driven_by_ssot():
    pages = {path.relative_to(rpt.REPO_ROOT).as_posix() for path in rpt._page_blocks(rpt.load_ssot())}
    assert pages == {
        "docs/index.html",
        "docs/dashboards/traceability.html",
        "docs/dashboards/executive.html",
        "docs/dashboards/governance.html",
    }


def test_missing_references_are_counted_per_chain_field():
    trace = {"chains": [
        {"rtm_reference": "RTM-1", "contractual_gap_reference": "", "clarification_reference": "C", "answer_reference": None},
        {"rtm_reference": "RTM-2", "contractual_gap_reference": "G", "clarification_reference": "C", "answer_reference": "A"},
    ]}
    tile = rpt.missing_references_tile(trace)
    assert ">2<" in tile and "status partial" in tile


def test_review_gate_is_labelled_declared():
    runtime = {
        "runtime": {"version": "W007", "generated_on": "2026-06-05"},
        "coverage_metrics": {"review_gate_completion_percent": 70},
    }
    tile = rpt.review_gate_tile(runtime)
    assert ">70%<" in tile and "not measured" in tile


def test_governance_tiles_read_counts_and_risks():
    tiles = rpt.governance_tiles(
        {"artifact_counts": {"governance_controls": 4, "validation_workflows": 2}},
        {"open_risks": {"count": 0, "highest_severity": "low"}},
    )
    assert ">4<" in tiles and ">2<" in tiles
    assert ">0<" in tiles and "highest low" in tiles and "status partial" not in tiles
