import json
from pathlib import Path

import pytest

from codex.bridges.knowledge_exchange import KnowledgeExchangeError
from codex.bridges.knowledge_exchange_return import apply_child_return


def _parent(findings=None):
    if findings is None:
        findings = [
            {"finding_id": "KEB-1"},
            {"finding_id": "KEB-2"},
            {"finding_id": "KEB-3"},
            {"finding_id": "KEB-4"},
        ]
    return {
        "schema": "codex-keb-exchange-receipt/v1",
        "correlation_id": "RET-TEST",
        "source": {"repository": "example/child"},
        "disposition_owner": "example/child",
        "output_sha256": "a" * 64,
        "findings": findings,
    }


def _child(dispositions=None):
    if dispositions is None:
        dispositions = [
            {"finding_id": "KEB-1", "disposition": "ACCEPT_AS_DERIVED_EVIDENCE", "rationale": "accepted"},
            {"finding_id": "KEB-2", "disposition": "REJECT_WITH_REASON", "rationale": "rejected"},
            {"finding_id": "KEB-3", "disposition": "DUPLICATE_EXISTING_WORK", "rationale": "duplicate"},
            {"finding_id": "KEB-4", "disposition": "DEFER_PENDING_SOURCE", "rationale": "deferred"},
        ]
    return {
        "schema": "codex-keb-child-disposition/v1",
        "correlation_id": "RET-TEST",
        "receipt_output_sha256": "a" * 64,
        "disposition_owner": "example/child",
        "dispositions": dispositions,
        "metrics": {"obligation_closures": 2, "semantic_debt_delta": -1},
    }


def _write(tmp_path: Path, parent, child, suffix=""):
    parent_path = tmp_path / f"parent{suffix}.json"
    child_path = tmp_path / f"child{suffix}.json"
    output_path = tmp_path / f"return{suffix}.json"
    parent_path.write_text(json.dumps(parent, sort_keys=True), encoding="utf-8")
    child_path.write_text(json.dumps(child, sort_keys=True), encoding="utf-8")
    return parent_path, child_path, output_path


def test_mixed_child_dispositions_emit_closure_metrics(tmp_path):
    paths = _write(tmp_path, _parent(), _child())
    receipt = apply_child_return(*paths)

    assert receipt["status"] == "PASS_DISPOSITIONED"
    assert receipt["metrics"] == {
        "findings_returned": 4,
        "dispositions_received": 4,
        "accepted": 1,
        "rejected": 1,
        "duplicate": 1,
        "deferred": 1,
        "obligation_closures": 2,
        "semantic_debt_delta": -1,
    }
    assert receipt["authority_transfer"] is False
    assert receipt["formal_credit_delta"] == 0


def test_zero_finding_return_is_complete_without_fake_dispositions(tmp_path):
    parent = _parent(findings=[])
    child = _child(dispositions=[])
    child["metrics"] = {"obligation_closures": 0, "semantic_debt_delta": 0}
    receipt = apply_child_return(*_write(tmp_path, parent, child))

    assert receipt["status"] == "PASS_NO_FINDINGS"
    assert receipt["metrics"]["findings_returned"] == 0
    assert receipt["metrics"]["dispositions_received"] == 0


def test_wrong_parent_receipt_hash_fails_closed(tmp_path):
    child = _child()
    child["receipt_output_sha256"] = "b" * 64

    with pytest.raises(KnowledgeExchangeError, match="receipt_output_sha256"):
        apply_child_return(*_write(tmp_path, _parent(), child))


def test_wrong_child_owner_fails_closed(tmp_path):
    child = _child()
    child["disposition_owner"] = "example/not-owner"

    with pytest.raises(KnowledgeExchangeError, match="disposition_owner"):
        apply_child_return(*_write(tmp_path, _parent(), child))


@pytest.mark.parametrize("mutation,match", [
    ("unknown", "unknown finding_id"),
    ("duplicate", "duplicate child disposition"),
    ("missing", "missing child dispositions"),
])
def test_finding_identity_set_is_exact(tmp_path, mutation, match):
    dispositions = _child()["dispositions"]
    if mutation == "unknown":
        dispositions[0] = {**dispositions[0], "finding_id": "KEB-UNKNOWN"}
    elif mutation == "duplicate":
        dispositions[1] = {**dispositions[1], "finding_id": "KEB-1"}
    else:
        dispositions = dispositions[:-1]

    with pytest.raises(KnowledgeExchangeError, match=match):
        apply_child_return(*_write(tmp_path, _parent(), _child(dispositions)))


def test_unsupported_disposition_fails_closed(tmp_path):
    child = _child()
    child["dispositions"][0]["disposition"] = "PROMOTE_ENGINEERING"

    with pytest.raises(KnowledgeExchangeError, match="unsupported child disposition"):
        apply_child_return(*_write(tmp_path, _parent(), child))


def test_return_receipt_is_deterministic(tmp_path):
    parent = _parent()
    child = _child()
    first_paths = _write(tmp_path, parent, child, "1")
    second_paths = _write(tmp_path, parent, child, "2")

    first = apply_child_return(*first_paths)
    second = apply_child_return(*second_paths)

    assert first == second
