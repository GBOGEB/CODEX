"""The GISTAU properties layer consumes ABACUS physics; it never governs it."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from gistau_ch15.properties import qplant_hepak_policy as policy
from gistau_ch15.properties.backend_selector import (
    CROSSCHECK_ONLY,
    VALIDATION_REFERENCE_ONLY,
    availability_report_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH = REPO_ROOT / "governance" / "qps" / "keb_cryo_property_capability_graph.yaml"


def _tool():
    spec = importlib.util.spec_from_file_location(
        "verify_physics_authority_pin", REPO_ROOT / "tools" / "verify_physics_authority_pin.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pin():
    return _tool().load_pin()


def test_pin_is_well_formed_and_meta_checksum_current(pin):
    _tool().check_pin(pin)


def test_meta_checksum_detects_any_pin_edit(pin):
    tool = _tool()
    tampered = yaml.safe_load(yaml.safe_dump(pin))
    tampered["pinned_files"][0]["sha256"] = "0" * 64
    with pytest.raises(tool.PinError, match="meta_checksum"):
        tool.check_pin(tampered)


def test_stale_checkout_is_rejected(pin, tmp_path):
    problems = _tool().verify_checkout(pin, tmp_path)
    assert any(p.startswith("STALE_SHA") for p in problems)
    assert any(p.startswith("MISSING") for p in problems)


def test_no_gistau_backend_governs():
    rows = availability_report_rows()
    assert rows
    roles = {row["name"]: row["authority_role"] for row in rows}
    assert set(roles.values()) <= {CROSSCHECK_ONLY, VALIDATION_REFERENCE_ONLY}
    assert roles["nist_gistau_reference"] == VALIDATION_REFERENCE_ONLY
    assert all("GBOGEB/ABACUS" in row["governing_authority"] for row in rows)


def test_codex_lambda_matches_pinned_abacus_lambda(pin):
    assert policy.COOLPROP_HE_MIN_K == pin["pinned_constants"]["lambda_point_K"]


def test_policy_parity_is_recorded_not_silent(pin):
    """Recompute CODEX vs pinned-ABACUS QPLANT routing; the recorded divergence must match."""
    lo, hi = pin["pinned_constants"]["qplant_hepak_band_K"]
    parity = pin["policy_parity"]
    diverging = []
    for t in parity["probes_K"]:
        abacus = "HEPAK" if lo <= t <= hi else "COOLPROP"
        if policy.governing_provider_for_temperature(t) != abacus:
            diverging.append(t)
    assert diverging == parity["diverging_probes_K"]
    assert (parity["status"] == "PARITY") == (not diverging)


def test_capability_graph_declares_crosscheck_node_and_router_stays_planned():
    graph = yaml.safe_load(GRAPH.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert nodes["KEB-NODE-GISTAU-CROSSCHECK"]["authority_role"] == CROSSCHECK_ONLY
    assert nodes["EXT-NODE-ABACUS-HE4-PROPERTY"]["pin"] == "governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml"
    assert nodes["KEB-NODE-CRYO-PROPERTY-ROUTER"]["lifecycle"] == "PLANNED"
    edges = {e["id"]: e for e in graph["edges"]}
    assert edges["KEB-EDGE-010"]["source"] == "KEB-NODE-GISTAU-CROSSCHECK"
    assert edges["KEB-EDGE-010"]["target"] == "EXT-NODE-ABACUS-HE4-PROPERTY"
    metrics = graph["activation_metrics"]
    assert metrics["discovered_nodes"] == len(graph["nodes"])


def test_committed_review_page_is_current():
    spec = importlib.util.spec_from_file_location(
        "render_physics_authority_review", REPO_ROOT / "tools" / "render_physics_authority_review.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    committed = (REPO_ROOT / "docs" / "gistau-ch15" / "physics_authority.html").read_text(encoding="utf-8")
    assert committed == module.render(), "regenerate: PYTHONPATH=src python tools/render_physics_authority_review.py"


def _render_with_parity(parity_overrides):
    spec = importlib.util.spec_from_file_location(
        "render_physics_authority_review", REPO_ROOT / "tools" / "render_physics_authority_review.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tool = _tool()
    pin = tool.load_pin()
    pin["policy_parity"] = {**pin["policy_parity"], **parity_overrides}
    if "resolution" in parity_overrides and parity_overrides["resolution"] is None:
        pin["policy_parity"].pop("resolution")
    pin["meta_checksum_sha256"] = tool.meta_checksum(pin)  # re-seal: parity is checksummed
    return module.render(pin)


def test_parity_still_requires_explicit_acceptance():
    html = _render_with_parity({"status": "PARITY", "diverging_probes_K": []})
    assert "awaits your acceptance" in html
    assert "Nothing needs a decision" not in html


def test_divergence_text_is_authority_neutral_without_recorded_resolution():
    html = _render_with_parity({"status": "DIVERGED", "diverging_probes_K": [1.8], "resolution": None})
    assert "ABACUS has to adopt" not in html
    assert "No resolution is recorded in the pin" in html

    from gistau_ch15.properties.backend_selector import (
        GOVERNING_AUTHORITY,
        select_available_backends,
    )

def test_divergence_text_uses_recorded_resolution():
    html = _render_with_parity({"status": "DIVERGED", "diverging_probes_K": [1.8], "resolution": "CODEX re-mirrors ABACUS"})
    assert "Recorded resolution: CODEX re-mirrors ABACUS" in html
@pytest.mark.parametrize(
    "mutate",
    [
        lambda p: p["authority"].__setitem__("runtime_dependency", "CoolProp==9.9.9"),
        lambda p: p["pinned_files"][0].__setitem__("git_blob_sha", "f" * 40),
        lambda p: p["pinned_files"][0].__setitem__("role", "something else"),
        lambda p: p["local_roles"].__setitem__("src/gistau_ch15/properties", "GOVERNING"),
        lambda p: p["policy_parity"].__setitem__("status", "DIVERGED"),
        lambda p: p["output_crosscheck"].__setitem__("output_checksum_sha256", "0" * 64),
    ],
)
def test_meta_checksum_covers_every_authority_bearing_field(pin, mutate):
    tool = _tool()
    tampered = yaml.safe_load(yaml.safe_dump(pin))
    mutate(tampered)
    with pytest.raises(tool.PinError, match="meta_checksum"):
        tool.check_pin(tampered)


def test_checkout_blob_ids_are_verified(pin, tmp_path):
    import subprocess

    tool = _tool()
    repo = tmp_path / "abacus"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    f = pin["pinned_files"][0]
    target = repo / f["path"]
    target.parent.mkdir(parents=True)
    target.write_text("content\n")
    tampered = yaml.safe_load(yaml.safe_dump(pin))
    tampered["pinned_files"] = [dict(f, sha256=__import__("hashlib").sha256(b"content\n").hexdigest(), git_blob_sha="a" * 40)]
    problems = tool.verify_checkout(tampered, repo)
    assert any(p.startswith("BLOB_DRIFT") for p in problems)
    assert not any(p.startswith("CONTENT_DRIFT") for p in problems)
