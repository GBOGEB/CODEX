import json

import pytest

from codex.bridges.knowledge_exchange import KnowledgeExchangeError, run_exchange


def _request(artifact):
    return {
        "payload_version": "1.0.0",
        "exchange_type": "knowledge_exchange",
        "correlation_id": "TEST-SOURCE-ARTIFACT",
        "source": {
            "repository": "GBOGEB/cryoplant-project",
            "ref": "main",
            "sha": "a" * 40,
            "run_id": "123",
        },
        "source_artifact": artifact,
        "operations": ["evidence_reference_exchange", "lineage_receipt"],
        "terms": ["KEB"],
        "evidence_references": [
            {"id": "E1", "path": "evidence/source.md", "authority": "SOURCE"}
        ],
        "authority_rule": "authority_transfer=false",
        "requested_return": {
            "disposition_owner": "GBOGEB/cryoplant-project",
        },
    }


def _write_inputs(tmp_path, request):
    request_path = tmp_path / "request.json"
    glossary_path = tmp_path / "glossary.yaml"
    output_path = tmp_path / "receipt.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    glossary_path.write_text("glossary:\n  KEB: Knowledge Exchange Bridge\n", encoding="utf-8")
    return request_path, glossary_path, output_path


def test_hash_only_source_refresh_is_lineage_not_finding(tmp_path):
    artifact = {
        "path": "QPS_Agenda_LKT_DOC_LKT_QA_REPAIRED.docx",
        "name": "QPS_Agenda_LKT_DOC_LKT_QA_REPAIRED.docx",
        "sha256": "b" * 64,
        "authority_class": "CANONICAL_SOURCE",
        "semantic_change": False,
    }
    request_path, glossary_path, output_path = _write_inputs(
        tmp_path, _request(artifact)
    )

    receipt = run_exchange(request_path, glossary_path, output_path)

    assert receipt["source_artifacts"] == [artifact]
    assert receipt["findings"] == []
    lineage = next(
        stage for stage in receipt["stages"] if stage["stage"] == "lineage_receipt"
    )
    assert lineage["source_artifacts"] == [artifact]
    assert receipt["child_disposition_required"] is True


def test_semantic_source_delta_is_carried_without_parent_disposition(tmp_path):
    artifact = {
        "path": "QPS_Agenda_LKT.docx",
        "sha256": "c" * 64,
        "authority_class": "CANONICAL_SOURCE",
        "semantic_change": True,
    }
    request_path, glossary_path, output_path = _write_inputs(
        tmp_path, _request(artifact)
    )

    receipt = run_exchange(request_path, glossary_path, output_path)

    assert receipt["source_artifacts"][0]["semantic_change"] is True
    assert receipt["findings"] == []
    assert receipt["child_disposition_required"] is True


def test_source_artifact_digest_fails_closed(tmp_path):
    artifact = {
        "path": "QPS_Agenda_LKT.docx",
        "sha256": "NOT-A-DIGEST",
        "authority_class": "CANONICAL_SOURCE",
        "semantic_change": False,
    }
    request_path, glossary_path, output_path = _write_inputs(
        tmp_path, _request(artifact)
    )

    with pytest.raises(KnowledgeExchangeError, match="64-hex"):
        run_exchange(request_path, glossary_path, output_path)


def test_source_artifact_forms_are_mutually_exclusive(tmp_path):
    artifact = {
        "path": "QPS_Agenda_LKT.docx",
        "sha256": "d" * 64,
        "authority_class": "CANONICAL_SOURCE",
        "semantic_change": False,
    }
    request = _request(artifact)
    request["source_artifacts"] = [artifact]
    request_path, glossary_path, output_path = _write_inputs(tmp_path, request)

    with pytest.raises(KnowledgeExchangeError, match="not both"):
        run_exchange(request_path, glossary_path, output_path)
