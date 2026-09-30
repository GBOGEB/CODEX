#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
REQUEST_SCHEMA = MC / "schemas" / "execution_request.schema.json"
POLICY = MC / "bounded_apply_policy.yaml"
LEDGER = MC / "gateway" / "bounded_apply_ledger.json"


class BoundedApplyError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BoundedApplyError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BoundedApplyError(f"JSON object required at {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_schema(request: dict[str, Any]) -> None:
    schema = load_json(REQUEST_SCHEMA)
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(request)
    except ValidationError as exc:
        where = ".".join(str(x) for x in exc.absolute_path) or "<root>"
        raise BoundedApplyError(
            f"schema validation failed at {where}: {exc.message}"
        ) from exc


def governed_apply_payload(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": request["target"],
        "action_class": request["action_class"],
        "intent": request["intent"],
        "changed_paths": sorted(request.get("changed_paths", [])),
        "approval_ref": request.get("approval_ref"),
        "dry_run_receipt_ref": request.get("dry_run_receipt_ref"),
        "authority_transfer": request["authority_transfer"],
        "formal_credit_delta": request["formal_credit_delta"],
        "engineering_credit_delta": request["engineering_credit_delta"],
    }


def expected_payload_sha256(request: dict[str, Any]) -> str:
    return sha256_text(canonical_json(governed_apply_payload(request)))


def expected_idempotency_key(expected_sha: str, payload_sha256: str) -> str:
    return f"mc-apply-plan:{expected_sha}:{payload_sha256}"


def load_policy() -> dict[str, Any]:
    value = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundedApplyError("bounded apply policy must be a mapping")
    return value


def validate_bounded_apply(
    request: dict[str, Any],
    *,
    observed_head_sha: str,
    actor: str,
    policy: dict[str, Any],
    dry_run_receipt: dict[str, Any],
    completed_idempotency_keys: set[str],
) -> dict[str, Any]:
    validate_schema(request)

    if not actor.strip():
        raise BoundedApplyError("authenticated actor is required")
    if request["action_class"] != "APPLY_BOUNDED_CODEX":
        raise BoundedApplyError("bounded apply planner requires APPLY_BOUNDED_CODEX")

    target = request["target"]
    target_policy = policy.get("target", {})
    if target["repo"] != target_policy.get("repository"):
        raise BoundedApplyError("bounded apply target must be GBOGEB/CODEX")
    if target["ref"] != target_policy.get("ref"):
        raise BoundedApplyError("bounded apply target must use ref=main")
    if target["expected_head_sha"] != observed_head_sha:
        raise BoundedApplyError(
            f"stale target head: request={target['expected_head_sha']} "
            f"observed={observed_head_sha}"
        )

    if request["intent"] not in set(policy.get("allowed_intents", [])):
        raise BoundedApplyError("bounded apply intent is not allow-listed")

    changed_paths = request.get("changed_paths") or []
    if not changed_paths:
        raise BoundedApplyError("bounded apply requires at least one changed path")
    allowed_paths = set(policy.get("changed_path_allowlist", []))
    rejected = sorted(set(changed_paths) - allowed_paths)
    if rejected:
        raise BoundedApplyError(
            "changed path is outside bounded CODEX allowlist: " + ", ".join(rejected)
        )

    approval_ref = str(request.get("approval_ref") or "")
    approval_prefix = str(policy.get("approval", {}).get("accepted_ref_prefix") or "")
    if not approval_ref or not approval_prefix or not approval_ref.startswith(approval_prefix):
        raise BoundedApplyError("explicit CODEX approval_ref is required")

    receipt_ref = str(request.get("dry_run_receipt_ref") or "")
    if not receipt_ref:
        raise BoundedApplyError("exact-head dry_run_receipt_ref is required")
    required_decision = policy.get("dry_run", {}).get("required_decision")
    if dry_run_receipt.get("decision") != required_decision:
        raise BoundedApplyError("dry-run receipt is not EXECUTED")
    if dry_run_receipt.get("after_sha") is not None:
        raise BoundedApplyError("dry-run receipt must prove no mutation")
    if dry_run_receipt.get("observed_head_sha") != observed_head_sha:
        raise BoundedApplyError("dry-run receipt does not bind the requested exact head")
    if dry_run_receipt.get("authority_transfer") is not False:
        raise BoundedApplyError("dry-run receipt transferred authority")
    if dry_run_receipt.get("formal_credit_delta") != 0:
        raise BoundedApplyError("dry-run receipt changed formal credit")
    if dry_run_receipt.get("engineering_credit_delta") != 0:
        raise BoundedApplyError("dry-run receipt changed engineering credit")

    digest = expected_payload_sha256(request)
    if request["payload_sha256"] != digest:
        raise BoundedApplyError("payload_sha256 does not bind bounded apply envelope")
    key = expected_idempotency_key(observed_head_sha, digest)
    if request["idempotency_key"] != key:
        raise BoundedApplyError("idempotency_key does not bind head and bounded payload")
    if key in completed_idempotency_keys:
        raise BoundedApplyError("completed bounded apply idempotency key replay is forbidden")

    mutation_enabled = policy.get("mutation_enabled") is True
    transports = policy.get("enabled_mutation_transports", [])
    if mutation_enabled or transports:
        raise BoundedApplyError(
            "v0.1 planning slice must remain mutation-disabled before separate promotion"
        )

    return {
        "schema_version": "0.1",
        "policy_id": policy.get("policy_id"),
        "decision": "WITHHELD_MUTATION_DISABLED",
        "authenticated_principal": f"github:{actor}",
        "observed_head_sha": observed_head_sha,
        "request_id": request["request_id"],
        "request_sha256": sha256_text(canonical_json(request)),
        "payload_sha256": digest,
        "idempotency_key": key,
        "changed_paths": sorted(changed_paths),
        "approval_ref": approval_ref,
        "dry_run_receipt_ref": receipt_ref,
        "mutation_enabled": False,
        "execute_permitted": False,
        "enabled_mutation_transports": [],
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "result_summary": (
            "All bounded CODEX planning guards passed; execution remains withheld "
            "because mutation is disabled pending separate governance promotion."
        ),
    }


def load_referenced_receipt(receipt_ref: str) -> dict[str, Any]:
    path = (ROOT / receipt_ref).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BoundedApplyError("dry-run receipt path escapes repository") from exc
    receipt_root = (ROOT / "mission_control" / "mycelium" / "gateway" / "receipts").resolve()
    try:
        path.relative_to(receipt_root)
    except ValueError as exc:
        raise BoundedApplyError("dry-run receipt must live under governed receipt root") from exc
    return load_json(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--observed-head", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    request = load_json(args.request)
    policy = load_policy()
    receipt_ref = str(request.get("dry_run_receipt_ref") or "")
    receipt = load_referenced_receipt(receipt_ref)
    ledger = load_json(LEDGER)
    completed = set(ledger.get("completed_idempotency_keys", []))
    plan = validate_bounded_apply(
        request,
        observed_head_sha=args.observed_head,
        actor=args.actor,
        policy=policy,
        dry_run_receipt=receipt,
        completed_idempotency_keys=completed,
    )
    args.out.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(plan, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BoundedApplyError as exc:
        raise SystemExit(f"BOUNDED_APPLY_WITHHELD: {exc}")
