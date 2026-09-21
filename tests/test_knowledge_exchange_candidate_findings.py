import json
from pathlib import Path

import pytest

from codex.bridges.knowledge_exchange import FINDING_TYPES, KnowledgeExchangeError, run_exchange


def _base_request():
    return {
        "payload_version": "1.0.0",
        "exchange_type": "knowledge_exchange",
        "correlation_id": "KEB-TYPED-FINDINGS-TEST",
        "source": {
            "repository": "example/child",
            "ref": "main",
            "sha": "UNKNOWN_FIXTURE",
            "run_id": "test",
        },
        "operations": ["glossary_alignment", "semantic_drift_check", "lineage_receipt"],
        "terms": ["KEB"],
        "authority_rule": "candidate findings only; child owns disposition",
        "requested_return": {"disposition_owner": "example/child"},
    }


def _candidate(finding_type, subject=None):
    subject = subject or finding_type.lower().replace("_", " ")
    return {
        "finding_type": finding_type,
        "subject": subject,
        "source_reference": f"source/{finding_type}.yaml",
        "target_ocd_or_adr": "ADR-TEST-001",
        "confidence": 0.8,
        "proposed_action": "Review the candidate finding in the child authority.",
        "authority_level": "GOVERNANCE_CANDIDATE",
        "disposition": None,
    }


def _run(tmp_path: Path, request):
    request_path = tmp_path / "request.json"
    glossary_path = tmp_path / "glossary.yaml"
    output_path = tmp_path / "receipt.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    glossary_path.write_text("glossary:\n  KEB: Knowledge Exchange Bridge\n", encoding="utf-8")
    return run_exchange(request_path, glossary_path, output_path)


def test_all_governed_candidate_finding_types_are_supported_and_deduplicated(tmp_path):
    request = _base_request()
    candidates = [_candidate(kind) for kind in sorted(FINDING_TYPES)]
    candidates.append(dict(candidates[0]))
    request["candidate_findings"] = candidates

    receipt = _run(tmp_path, request)

    assert len(receipt["findings"]) == len(FINDING_TYPES)
    assert {finding["finding_type"] for finding in receipt["findings"]} == FINDING_TYPES
    assert len({finding["finding_id"] for finding in receipt["findings"]}) == len(FINDING_TYPES)
    assert all(finding["disposition"] is None for finding in receipt["findings"])
    stage = next(
        stage
        for stage in receipt["stages"]
        if stage["stage"] == "candidate_findings_validation"
    )
    assert stage["records"] == len(FINDING_TYPES) + 1
    assert stage["unique_findings"] == len(FINDING_TYPES)


def test_candidate_and_generated_glossary_findings_share_semantic_identity(tmp_path):
    request = _base_request()
    request["terms"] = ["missing reusable term"]
    request["candidate_findings"] = [
        _candidate("GLOSSARY_DRIFT", subject="missing reusable term")
    ]

    receipt = _run(tmp_path, request)

    matching = [
        finding
        for finding in receipt["findings"]
        if finding["finding_type"] == "GLOSSARY_DRIFT"
        and finding["subject"] == "missing reusable term"
    ]
    assert len(matching) == 1


def test_unknown_candidate_finding_type_fails_closed(tmp_path):
    request = _base_request()
    request["candidate_findings"] = [_candidate("NOT_GOVERNED")]

    with pytest.raises(KnowledgeExchangeError, match="finding_type"):
        _run(tmp_path, request)


def test_parent_cannot_prepopulate_child_disposition(tmp_path):
    request = _base_request()
    candidate = _candidate("MISSING_TRACE")
    candidate["disposition"] = "ACCEPT_AS_DERIVED_EVIDENCE"
    request["candidate_findings"] = [candidate]

    with pytest.raises(KnowledgeExchangeError, match="child-owned"):
        _run(tmp_path, request)


def test_existing_requests_remain_backward_compatible(tmp_path):
    receipt = _run(tmp_path, _base_request())

    assert receipt["findings"] == []
    assert not any(
        stage["stage"] == "candidate_findings_validation"
        for stage in receipt["stages"]
    )
