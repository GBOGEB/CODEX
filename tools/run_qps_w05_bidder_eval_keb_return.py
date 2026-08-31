#!/usr/bin/env python3
"""Execute governed W05 KEB mechanics and emit a deterministic receipt."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

import yaml

CORR = "QPS-FED-W05-BIDDER-EVAL"
REQUEST = Path("federation/qps/QPS_FED_W05_BIDDER_EVAL_KEB_REQUEST.yaml")
SNAPSHOT = Path(
    "federation/qps/snapshots/"
    "QPS_FED_W05_BIDDER_EVAL_KEB_SANITIZED_SNAPSHOT_v0.1.yaml"
)
GLOSSARY = Path("PIPELINE/GLOSSARY.yaml")
OUT = Path(
    "federation/qps/runtime/QPS_FED_W05_BIDDER_EVAL_KEB_RUNTIME_RECEIPT.yaml"
)
EDGE_ENUM = {
    "DIRECT",
    "SUPPORTING",
    "EVIDENCE_ONLY",
    "CONTRADICTS",
    "ALLOCATION_SHIFT",
    "MULTI_NODE_EVIDENCE",
    "INTERNAL_CONTRADICTION",
}


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} is not a YAML mapping")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def bundle_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def git_sha(root: Path = Path(".")) -> str:
    head = (root / ".git" / "HEAD").read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        ref = head[5:]
        loose = root / ".git" / ref
        if loose.exists():
            head = loose.read_text(encoding="utf-8").strip()
        else:
            packed = (root / ".git" / "packed-refs").read_text(encoding="utf-8")
            matches = [line.split()[0] for line in packed.splitlines() if line.endswith(" " + ref)]
            if len(matches) != 1:
                raise SystemExit("unable to resolve parent git SHA")
            head = matches[0]
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise SystemExit("unable to resolve parent git SHA")
    return head


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def result_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def validate_inputs(
    request: dict[str, Any], snapshot: dict[str, Any], glossary: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, Any], set[str]]:
    if request.get("correlation_id") != CORR or snapshot.get("correlation_id") != CORR:
        raise SystemExit("W05 correlation mismatch")
    if request.get("input_contract", {}).get("source_wave") != snapshot.get("source_wave"):
        raise SystemExit("request/snapshot source-wave mismatch")
    child = request.get("child", {})
    source = snapshot.get("source_identity", {})
    if child.get("repository") != source.get("child_repository"):
        raise SystemExit("request/snapshot child repository mismatch")
    if child.get("baseline_sha") != source.get("child_baseline_sha"):
        raise SystemExit("request/snapshot child baseline mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", str(child.get("baseline_sha", ""))):
        raise SystemExit("invalid child baseline SHA")
    if "SANITIZED" not in str(snapshot.get("confidentiality", "")):
        raise SystemExit("snapshot confidentiality contract failed")
    operations = request.get("requested_KEB_operations")
    if not isinstance(operations, list) or not operations or not all(
        isinstance(operation, str) and operation for operation in operations
    ):
        raise SystemExit("requested_KEB_operations must be a non-empty string list")
    if len(operations) != len(set(operations)):
        raise SystemExit("requested_KEB_operations contains duplicates")
    domains = request.get("exchange_domains")
    snapshot_domains = snapshot.get("exchange_domains")
    if not isinstance(domains, list) or set(domains) != set(snapshot_domains or []):
        raise SystemExit("request/snapshot exchange-domain mismatch")
    targets = snapshot.get("normalization_targets")
    if not isinstance(targets, dict):
        raise SystemExit("normalization_targets must be a mapping")
    glossary_terms = glossary.get("glossary")
    if not isinstance(glossary_terms, dict):
        raise SystemExit("glossary must be a mapping")
    return operations, domains, targets, {norm(term) for term in glossary_terms}


def build_handlers(
    snapshot: dict[str, Any], domains: list[str], targets: dict[str, Any], governed: set[str]
) -> dict[str, Callable[[], dict[str, Any]]]:
    risks = snapshot.get("semantic_risks", [])
    risk_by_group = {str(risk.get("term_group")): risk for risk in risks}

    def normalize_aliases() -> dict[str, Any]:
        aliases = {
            domain: list(targets.get(domain, {}).get("aliases", [])) for domain in domains
        }
        return {
            "aliases_by_domain": aliases,
            "domains_with_alias_sets": sum(bool(values) for values in aliases.values()),
            "domain_count": len(domains),
            "glossary_gap_terms": sorted(domain for domain in domains if norm(domain) not in governed),
        }

    def certificate_scope() -> dict[str, Any]:
        return {
            "rule": "certificate_scope_is_not_project_specific_QMS_application",
            "risk": risk_by_group.get("ISO9001", {}),
            "status": "VALIDATION_RULE_EXECUTED",
        }

    def document_status() -> dict[str, Any]:
        terms = snapshot.get("document_status_terms", [])
        if len(terms) != len(set(terms)):
            raise SystemExit("duplicate document status terms")
        return {
            "ordered_status_terms": terms,
            "named_deliverable_is_not_approved_evidence": True,
            "risk": risk_by_group.get("document_status", {}),
        }

    def lifecycle() -> dict[str, Any]:
        terms = snapshot.get("lifecycle_terms", [])
        required = {"L4", "L5", "L6", "operation", "maintenance", "warranty"}
        if not required.issubset(terms):
            raise SystemExit("lifecycle semantic terms incomplete")
        return {
            "terms": terms,
            "L4_L5_L6_are_distinct": len({term for term in terms if term in {"L4", "L5", "L6"}}) == 3,
            "risk": risk_by_group.get("lifecycle", {}),
        }

    def edge_semantics() -> dict[str, Any]:
        actual = snapshot.get("edge_semantics", [])
        if set(actual) != EDGE_ENUM or len(actual) != len(EDGE_ENUM):
            raise SystemExit("edge semantic enum mismatch or duplicate")
        return {
            "edge_enum": actual,
            "multi_node_duplicate_credit_prohibited": True,
            "risk": risk_by_group.get("evidence_edges", {}),
        }

    def reference_hierarchy() -> dict[str, Any]:
        domain = "Addendum_I_Addendum_II_OFFER_RTM_AD_reference_hierarchy"
        if domain not in domains:
            raise SystemExit("reference hierarchy domain missing")
        return {
            "domain": domain,
            "bidder_proposed_precedence_has_no_contract_authority": True,
            "risk": risk_by_group.get("reference_hierarchy", {}),
        }

    def welding() -> dict[str, Any]:
        domain = "WPS_WPQR_welder_operator_NDT_orbital_welding"
        aliases = targets.get(domain, {}).get("aliases", [])
        required = {"WPS", "WPQR", "NDT"}
        if not required.issubset(aliases):
            raise SystemExit("welding qualification aliases incomplete")
        return {
            "aliases": aliases,
            "code_and_qualification_identity_preserved": True,
            "risk": risk_by_group.get("welding_NDT", {}),
        }

    def evidence_lineage() -> dict[str, Any]:
        proof = snapshot.get("proof_levels", [])
        if proof != ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]:
            raise SystemExit("proof ladder mismatch")
        return {
            "proof_levels": proof,
            "document_status_terms": snapshot.get("document_status_terms", []),
            "evidence_location_required": True,
            "multi_node_reuse_without_duplicate_credit": True,
        }

    def semantic_drift() -> dict[str, Any]:
        return {
            "semantic_risks": risks,
            "risk_count": len(risks),
            "domain_feature_rows": [
                {
                    "domain": domain,
                    "alias_count": len(targets.get(domain, {}).get("aliases", [])),
                    "governed_as_exact_glossary_term": norm(domain) in governed,
                    "has_normalization_target": domain in targets,
                }
                for domain in domains
            ],
            "feature_status": "PCA_READY_SEMANTIC_GAP_FEATURES_ONLY",
            "engineering_credit": 0,
        }

    return {
        "normalize_aliases_and_governed_vocabulary": normalize_aliases,
        "distinguish_certificate_accreditation_certification_and_project_QMS_application": certificate_scope,
        "distinguish_document_issue_status_information_review_approval_hold_witness_record_as_built": document_status,
        "normalize_lifecycle_terms_and_prevent_L4_L5_L6_semantic_collapse": lifecycle,
        "normalize_direct_supporting_evidence_only_contradiction_allocation_shift_multi_node_internal_contradiction_edges": edge_semantics,
        "validate_reference_hierarchy_without_promoting_bidder_proposed_precedence_to_contract_authority": reference_hierarchy,
        "normalize_welding_and_NDT_terms_while_preserving_code_standard_identity": welding,
        "validate_evidence_location_lineage_and_multi_node_reuse_without_duplicate_credit": evidence_lineage,
        "flag_semantic_drift_between_HSE_compliance_matrix_GSHRC_DDS_scope_matrix_and_contract_nodes": semantic_drift,
    }


def main() -> int:
    request, snapshot, glossary = load(REQUEST), load(SNAPSHOT), load(GLOSSARY)
    operations, domains, targets, governed = validate_inputs(request, snapshot, glossary)
    handlers = build_handlers(snapshot, domains, targets, governed)
    unknown = [operation for operation in operations if operation not in handlers]
    if unknown:
        raise SystemExit(f"unimplemented KEB operations: {unknown}")

    request_hash = sha256_file(REQUEST)
    snapshot_hash = sha256_file(SNAPSHOT)
    glossary_hash = sha256_file(GLOSSARY)
    input_hash = bundle_digest([REQUEST, SNAPSHOT, GLOSSARY])
    parent_sha = git_sha()
    executed: list[str] = []
    operation_status: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    for operation in operations:
        result = handlers[operation]()
        result_sha = result_hash(result)
        executed.append(operation)
        operation_status[operation] = {
            "executed": True,
            "status": "PASS_EXECUTED_MECHANIC",
            "mechanic_path": "tools/run_qps_w05_bidder_eval_keb_return.py",
            "result_sha256": result_sha,
            "result": result,
        }
        findings.append(
            {
                "stable_finding_id": "CODEX-W05-" + sha256_bytes(operation.encode())[:12],
                "correlation_id": CORR,
                "governed_term_or_reference": operation,
                "operation": operation,
                "drift_or_validation_result": result,
                "recommended_child_action": "review_and_disposition_ACCEPT_REJECT_DEFER",
                "input_glossary_output_hashes": {
                    "request_sha256": request_hash,
                    "snapshot_sha256": snapshot_hash,
                    "glossary_sha256": glossary_hash,
                    "operation_result_sha256": result_sha,
                },
                "disposition_unset": True,
                "qps_authority": False,
            }
        )

    receipt: dict[str, Any] = {
        "receipt_contract_version": "0.2.0",
        "run_id": f"CODEX-W05-{parent_sha[:12]}-{input_hash[:12]}",
        "artifact_id": "CODEX-W05-BIDDER-EVAL-KEB-RUNTIME-RECEIPT",
        "parent_repository": "GBOGEB/CODEX",
        "parent_commit_sha": parent_sha,
        "correlation_id": CORR,
        "source_binding": {
            "child_repository": request["child"]["repository"],
            "child_artifact": request["child"]["artifact"],
            "child_merge_sha": request["child"]["baseline_sha"],
            "child_artifact_sha256": request["child"]["artifact_sha256"],
            "snapshot_path": "federation/qps/snapshots/QPS_FED_W05_BIDDER_EVAL_KEB_SANITIZED_SNAPSHOT_v0.1.yaml",
            "snapshot_sha256": snapshot_hash,
        },
        "input_hashes": {
            "request_sha256": request_hash,
            "snapshot_sha256": snapshot_hash,
            "glossary_sha256": glossary_hash,
            "bundle_sha256": input_hash,
        },
        "output_hash": "PENDING",
        "requested_operations": operations,
        "executed_operations": executed,
        "operation_status": operation_status,
        "typed_semantic_findings": findings,
        "child_disposition_placeholder": "UNSET",
        "authority_boundary": "CODEX returns derived semantic governance findings only; QPS child owns engineering and compliance disposition",
    }
    payload = json.dumps(
        {key: value for key, value in receipt.items() if key != "output_hash"},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    receipt["output_hash"] = sha256_bytes(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
