"""Read-only candidate REX roll-up for CODE PURPLE and MissionControl.

Input is the governed repository-return schema, not scrape results or assumed
work done by an agent. This never writes a merge gate, source ledger or QPS SSOT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "federation/rex/returns/ABACUS_CODE_PURPLE_20261012_REX_RETURN.yaml"
OUTPUT = ROOT / "docs/data/code_purple_rex_rollup.json"
SCHEMA = "code-purple.rex-control-metrics/1.0"
REX_SCHEMA = "gbogeb-repo-rex-return/1.0"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"OPEN", "CONTAINED", "REPAIRED", "VERIFIED",
            "CONTROLLED", "DEFERRED", "SUPERSEDED"}
FAMILIES = {"SEMANTIC", "NAMESPACE", "LINEAGE", "AUTHORITY",
            "RUNTIME", "CI_CD", "VALIDATION", "DATA_SSOT", "ARTIFACT",
            "FEDERATION", "SECURITY", "PERFORMANCE", "UX_LOOKUP"}
ACTIVE = {"OPEN", "CONTAINED", "DEFERRED"}
COMPLETE = {"VERIFIED", "CONTROLLED"}
SEVERITY_WEIGHT = 10
STATUS_WEIGHT = {
    "OPEN": 5, "DEFERRED": 5, "CONTAINED": 4,
    "REPAIRED": 3, "VERIFICATION_PENDING": 4,
    "VERIFIED": 1, "CONTROLLED": 1, "SUPERSEDED": 0,
}


def valid_evidence_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    url = urlparse(value)
    return (
        url.scheme == "https"
        and url.netloc == "github.com"
        and url.path.startswith("/GBOGEB/")
        and not url.username and not url.password
    )


def validate(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict) or data.get("schema") != REX_SCHEMA:
        raise ValueError("expected canonical repository REX return schema")
    if data.get("repo") != "GBOGEB/ABACUS":
        raise ValueError("REX return must retain originating repo authority")
    state = data.get("repo_state")
    if not isinstance(state, dict):
        raise TypeError("repo_state missing")
    for key in ("main_sha", "head_sha", "companion_p0_head_sha"):
        if not FULL_SHA.fullmatch(str(state.get(key) or "")):
            raise ValueError(f"{key} must contain a full source SHA")
    if state.get("current_merge") != "NOT_PROVEN":
        raise ValueError("candidate REX may not assert ABACUS merge")
    if state.get("security_review_admission") != "NOT_PROVEN":
        raise ValueError("candidate REX may not assert security admission")
    contract = data.get("return_contract") or {}
    if (contract.get("authority_transfer") is not False
            or contract.get("formal_credit_delta") != 0
            or contract.get("engineering_credit_delta") != 0
            or contract.get("promotion_state") != "CANDIDATE_GLOBAL_REX_NOT_ACCEPTED"):
        raise ValueError("unauthorized promotion or control credit")
    rows = data.get("records")
    if not isinstance(rows, list) or not rows:
        raise ValueError("records must be nonempty")
    ids: set[str] = set()
    signatures: set[str] = set()
    for record in rows:
        if not isinstance(record, dict):
            raise TypeError("invalid REX record")
        ident = record.get("rex_id")
        signature = record.get("signature")
        if not isinstance(ident, str) or not ident.startswith("REX-ABACUS-"):
            raise ValueError("unbound REX identifier")
        if not isinstance(signature, str) or "." not in signature:
            raise ValueError("unbound REX signature")
        if ident in ids or signature in signatures:
            raise ValueError("duplicate identity/signature must update existing REX")
        ids.add(ident)
        signatures.add(signature)
        stars = record.get("severity_stars")
        if type(stars) is not int or not 1 <= stars <= 5:
            raise ValueError("severity must be an integer 1..5")
        if record.get("family") not in FAMILIES:
            raise ValueError("unknown REX family")
        if record.get("control_status") not in STATUSES:
            raise ValueError("unknown control status")
        origins = record.get("repo") or {}
        if origins.get("primary") != "GBOGEB/ABACUS":
            raise ValueError("return cannot transfer source authority")
        frequency = record.get("frequency") or {}
        count = frequency.get("observed_count")
        if type(count) is not int or count < 1:
            raise ValueError("frequency needs a positive directly observed count")
        if not frequency.get("unit") or not frequency.get("measurement_window"):
            raise ValueError("frequency needs explicit unit and window")
        verification = record.get("verification") or {}
        if not verification.get("result"):
            raise ValueError("missing verification disposition")
        if not valid_evidence_url(verification.get("source_url")):
            raise ValueError("missing primary trustworthy evidence link")
        if record["control_status"] in COMPLETE and not (
            str(verification["result"]).startswith("PASS")
        ):
            raise ValueError("cannot label controlled/verified without a PASS")
    summary = data.get("summary") or {}
    if summary.get("total_records") != len(rows):
        raise ValueError("summary record_count must match source records")
    if summary.get("open_or_deferred") != sum(
        r["control_status"] in ACTIVE for r in rows
    ):
        raise ValueError("open count disagrees with source evidence")
    if summary.get("verified_or_controlled") != sum(
        r["control_status"] in COMPLETE for r in rows
    ):
        raise ValueError("verified count disagrees with source evidence")
    if summary.get("five_star_open") != sum(
        r["control_status"] in ACTIVE and r["severity_stars"] == 5
        for r in rows
    ):
        raise ValueError("five-star open count disagrees with source evidence")
    return rows


def effective_control_status(record: dict[str, Any]) -> str:
    """Source-declared PASS is never an independently authenticated completion.

    No GitHub API-backed, exact-head review/run attestation is provided by this
    offline candidate projector. Fail closed even for source statuses marked
    VERIFIED/CONTROLLED. The producer must not grant global acceptance credit.
    """
    if record["control_status"] in COMPLETE:
        return "VERIFICATION_PENDING"
    return str(record["control_status"])


def load_canonical_source(selected_path: Path) -> tuple[dict[str, Any], bytes]:
    """Reject alternate source paths: published attribution is canonical only."""
    if selected_path.resolve(strict=True) != SOURCE.resolve(strict=True):
        raise ValueError("noncanonical --source is forbidden for provenance output")
    source_bytes = SOURCE.read_bytes()
    return yaml.safe_load(source_bytes), source_bytes


def make_rollup(data: dict[str, Any], source_bytes: bytes) -> dict[str, Any]:
    """Project source-bound REX records, never assert runtime/main freshness."""
    rows = validate(data)
    # Callers cannot supply altered in-memory bytes while attributing the report
    # to the governed canonical path. Validate before this check so malformed
    # candidate records still produce precise schema diagnostics in tests.
    if source_bytes != SOURCE.read_bytes() or yaml.safe_load(source_bytes) != data:
        raise ValueError("projection data/bytes do not match canonical governed source")
    normalized = []
    frequency_units: Counter[str] = Counter()
    status_count: Counter[str] = Counter()
    for record in rows:
        unit = str(record["frequency"]["unit"])
        frequency_units[unit] += record["frequency"]["observed_count"]
        claimed_state = record["control_status"]
        state = effective_control_status(record)
        status_count[state] += 1
        proof = record["verification"]
        normalized.append({
            "rex_id": record["rex_id"],
            "signature": record["signature"],
            "severity_stars": record["severity_stars"],
            "priority_score": record["severity_stars"] * SEVERITY_WEIGHT
                + STATUS_WEIGHT[state],
            "priority_basis": "severity_plus_active_status_not_empirical_risk",
            "control_status": state,
            "source_claimed_control_status": claimed_state,
            "proof_authentication": (
                "WITHHELD_NO_INDEPENDENT_CURRENT_HEAD_RUN_OR_REVIEW_RECEIPT"
                if claimed_state in COMPLETE else "SOURCE_OBSERVATION_NOT_ADMISSION"
            ),
            "family": record["family"],
            "recurrence": record["recurrence"],
            "issue_kind": record["issue_kind"],
            "frequency": {
                "count": record["frequency"]["observed_count"],
                "unit": unit,
                "window": record["frequency"]["measurement_window"],
            },
            "lesson": record["lesson"],
            "repair_method": record["repair_method"],
            "evidence_url": proof["source_url"],
            "verification_result": (
                "WITHHELD_SOURCE_DECLARED_PASS_NOT_AUTHENTICATED"
                if claimed_state in COMPLETE else proof["result"]
            ),
            "source_claimed_result": proof["result"],
            "next_action": (
                "Revalidate/repair active root using source evidence"
                if state in ACTIVE else
                "Independently prove repair and consumer acceptance"
                if state == "REPAIRED" else
                "Authenticate terminal exact-head run and independent review before credit"
                if state == "VERIFICATION_PENDING" else
                "Retain guard and reopen only on measured regression"
            ),
        })
    normalized.sort(key=lambda r: (
        -r["priority_score"], r["rex_id"]
    ))
    for index, record in enumerate(normalized, start=1):
        record["rank"] = index
    top = {
        str(n): {
            "capacity": n,
            "populated": min(n, len(normalized)),
            "unfilled_slots": max(0, n - len(normalized)),
            "scope": "observed_candidate_rex_signatures_only",
            "records": [r["rex_id"] for r in normalized[:n]],
        }
        for n in (7, 14, 21)
    }
    source = data["repo_state"]
    return {
        "schema": SCHEMA,
        "evidence_state": "CANDIDATE_NOT_ADMITTED",
        "measurement_window": data["measurement_window"],
        "source": {
            "repo": data["repo"],
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "main_sha": source["main_sha"],
            "pr1876_head_sha": source["head_sha"],
            "pr1858_head_sha": source["companion_p0_head_sha"],
            "p0_issue_url": source["code_purple_governance_issue"],
            "proof_reuse_issue_url": source["local_incremental_ci_issue"],
            "merge_status": source["current_merge"],
            "security_review_status": source["security_review_admission"],
        },
        "metrics": {
            "candidate_rex_signatures": len(normalized),
            "candidate_rex_control_status": dict(sorted(status_count.items())),
            "open_or_deferred_candidate_signatures": sum(
                r["control_status"] in ACTIVE for r in rows
            ),
            "repaired_not_yet_verified": status_count["REPAIRED"],
            "verified_or_controlled_candidate_signatures": sum(
                r["control_status"] in COMPLETE for r in normalized
            ),
            "source_declared_verified_or_controlled_signatures": sum(
                r["control_status"] in COMPLETE for r in rows
            ),
            "verification_pending_candidate_signatures": status_count[
                "VERIFICATION_PENDING"
            ],
            "verification_credit_state": "WITHHELD_EXTERNAL_AUTHENTICATION_REQUIRED",
            "frequency_by_incompatible_unit": dict(sorted(frequency_units.items())),
            "frequency_total": None,
            "frequency_total_state": "WITHHELD_HETEROGENEOUS_UNITS",
            "actual_root_cause_queue_open": None,
            "actual_root_cause_queue_closed": None,
            "bd_queue_open": None,
            "bd_queue_closed": None,
            "authenticated_crew_launches": None,
            "current_main_coverage_pct": None,
            "current_pr_broad_coverage_pct": None,
            "current_diff_coverage_pct": None,
            "current_ci_runner_minutes": None,
            "reused_runner_minutes": None,
            "measured_pca_score": None,
            "missing_value_state": "UNKNOWN_NOT_ZERO",
        },
        "historical_coverage_baselines": {
            "main_2026_10_11": {"value_pct": 36.85, "scope": "ABACUS_MAIN_HISTORICAL"},
            "pr_broad_2026_10_12": {"value_pct": 36.92, "scope": "PR_SIDE_HISTORICAL"},
            "pr_diff_2026_10_12": {"value_pct": 51.0, "scope": "PR_SIDE_HISTORICAL"},
            "comparable_current_delta": None,
            "measurement_state": "HISTORICAL_BASELINES_NOT_CURRENT_SAMPLE",
        },
        "top7_14_21": top,
        "ranked_rex_candidates": normalized,
        "consumer_routes": data["return_contract"]["pay_it_forward"],
        "admission": {
            "glob_rex_promotion": "PENDING_INDEPENDENT_REVIEW",
            "qps_consumer_acceptance": "PENDING_INDEPENDENT_REVIEW",
            "missioncontrol_dispatch": "NOT_PROVEN",
            "authority_transfer": False,
            "security_waiver": False,
            "formal_credit_delta": 0,
            "engineering_credit_delta": 0,
        },
        "telemetry_hooks": {
            "dmaic_control": "metrics",
            "missioncontrol_rex": "ranked_rex_candidates",
            "top7_14_21": "top7_14_21",
            "ldab": "ranked_rex_candidates.family",
            "bd_queue": "metrics.bd_queue_open",
            "pca": "metrics.measured_pca_score",
            "pca_state": "WITHHELD_UNTIL_COMPARABLE_NUMERIC_POPULATION",
            "read_only": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data, source_bytes = load_canonical_source(args.source)
    result = make_rollup(data, source_bytes)
    text = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("CODE PURPLE REX roll-up is stale or absent")
        print("CODE PURPLE REX roll-up deterministic and source-bound")
        return
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"CODE PURPLE candidate REX roll-up: {len(result['ranked_rex_candidates'])} records")


if __name__ == "__main__":
    main()
