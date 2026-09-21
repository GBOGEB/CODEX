"""Typed Knowledge Exchange Bridge for governed repository federation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

PAYLOAD_VERSION = "1.0.0"
ALLOWED_OPERATIONS = {
    "glossary_alignment",
    "semantic_drift_check",
    "adr_index_exchange",
    "evidence_reference_exchange",
    "maturity_telemetry_exchange",
    "lineage_receipt",
}
FULL_EXCHANGE_OPERATIONS = {
    "adr_index_exchange",
    "evidence_reference_exchange",
    "maturity_telemetry_exchange",
}
DISPOSITIONS = {
    "ACCEPT_AS_DERIVED_EVIDENCE",
    "REJECT_WITH_REASON",
    "DEFER_PENDING_SOURCE",
    "DUPLICATE_EXISTING_WORK",
}
FINDING_TYPES = {
    "GLOSSARY_DRIFT",
    "SEMANTIC_DRIFT",
    "MISSING_TRACE",
    "CONFLICT",
    "DUPLICATE",
    "MISSING_EVIDENCE",
    "PRIORITY_SIGNAL",
    "GENERIC_IMPROVEMENT",
}


class KnowledgeExchangeError(ValueError):
    """Raised when a KEB request is invalid."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_term(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _stable_finding_id(correlation_id: str, term: str, finding_type: str) -> str:
    seed = f"{correlation_id}|{_normalize_term(term)}|{finding_type}".encode("utf-8")
    return f"KEB-{hashlib.sha256(seed).hexdigest()[:12]}"


def _load_governed_terms(glossary_path: Path) -> tuple[set[str], str, str]:
    raw = glossary_path.read_bytes()
    parsed = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(parsed, dict) or not isinstance(parsed.get("glossary"), dict):
        raise KnowledgeExchangeError("glossary source must contain a mapping at key 'glossary'")
    terms = {_normalize_term(str(key)) for key in parsed["glossary"].keys()}
    terms.discard("")
    return terms, _sha256_bytes(raw), glossary_path.as_posix()


def _require_record_array(request: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = request.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(x, dict) for x in value):
        raise KnowledgeExchangeError(f"{key} must be a non-empty object array")
    return value


def _validate_source_artifact(record: dict[str, Any], field: str) -> None:
    if not isinstance(record.get("path"), str) or not record["path"]:
        raise KnowledgeExchangeError(f"{field}.path must be a non-empty string")
    if "name" in record and (not isinstance(record["name"], str) or not record["name"]):
        raise KnowledgeExchangeError(f"{field}.name must be a non-empty string when provided")
    digest = record.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise KnowledgeExchangeError(f"{field}.sha256 must be a lowercase 64-hex digest")
    if not isinstance(record.get("authority_class"), str) or not record["authority_class"]:
        raise KnowledgeExchangeError(f"{field}.authority_class must be a non-empty string")
    if not isinstance(record.get("semantic_change"), bool):
        raise KnowledgeExchangeError(f"{field}.semantic_change must be boolean")


def _source_artifacts(request: dict[str, Any]) -> list[dict[str, Any]]:
    if "source_artifact" in request and "source_artifacts" in request:
        raise KnowledgeExchangeError("use source_artifact or source_artifacts, not both")
    if "source_artifact" in request:
        artifact = request["source_artifact"]
        if not isinstance(artifact, dict):
            raise KnowledgeExchangeError("source_artifact must be an object")
        return [artifact]
    if "source_artifacts" in request:
        artifacts = request["source_artifacts"]
        if not isinstance(artifacts, list) or not artifacts or not all(isinstance(x, dict) for x in artifacts):
            raise KnowledgeExchangeError("source_artifacts must be a non-empty object array")
        return artifacts
    return []


def _candidate_findings(request: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = request.get("candidate_findings", [])
    if not isinstance(candidates, list) or not all(isinstance(x, dict) for x in candidates):
        raise KnowledgeExchangeError("candidate_findings must be an object array")
    required = (
        "finding_type",
        "subject",
        "source_reference",
        "target_ocd_or_adr",
        "proposed_action",
        "authority_level",
    )
    for index, candidate in enumerate(candidates):
        field = f"candidate_findings[{index}]"
        finding_type = candidate.get("finding_type")
        if finding_type not in FINDING_TYPES:
            raise KnowledgeExchangeError(
                f"{field}.finding_type must be one of {', '.join(sorted(FINDING_TYPES))}"
            )
        for key in required[1:]:
            if not isinstance(candidate.get(key), str) or not candidate[key]:
                raise KnowledgeExchangeError(f"{field}.{key} must be a non-empty string")
        confidence = candidate.get("confidence", 1.0)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise KnowledgeExchangeError(f"{field}.confidence must be a number from 0 to 1")
        if candidate.get("disposition") is not None:
            raise KnowledgeExchangeError(
                f"{field}.disposition must be null; disposition remains child-owned"
            )
    return candidates


def _materialize_candidate_findings(
    request: dict[str, Any], input_hash: str
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in _candidate_findings(request):
        finding_id = _stable_finding_id(
            request["correlation_id"],
            candidate["subject"],
            candidate["finding_type"],
        )
        if finding_id in seen:
            continue
        seen.add(finding_id)
        findings.append(
            {
                "finding_id": finding_id,
                "subject": candidate["subject"],
                "source_reference": candidate["source_reference"],
                "target_ocd_or_adr": candidate["target_ocd_or_adr"],
                "finding_type": candidate["finding_type"],
                "confidence": float(candidate.get("confidence", 1.0)),
                "proposed_action": candidate["proposed_action"],
                "authority_level": candidate["authority_level"],
                "input_hash": input_hash,
                "output_hash": None,
                "disposition": None,
            }
        )
    return findings


def validate_request(request: dict[str, Any]) -> None:
    required = {
        "payload_version", "exchange_type", "correlation_id", "source",
        "operations", "terms", "authority_rule", "requested_return",
    }
    missing = sorted(required - set(request))
    if missing:
        raise KnowledgeExchangeError(f"missing required fields: {', '.join(missing)}")
    if request["payload_version"] != PAYLOAD_VERSION:
        raise KnowledgeExchangeError(f"payload_version must be {PAYLOAD_VERSION}")
    if request["exchange_type"] != "knowledge_exchange":
        raise KnowledgeExchangeError("exchange_type must be knowledge_exchange")
    if not isinstance(request["correlation_id"], str) or not request["correlation_id"]:
        raise KnowledgeExchangeError("correlation_id must be a non-empty string")

    source = request["source"]
    if not isinstance(source, dict):
        raise KnowledgeExchangeError("source must be an object")
    for key in ("repository", "ref", "sha", "run_id"):
        if not isinstance(source.get(key), str) or not source[key]:
            raise KnowledgeExchangeError(f"source.{key} must be a non-empty string")

    operations = request["operations"]
    if not isinstance(operations, list) or not operations or not all(isinstance(op, str) for op in operations):
        raise KnowledgeExchangeError("operations must be a non-empty string array")
    unknown = sorted(set(operations) - ALLOWED_OPERATIONS)
    if unknown:
        raise KnowledgeExchangeError(f"unsupported operations: {', '.join(unknown)}")

    if set(operations) & FULL_EXCHANGE_OPERATIONS:
        sha = source["sha"]
        if sha.startswith("UNKNOWN") or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise KnowledgeExchangeError("full exchange requires a concrete 40-character source.sha")

    for index, artifact in enumerate(_source_artifacts(request)):
        _validate_source_artifact(artifact, f"source_artifacts[{index}]")
    _candidate_findings(request)

    terms = request["terms"]
    if not isinstance(terms, list) or not terms or not all(isinstance(x, str) and x for x in terms):
        raise KnowledgeExchangeError("terms must be a non-empty string array")

    if "adr_index_exchange" in operations:
        for record in _require_record_array(request, "adr_index"):
            if not all(isinstance(record.get(k), str) and record[k] for k in ("id", "path", "status")):
                raise KnowledgeExchangeError("each adr_index record requires id, path and status")
    if "evidence_reference_exchange" in operations:
        for record in _require_record_array(request, "evidence_references"):
            if not all(isinstance(record.get(k), str) and record[k] for k in ("id", "path", "authority")):
                raise KnowledgeExchangeError("each evidence reference requires id, path and authority")
    if "maturity_telemetry_exchange" in operations:
        telemetry = request.get("maturity_telemetry")
        if not isinstance(telemetry, dict) or not telemetry:
            raise KnowledgeExchangeError("maturity_telemetry must be a non-empty object")

    requested = request["requested_return"]
    if not isinstance(requested, dict):
        raise KnowledgeExchangeError("requested_return must be an object")
    if requested.get("disposition_owner") == "GBOGEB/CODEX":
        raise KnowledgeExchangeError("disposition must remain child-owned")


def run_exchange(request_path: Path, glossary_path: Path, output_path: Path) -> dict[str, Any]:
    raw_request = request_path.read_bytes()
    request = json.loads(raw_request.decode("utf-8"))
    validate_request(request)

    governed_terms, glossary_hash, glossary_ref = _load_governed_terms(glossary_path)
    input_hash = _sha256_bytes(raw_request)
    findings = _materialize_candidate_findings(request, input_hash)
    finding_ids = {finding["finding_id"] for finding in findings}
    exchanged: dict[str, Any] = {}
    source_artifacts = _source_artifacts(request)
    stages: list[dict[str, Any]] = [{"stage": "request_validation", "operation": None, "status": "PASS"}]
    if "candidate_findings" in request:
        stages.append(
            {
                "stage": "candidate_findings_validation",
                "operation": None,
                "status": "PASS",
                "records": len(request["candidate_findings"]),
                "unique_findings": len(findings),
            }
        )

    for operation in request["operations"]:
        if operation == "glossary_alignment":
            before = len(findings)
            for term in request["terms"]:
                if _normalize_term(term) not in governed_terms:
                    finding_type = "GLOSSARY_DRIFT"
                    finding_id = _stable_finding_id(
                        request["correlation_id"], term, finding_type
                    )
                    if finding_id not in finding_ids:
                        findings.append({
                            "finding_id": finding_id,
                            "subject": term,
                            "source_reference": f"GBOGEB/CODEX/{glossary_ref}@sha256:{glossary_hash[:16]}",
                            "target_ocd_or_adr": "QPS_DOW_KEB_EXECUTION_ARCHITECTURE_SSOT_v0.1",
                            "finding_type": finding_type,
                            "confidence": 1.0,
                            "proposed_action": f"Define or cross-reference governed term '{term}' in the parent glossary if intended as reusable federation vocabulary.",
                            "authority_level": "GOVERNANCE",
                            "input_hash": input_hash,
                            "output_hash": None,
                            "disposition": None,
                        })
                        finding_ids.add(finding_id)
            stages.append({"stage": operation, "operation": operation, "status": "PASS", "terms_checked": len(request["terms"]), "findings": len(findings) - before})
        elif operation == "semantic_drift_check":
            missing = [term for term in request["terms"] if _normalize_term(term) not in governed_terms]
            stages.append({"stage": operation, "operation": operation, "status": "PASS", "scope": "governed_vocabulary_identity", "drift_terms": len(missing)})
        elif operation == "adr_index_exchange":
            exchanged["adr_index"] = request["adr_index"]
            stages.append({"stage": operation, "operation": operation, "status": "PASS", "records": len(request["adr_index"])})
        elif operation == "evidence_reference_exchange":
            exchanged["evidence_references"] = request["evidence_references"]
            stages.append({"stage": operation, "operation": operation, "status": "PASS", "records": len(request["evidence_references"])})
        elif operation == "maturity_telemetry_exchange":
            exchanged["maturity_telemetry"] = request["maturity_telemetry"]
            stages.append({"stage": operation, "operation": operation, "status": "PASS", "metrics": len(request["maturity_telemetry"])})
        elif operation == "lineage_receipt":
            stages.append({
                "stage": operation,
                "operation": operation,
                "status": "PASS",
                "source": glossary_ref,
                "source_sha256": glossary_hash,
                "child_source_sha": request["source"]["sha"],
                "source_artifacts": source_artifacts,
            })

    receipt: dict[str, Any] = {
        "schema": "codex-keb-exchange-receipt/v1",
        "payload_version": PAYLOAD_VERSION,
        "exchange_type": "knowledge_exchange",
        "correlation_id": request["correlation_id"],
        "source": request["source"],
        "source_artifacts": source_artifacts,
        "requested_operations": request["operations"],
        "executed_operations": [stage["operation"] for stage in stages if stage.get("operation")],
        "stages": stages,
        "exchanged": exchanged,
        "input_sha256": input_hash,
        "glossary_source": glossary_ref,
        "glossary_sha256": glossary_hash,
        "findings": findings,
        "child_disposition_required": True,
        "allowed_child_dispositions": sorted(DISPOSITIONS),
        "authority_rule": request["authority_rule"],
    }
    if receipt["executed_operations"] != request["operations"]:
        raise KnowledgeExchangeError("not all requested operations were executed in request order")

    provisional = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    output_hash = _sha256_bytes(provisional)
    receipt["output_sha256"] = output_hash
    for finding in findings:
        finding["output_hash"] = output_hash

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a typed KEB knowledge exchange")
    parser.add_argument("--input", required=True)
    parser.add_argument("--glossary", default="PIPELINE/GLOSSARY.yaml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    receipt = run_exchange(Path(args.input), Path(args.glossary), Path(args.output))
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
