"""Non-admitting acceptance evidence consumer for one federation owner.

Caller supplies expected SHA-256 and exact source/head identities from its
own trusted evidence channel. Hash matching does NOT authenticate the producer.
This module cannot dispatch workers, update ledgers or approve a merge.
"""
from __future__ import annotations

import hashlib
import json
import re

CONSUMER_REPO = "GBOGEB/CODEX"
SOURCE_REPO = "GBOGEB/ABACUS"
PROJECTION_SCHEMA = "codepurple.acceptance.projection.v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


class EvidenceWithheld(ValueError):
    """Malformed, unbound, or inadmissible consumer evidence."""


def _require(condition, reason):
    if not condition:
        raise EvidenceWithheld(reason)


def consumer_receipt(
    raw_bytes,
    *,
    expected_sha256,
    expected_producer_head,
    expected_consumer_head,
):
    """Make deterministic read-only receipt; never accept a canonical claim."""
    _require(isinstance(raw_bytes, bytes), "source must be raw bytes")
    _require(isinstance(expected_sha256, str) and SHA64.fullmatch(expected_sha256),
             "trusted SHA-256 digest missing")
    _require(isinstance(expected_producer_head, str)
             and SHA40.fullmatch(expected_producer_head), "bad producer SHA")
    _require(isinstance(expected_consumer_head, str)
             and SHA40.fullmatch(expected_consumer_head), "bad consumer SHA")
    actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    _require(actual_sha256 == expected_sha256, "payload digest mismatch")
    try:
        source = json.loads(raw_bytes.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise EvidenceWithheld("invalid JSON payload") from exc
    _require(type(source) is dict, "projection must be object")
    _require(source.get("schema") == PROJECTION_SCHEMA, "schema mismatch")
    _require(source.get("admission") == "HOLD", "admission forged")
    _require(source.get("authority_transfer") is False
             and source.get("security_waiver") is False, "authority or waiver forged")
    contexts = source.get("source_contexts")
    _require(type(contexts) is dict, "missing source contexts")
    producer = contexts.get(SOURCE_REPO)
    consumer = contexts.get(CONSUMER_REPO)
    _require(type(producer) is dict and type(consumer) is dict,
             "missing federation source context")
    _require(producer.get("head_sha") == expected_producer_head,
             "stale producer head")
    _require(consumer.get("head_sha") == expected_consumer_head,
             "stale consumer context")
    _require(type(producer.get("epoch")) is int
             and producer["epoch"] >= 0, "invalid producer epoch")
    _require(type(consumer.get("epoch")) is int
             and consumer["epoch"] >= 0, "invalid consumer epoch")
    obligations = source.get("obligations")
    _require(type(obligations) is list and obligations, "missing obligations")
    _require(all(type(item) is dict
                 and item.get("admission_checked") is False
                 and item.get("human_review") is None
                 for item in obligations), "unsupported approval assertion")
    metrics = source.get("metrics")
    _require(type(metrics) is dict
             and metrics.get("admitted") == 0, "admitted count unsupported")
    _require(metrics.get("current_main_coverage") is None
             and metrics.get("current_diff_coverage") is None,
             "unsupported coverage promotion")
    return {
        "schema": "codepurple.acceptance.consumer_review.v1",
        "consumer_repository": CONSUMER_REPO,
        "source_repository": SOURCE_REPO,
        "source_payload_sha256": actual_sha256,
        "producer_source_sha": expected_producer_head,
        "consumer_context_sha": expected_consumer_head,
        "producer_epoch": producer["epoch"],
        "consumer_epoch": consumer["epoch"],
        "observed_obligations": len(obligations),
        "consumer_evidence_class": "OBSERVATION_ONLY",
        "authenticated_origin_verified": False,
        "independent_review_verified": False,
        "engineering_acceptance_verified": False,
        "root_closure_credit": 0,
        "merge_admission": "HOLD",
        "authority_transfer": False,
        "security_waiver": False,
    }
