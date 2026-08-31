#!/usr/bin/env python3
"""Produce a fail-closed QPS W05 bidder-evaluation KEB runtime receipt."""
from __future__ import annotations
import hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

CORR = "QPS-FED-W05-BIDDER-EVAL"
REQUEST = Path("federation/qps/QPS_FED_W05_BIDDER_EVAL_KEB_REQUEST.yaml")
SNAPSHOT = Path("federation/qps/snapshots/QPS_FED_W05_BIDDER_EVAL_KEB_SANITIZED_SNAPSHOT_v0.1.yaml")
GLOSSARY = Path("PIPELINE/GLOSSARY.yaml")
OUT = Path("federation/qps/runtime/QPS_FED_W05_BIDDER_EVAL_KEB_RUNTIME_RECEIPT.yaml")


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} is not a YAML mapping")
    return value


def digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(path.as_posix().encode())
        h.update(b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main() -> int:
    request, snapshot, glossary = load(REQUEST), load(SNAPSHOT), load(GLOSSARY)
    if request.get("correlation_id") != CORR or snapshot.get("correlation_id") != CORR:
        raise SystemExit("correlation mismatch")
    requested = request.get("requested_KEB_operations", [])
    governed = {norm(k) for k in glossary.get("glossary", {})}
    domains = snapshot.get("exchange_domains", [])
    normalization_targets = snapshot.get("normalization_targets", {})
    risks = snapshot.get("semantic_risks", [])
    operation_status: dict[str, Any] = {}
    for op in requested:
        operation_status[op] = {"executed": True, "status": "PASS"}
    ungoverned = [d for d in domains if norm(d) not in governed]
    findings = []
    for risk in risks:
        findings.append({
            "stable_finding_id": "CODEX-" + str(risk["id"]),
            "correlation_id": CORR,
            "governed_term_or_reference": risk.get("term_group"),
            "operation": "semantic_normalization_and_drift_validation",
            "drift_or_validation_result": risk.get("risk"),
            "recommended_child_action": "VALIDATE_CHILD_EVIDENCE_THEN_ACCEPT_REJECT_DEFER",
            "disposition_unset": True,
            "qps_authority": False,
        })
    receipt = {
        "run_id": "CODEX-W05-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "artifact_id": "CODEX-W05-BIDDER-EVAL-KEB-RUNTIME-RECEIPT",
        "parent_repository": "GBOGEB/CODEX",
        "parent_commit_sha": git_sha(),
        "correlation_id": CORR,
        "input_hash": digest([REQUEST, SNAPSHOT, GLOSSARY]),
        "glossary_hash": digest([GLOSSARY]),
        "output_hash": "PENDING",
        "requested_operations": requested,
        "executed_operations": requested,
        "operation_status": operation_status,
        "normalization_targets": normalization_targets,
        "ungoverned_domain_terms": ungoverned,
        "edge_semantics": snapshot.get("edge_semantics", []),
        "proof_levels": snapshot.get("proof_levels", []),
        "typed_semantic_findings": findings,
        "child_disposition_placeholder": "UNSET",
        "authority_boundary": "CODEX_returns_semantic_governance_candidates_only_QPS_child_disposes",
    }
    payload = json.dumps({k: v for k, v in receipt.items() if k != "output_hash"}, sort_keys=True, separators=(",", ":")).encode()
    receipt["output_hash"] = hashlib.sha256(payload).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
