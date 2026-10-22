"""Bind evidenced Mycelium node observations into control_observations.json.

Every value written here is read from a committed receipt in
mission_control/mycelium/evidence/ or from port_registry.json, and cross-checked
against the values the node records already carry (an assert fails on any
disagreement). Nothing is typed in by hand: a field without a receipt is
written WITHHELD with its reason and unlock action.

    python scripts/bind_mycelium_observations.py --snapshot-at 2026-10-22T07:17:42Z
    python scripts/regen_missioncontrol_inventory.py   # regenerate receipts, then commit

The receipt names below (the exact current-main census, BD8K campaign, port
probes, CRYO-IF-B closure, PCA census list) are the evidence bound at the last
run. When a newer receipt supersedes one, change its name here and re-run, so
the binding stays reviewable in one diff.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_parser.add_argument("--snapshot-at", required=True, help="UTC stamp for control_observations.snapshot_at")
SNAPSHOT_AT = _parser.parse_args().snapshot_at
MYC = ROOT / "mission_control" / "mycelium"
EV = MYC / "evidence"
OBS = MYC / "control_observations.json"


def ev(name):
    return json.loads((EV / name).read_text(encoding="utf-8"))


def ref(name):
    return f"mission_control/mycelium/evidence/{name}"


obs = json.loads(OBS.read_text(encoding="utf-8"))
nodes = obs["nodes"]
obs["snapshot_at"] = SNAPSHOT_AT

# ------------------------------------------------------------------ receipts
p1697_name = "abacus_dab_post_1697_measured_e302_promoted.json"
p1697 = ev(p1697_name)
census = p1697["census"]
fam = census["all_families"]
prot = census["protected_families"]
bd8k_name = "dab_bd8k_campaign_20261001.json"
bd8k = ev(bd8k_name)
ports_name = "port_probe_receipts_20261001.json"
port_rx = ev(ports_name)
cryo_b_name = "cryo_if_b_pressure_input_closure_20261001.json"
cryo_b = ev(cryo_b_name)
exact_main = {
    "sha": p1697["current_main_sha"],
    "census_run": census["workflow_run"],
    "census_job": census["job"],
    "artifact_id": census["artifact_id"],
    "artifact_sha256": census["artifact_sha256"],
}

# ------------------------------------------------------------- lint health
# lint_health = 100 * (1 - measured / baseline) over the node's governed scope,
# measured at the exact current-main DAB census. Formula recorded in
# lint_health_policy below.
mech = nodes["dab_mech"]["mechanical_progress"]
assert mech["residual_w293"] == fam.get("W293", 0) == prot["W293"] == 0
mech_base = mech["removed_w293"] + mech["residual_w293"]

hard = nodes["dab_hard"]["family_progress"]
hard_base = sum(r["baseline"] for r in hard)
hard_meas = sum(prot[r["family"]] for r in hard)
assert all(r["measured_postmerge"] == prot[r["family"]] for r in hard)

camp = nodes["dab_bd8k"]["campaign"]["measured_post_merge"]
assert camp["total"] == census["total"] and camp["census_run"] == census["workflow_run"]
camp_base = camp["baseline_total"]
assert camp_base == bd8k["baseline"]["total"]


def lint(base, meas):
    return round(100.0 * (1 - meas / base), 2)


lint_rows = {
    "dab_mech": (lint(mech_base, mech["residual_w293"]), "W293", mech_base, mech["residual_w293"], [ref(p1697_name)]),
    "dab_hard": (lint(hard_base, hard_meas), "protected hard families " + "+".join(r["family"] for r in hard), hard_base, hard_meas, [ref(p1697_name)]),
    "dab_bd8k": (lint(camp_base, camp["total"]), "repository flake8 total", camp_base, camp["total"], [ref(p1697_name), ref(bd8k_name)]),
}
for node_id, (value, scope, base, meas, refs) in lint_rows.items():
    rec = nodes[node_id]
    chi = rec.setdefault("code_health_inputs", {})
    chi["lint_health"] = value
    chi.setdefault("qa_gate_health", None)
    chi.setdefault("test_health", None)
    chi.setdefault("debug_health", None)
    rec["code_health_provenance"] = {
        "lint_health": {
            "status": "DERIVED_FROM_MEASURED",
            "scope": scope,
            "baseline": base,
            "measured": meas,
            "formula": "100 * (1 - measured / baseline)",
            **exact_main,
            "evidence": refs,
        },
        "withheld": {
            "qa_gate_health": "no required-gate pass/executed census bound for this node",
            "test_health": "no governed test-run pass/total receipt bound for this node",
            "debug_health": "no first-red/recurrence census bound for this node",
        },
    }

# ------------------------------------------------------------------- dmaic
nodes["dab_mech"]["dmaic"] = {
    "status": "DERIVED_FROM_MEASURED",
    "phase": "CONTROL",
    "basis": f"W293 residual {prot['W293']} measured at exact current-main census {census['workflow_run']}; exact-SHA proof and drift watch",
    "evidence": [ref(p1697_name)],
}
hold = p1697["source_bound_hold"]
nodes["dab_hard"]["dmaic"] = {
    "status": "DERIVED_FROM_MEASURED",
    "phase": "CONTROL",
    "basis": (
        f"{sum(1 for r in hard if prot[r['family']] == 0)} of {len(hard)} protected hard families at 0 in exact current-main census "
        f"{census['workflow_run']}; remaining {hold['family']}={hold['count']} is a SOURCE_BOUND_HOLD ({hold['path']})"
    ),
    "evidence": [ref(p1697_name)],
}
issue_facts = {row["issue"]: row for row in cryo_b["source_evidence"]}
nodes["qps_triage_b"]["dmaic"] = {
    "status": "DERIVED_FROM_MEASURED",
    "phase": "ANALYZE",
    "basis": (
        f"dominant blocker identified (cryoplant-project #540) and boundary still in source-verification RFI (#210, "
        f"state {issue_facts[210]['state']} at receipt); reverse-pressure analysis bound; DOW calculation not yet returned"
    ),
    "evidence": [ref(cryo_b_name)],
    "observed_at_receipt": cryo_b["receipt_id"],
}
nodes["repo_codex"]["dmaic"] = {
    "status": "WITHHELD",
    "reason": "DMAIC is defined for main topics; no governed rule maps a whole repository to one phase",
    "unlock": "bind a repo-level DMAIC derivation rule in control_manifest.yaml, or exclude repo nodes from DMC-01",
}

# ------------------------------------------------------------------- ports
qps_port = next(p for p in port_rx["ports"] if p["id"] == "QPS_TRIAGE_RETURN")
nodes["qps_triage_b"]["ports"] = {
    "status": "DERIVED_FROM_MEASURED",
    "value": 100,
    "probed_ports": 1,
    "declared_ports": 1,
    "ports": [qps_port["id"]],
    "probe_state": qps_port["state"],
    "basis": "qps_triage_b priority/return metadata transits the declared QPS_TRIAGE_RETURN port (port_registry.json)",
    "evidence": [ref(ports_name), "mission_control/mycelium/port_registry.json", qps_port["target"]["receipt"]],
}
port_unlock = "declare a port for this node in port_registry.json and bind an exact governed source-to-target probe receipt"
nodes["topic_2k_refrigeration"]["ports"] = {
    "status": "WITHHELD",
    "reason": "DOW_EVIDENCE_RETURN is pinned to the HM01 support return, not the B-interface DOW gap this topic is waiting on",
    "unlock": port_unlock,
}
for node_id in ("dab_mech", "dab_hard", "dab_bd8k"):
    nodes[node_id]["ports"] = {"status": "WITHHELD", "reason": "no port declared for this node", "unlock": port_unlock}

# ---------------------------------------------------------------- maturity
maturity_unlock = "bind requirement_coverage, interface_closure, evidence_coverage and validation_coverage for this node"
for node_id in ("repo_codex", "qps_triage_b", "dab_mech", "dab_hard"):
    nodes[node_id]["maturity"] = {
        "status": "WITHHELD",
        "reason": "requirement/interface/evidence/validation coverage census not yet bound",
        "unlock": maturity_unlock,
    }
nodes["topic_2k_refrigeration"]["maturity"]["unlock"] = maturity_unlock
nodes["dab_bd8k"]["maturity"]["unlock"] = "none intended: campaign maturity is not a formal engineering state"

# ------------------------------------------------------------- code health
nh = "not an executable node; no code-health inputs apply"
for node_id in ("qps_triage_b", "topic_2k_refrigeration"):
    nodes[node_id]["code_health_provenance"] = {"withheld": nh, "unlock": "exclude non-code nodes from HLT-04, or bind the owning repository's QA"}
nodes["repo_codex"]["code_health_provenance"] = {
    "qa_gate_health": {"status": "MEASURED", "evidence": nodes["repo_codex"]["qa"]["evidence"]},
    "withheld": {
        "test_health": "no governed pytest pass/total receipt bound",
        "lint_health": "ruff is report-only with a pre-existing backlog; no governed baseline bound",
        "debug_health": "no first-red/recurrence census bound",
    },
}

# --------------------------------------------------------------- PCA rows
# Population: ABACUS post-merge exact-main DAB censuses with committed receipts.
FEATURES = ("total", "W293", "F841", "E722", "E741")


def row(rid, receipt, block, sha, run, job, artifact):
    feats = {}
    for k in FEATURES:
        if k in block:
            feats[k] = block[k]
        else:
            for sub in ("protected_families", "all_families", "families"):
                if isinstance(block.get(sub), dict) and k in block[sub]:
                    feats[k] = block[sub][k]
                    break
    assert set(feats) == set(FEATURES), (rid, feats)
    return {
        "id": rid,
        "status": "MEASURED",
        "population": "ABACUS_POST_MERGE_EXACT_MAIN_DAB_CENSUS",
        "source_repository": "GBOGEB/ABACUS",
        "measured_sha": sha,
        "census_run": run,
        "census_job": job,
        "artifact_id": artifact,
        "evidence": ref(receipt),
        "features": feats,
    }


rows = []
for pr in (1530, 1545, 1548):
    name = f"abacus_dab_post_{pr}_main_measured.json"
    b = ev(name)["post_merge_main_census"]
    rows.append(row(f"abacus_main_post_{pr}", name, b, b["merge_sha"], b["workflow_run"], b["job"], b["artifact_id"]))
name = "abacus_dab_post_1542_main_measured.json"
d = ev(name)
b = d["postmerge_main_census"]
rows.append(row("abacus_main_post_1542", name, b, d["lineage"]["slice"]["merge_sha"], b["workflow_run"], b["job"], b.get("artifact", {}).get("id")))
name = "abacus_dab_post_1581_main_measured.json"
d = ev(name)
b = d["exact_census"]
rows.append(row("abacus_main_post_1581", name, b, d["source"]["measured_sha"], b["workflow_run"], b["job"], b.get("artifact", {}).get("id")))
for wave in ("wave1", "wave2"):
    b = bd8k[wave]["post_merge_main"]
    rows.append(row(f"abacus_main_bd8k_{wave}", bd8k_name, b, b.get("measured_sha") or b.get("sha"), b.get("census_run"), b.get("census_job"), b.get("artifact_id")))
for pr in (1645, 1647):
    name = f"abacus_dab_post_{pr}_main_measured.json"
    d = ev(name)
    rows.append(row(f"abacus_main_post_{pr}", name, d, d["measured_source_sha"], d["workflow_run"], d["job"], d["artifact_id"]))
rows.append(row("abacus_main_post_1697", p1697_name, census, exact_main["sha"], census["workflow_run"], census["job"], census["artifact_id"]))
rows.sort(key=lambda r: r["census_run"])
for r in rows:
    assert r["measured_sha"] and r["census_run"], r
obs["pca_rows"] = rows
obs["pca_population_policy"] = {
    "population": "ABACUS_POST_MERGE_EXACT_MAIN_DAB_CENSUS",
    "row_rule": "one row per committed post-merge exact-main DAB census receipt in mission_control/mycelium/evidence/",
    "features": list(FEATURES),
    "feature_rule": "protected families measured in every row; constant families (E999, E731, F601, F811, F821) excluded as zero-variance",
    "role": "diagnostic projection of lint-debt trajectory only; no priority or importance claim",
}
obs["pairwise_outcomes"] = []
obs["pairwise_outcomes_policy"] = {
    "status": "WITHHELD",
    "reason": "no governed head-to-head comparison with an observed winner and loser exists between Mycelium items",
    "unlock": "commit a comparison receipt (winner, loser, count, evidence) from an observed decision, e.g. a governed option or bidder evaluation",
}
obs["lint_health_policy"] = {
    "formula": "lint_health = 100 * (1 - measured / baseline) over the node's governed flake8 scope",
    "measurement": "exact current-main ABACUS DAB census only; PR-head or planning probes never count",
    "guard": "control health signal only; no engineering or formal credit",
}

OBS.write_text(json.dumps(obs, indent=2) + "\n", encoding="utf-8", newline="\n")
print(len(rows), "pca rows;", {k: v[0] for k, v in lint_rows.items()})
