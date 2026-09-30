#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
REQUEST_SCHEMA = MC / "schemas" / "execution_request.schema.json"
RECEIPT_SCHEMA = MC / "schemas" / "execution_receipt.schema.json"
CONTRACT = MC / "execution_gateway_contract.yaml"
RECEIPT_DIR = MC / "gateway" / "receipts"

TARGET_REPOSITORY = "GBOGEB/CODEX"
TARGET_REF = "main"
ALLOWED_INTENTS = {"REFRESH_FEDERATION_HEADS"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class GatewayError(ValueError):
    pass


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GatewayError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GatewayError(f"JSON object required at {path}")
    return value


def validate_schema(payload: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    except ValidationError as exc:
        where = ".".join(str(x) for x in exc.absolute_path) or "<root>"
        raise GatewayError(f"schema validation failed at {where}: {exc.message}") from exc


def expected_idempotency_key(expected_sha: str, payload_sha256: str) -> str:
    return f"mc:{expected_sha}:{payload_sha256}"


def completed_request_exists(request_id: str) -> bool:
    if not RECEIPT_DIR.exists():
        return False
    for path in RECEIPT_DIR.glob("*.json"):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            receipt.get("request_id") == request_id
            and receipt.get("decision") in {"AUTHORIZE", "EXECUTED"}
        ):
            return True
    return False


def validate_request(
    request: dict[str, Any],
    *,
    expected_sha: str,
    actor: str,
    check_replay: bool = True,
) -> str:
    validate_schema(request, REQUEST_SCHEMA)

    if not actor.strip():
        raise GatewayError("authenticated actor is required")
    if not SHA_RE.fullmatch(expected_sha):
        raise GatewayError("expected SHA must be a 40-character lowercase SHA")

    target = request["target"]
    if target["repo"] != TARGET_REPOSITORY:
        raise GatewayError("authenticated transport is CODEX-only")
    if target["ref"] != TARGET_REF:
        raise GatewayError("authenticated transport requires ref=main")
    if target["expected_head_sha"] != expected_sha:
        raise GatewayError(
            f"stale target head: request={target['expected_head_sha']} expected={expected_sha}"
        )

    # This slice selects/proves the authenticated transport only.
    # Mutation remains disabled by the merged #848 design authority.
    if request["action_class"] != "STAGE_ONLY":
        raise GatewayError("transport proof accepts STAGE_ONLY requests only")

    intent = request["intent"]
    if intent not in ALLOWED_INTENTS:
        raise GatewayError(f"intent is not allow-listed: {intent!r}")

    expected_payload = sha256_text(intent)
    if request["payload_sha256"] != expected_payload:
        raise GatewayError("payload_sha256 must equal SHA-256(intent) in transport v0.1")

    expected_key = expected_idempotency_key(expected_sha, expected_payload)
    if request["idempotency_key"] != expected_key:
        raise GatewayError("idempotency_key does not bind exact head and payload digest")

    if request.get("changed_paths"):
        raise GatewayError("transport dry-run may not declare changed paths")

    if check_replay and completed_request_exists(request["request_id"]):
        raise GatewayError("completed request replay is forbidden")

    return intent


def build_receipt(
    *,
    request: dict[str, Any],
    actor: str,
    actor_id: str,
    expected_sha: str,
    run_id: int,
) -> dict[str, Any]:
    receipt = {
        "schema_version": "0.1",
        "request_id": request["request_id"],
        "decision": "AUTHORIZE",
        "authenticated_principal": f"github:{actor}#{actor_id or 'unknown'}",
        "authorization_policy": "mission_control/mycelium/execution_gateway_contract.yaml",
        "observed_head_sha": expected_sha,
        "after_sha": None,
        "request_sha256": sha256_text(canonical_json(request)),
        "workflow_run": run_id,
        "workflow_job": None,
        "result_summary": (
            "Authenticated workflow_dispatch transport dry-run validated. "
            "No mutation transport is enabled in this slice."
        ),
        "evidence_refs": sorted(
            set(
                list(request.get("evidence_refs", []))
                + [
                    "mission_control/mycelium/execution_gateway_contract.yaml",
                    "mission_control/mycelium/schemas/execution_request.schema.json",
                    "mission_control/mycelium/schemas/execution_receipt.schema.json",
                ]
            )
        ),
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    validate_schema(receipt, RECEIPT_SCHEMA)
    return receipt


def write_receipt(receipt: dict[str, Any], *, run_id: int, run_attempt: int) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    request_digest = sha256_text(str(receipt["request_id"]))[:16]
    path = RECEIPT_DIR / f"transport-{request_digest}-{run_id}-{run_attempt}.json"
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--actor-id", default="")
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-attempt", type=int, default=1)
    args = parser.parse_args()

    request = load_json(args.request)
    intent = validate_request(
        request,
        expected_sha=args.expected_sha,
        actor=args.actor,
    )
    receipt = build_receipt(
        request=request,
        actor=args.actor,
        actor_id=args.actor_id,
        expected_sha=args.expected_sha,
        run_id=args.run_id,
    )
    path = write_receipt(
        receipt,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
    )
    rel = path.relative_to(ROOT).as_posix()

    print(
        json.dumps(
            {
                "gateway_transport": "PASS",
                "intent": intent,
                "decision": receipt["decision"],
                "mutation_enabled": False,
                "receipt": rel,
            },
            sort_keys=True,
        )
    )

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"receipt_path={rel}\n")
            handle.write(f"intent={intent}\n")


if __name__ == "__main__":
    try:
        main()
    except GatewayError as exc:
        print(f"GATEWAY_TRANSPORT_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(2)
