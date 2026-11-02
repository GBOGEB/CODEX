"""Contracts for the per-lane LDAB debugger receipt adapter."""
import importlib.util
import json
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "lldb_lane_receipt.py"
SPEC = importlib.util.spec_from_file_location("lldb_lane_receipt", SOURCE)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

SHA = "a" * 40
GOOD = {
    "status": "ACCEPT",
    "real_probe_steps": 6,
    "container_id": "c0ffee1234567890",
    "host_binding": "127.0.0.1:32768",
    "image_id": "sha256:abc",
}
KW = {"lane": "L00", "source_sha": SHA, "repository": "GBOGEB/CODEX",
      "run_id": "100", "job_id": "200", "runner_id": "GitHub Actions 7"}


def test_accepted_probe_counts_as_session():
    r = M.build_lane(GOOD, **KW)
    assert r["counts_as_authenticated_session"] is True
    assert r["host_port"] == 32768 and r["host_binding"] == "127.0.0.1:32768"
    assert r["session_id"] == "100-L00-c0ffee123456" == r["port_lease_id"]
    assert r["evidence_url"].endswith("/actions/runs/100/job/200")
    assert r["authority_transfer"] is False and r["formal_credit_delta"] == 0


@pytest.mark.parametrize("probe", [
    None,
    {"status": "REJECT", "real_probe_steps": 9, "container_id": "x", "host_binding": "127.0.0.1:1"},
    {**GOOD, "real_probe_steps": 0},
    {**GOOD, "host_binding": "0.0.0.0:32768"},
    {**GOOD, "container_id": ""},
])
def test_no_evidence_is_never_a_session(probe):
    r = M.build_lane(probe, **KW)
    assert r["counts_as_authenticated_session"] is False
    assert r["session_id"] is None and r["port_lease_id"] is None
    if not probe or probe.get("status") != "ACCEPT":
        assert r["real_probe_steps"] == 0 and r["host_port"] is None


def test_missing_runner_blocks_session():
    r = M.build_lane(GOOD, **{**KW, "runner_id": None})
    assert r["counts_as_authenticated_session"] is False and r["session_id"] is None


def test_missing_job_id_leaves_evidence_url_null():
    assert M.build_lane(GOOD, **{**KW, "job_id": None})["evidence_url"] is None


@pytest.mark.parametrize("sha", ["", "abc", "g" * 40, "A" * 40])
def test_bad_sha_rejected(sha):
    with pytest.raises(ValueError):
        M.build_lane(GOOD, **{**KW, "source_sha": sha})


def test_aggregate_counts_only_real_sessions():
    lanes = [M.build_lane(GOOD, **{**KW, "lane": f"L{i:02d}"}) for i in range(3)]
    lanes.append(M.build_lane(None, **{**KW, "lane": "L03"}))
    agg = M.aggregate(lanes, expected=4)
    assert agg["authenticated_sessions"] == 3 and agg["total_real_probe_steps"] == 18
    assert agg["lanes_not_counted"] == ["L03"] and agg["all_lanes_reported"]
    assert M.aggregate(lanes[:3], expected=4)["all_lanes_reported"] is False
    assert M.aggregate(lanes + [lanes[0]], expected=4)["all_lanes_reported"] is False


def test_aggregate_flags_mixed_source_shas():
    a = M.build_lane(GOOD, **KW)
    b = M.build_lane(GOOD, **{**KW, "lane": "L01", "source_sha": "b" * 40})
    assert M.aggregate([a, b])["single_source_sha"] is False


def test_cli_roundtrip_and_exit_codes(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "100")
    monkeypatch.setenv("RUNNER_NAME", "r1")
    probe = tmp_path / "p.json"
    probe.write_text(json.dumps(GOOD))
    out = tmp_path / "o" / "lane.json"
    assert M.main(["lane", "--probe", str(probe), "--lane", "L00",
                   "--source-sha", SHA, "--job-id", "200", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["counts_as_authenticated_session"] is True
    agg = tmp_path / "agg.json"
    assert M.main(["aggregate", "--lanes", str(out), "--expected", "1", "--out", str(agg)]) == 0
    assert M.main(["aggregate", "--lanes", str(out), "--expected", "2", "--out", str(agg)]) == 2
    missing = tmp_path / "none.json"
    assert M.main(["lane", "--probe", str(missing), "--lane", "L01",
                   "--source-sha", SHA, "--out", str(tmp_path / "l1.json")]) == 0
    assert json.loads((tmp_path / "l1.json").read_text())["probe_status"] == "MISSING"
